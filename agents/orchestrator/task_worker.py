# agents/orchestrator/task_worker.py
"""
Background task worker that processes agent tasks from the message bus.
Continuously monitors queues and executes agents in the pipeline.
Uses threading to avoid blocking the async event loop.
"""

import asyncio
import threading
from typing import Dict, Any
from communication.memory_bus import AgentMessageBus, InMemoryMessageBus
from memory.working_memory import WorkingMemory
from memory.long_term_memory import LongTermMemory
import logging
import time
import inspect
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskWorker:
    """Background worker that processes tasks through the agent pipeline"""
    
    def __init__(self, agents: Dict[str, Any], message_bus: AgentMessageBus = None):
        """
        Initialize the task worker with registered agents
        
        Args:
            agents: Dict of {agent_name: agent_instance}
            message_bus: Optional message bus instance (if not provided, creates new)
        """
        self.agents = agents
        # Use provided message bus or create new one
        if message_bus:
            self.message_bus = message_bus
        else:
            self.message_bus = AgentMessageBus()
        self.working_memory = WorkingMemory()
        self.long_term_memory = LongTermMemory()
        self.running = False
        self.processed_count = 0
        self.worker_threads = []
        
    async def start(self):
        """Start the background task worker using threads"""
        self.running = True
        logger.info("🚀 Task Worker started (using threads to avoid blocking event loop)")
        
        # Create a thread for each agent to process their queue
        for agent_name in self.agents.keys():
            thread = threading.Thread(
                target=self._listen_and_process_agent_sync,
                args=(agent_name,),
                daemon=True
            )
            thread.start()
            self.worker_threads.append(thread)
            logger.info(f"👂 Worker thread started for {agent_name}")
        
        # Keep the async function alive while threads run
        try:
            while self.running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("Task worker cancelled")
            self.running = False
    
    async def stop(self):
        """Stop the task worker"""
        self.running = False
        logger.info("⛔ Task Worker stopped")
        
        # Wait for all threads to finish
        for thread in self.worker_threads:
            if thread.is_alive():
                thread.join(timeout=2)
    
    def _listen_and_process_agent_sync(self, agent_name: str):
        """
        Synchronous method that runs in a thread.
        Listens for messages for a specific agent and processes them.
        
        Args:
            agent_name: Name of the agent to listen for
        """
        agent = self.agents[agent_name]
        logger.info(f"👂 [{agent_name}] worker thread listening...")
        
        while self.running:
            try:
                # Non-blocking check with timeout - this is OK in a thread
                message = self.message_bus.receive_message(agent_name, timeout=2)
                
                if message:
                    logger.info(f"📨 [{agent_name}] Received task {message.task_id[:8]}...")
                    
                    # Execute the agent on this task
                    try:
                        task_data = message.payload
                        
                        # Call agent directly - agents don't use await anyway
                        # Skip asyncio.run() overhead
                        import inspect
                        if inspect.iscoroutinefunction(agent.execute):
                            # If it IS truly async, run it
                            result = asyncio.run(agent.execute(task_data))
                        else:
                            # If it's just a regular function, call it directly
                            result = agent.execute(task_data)
                        
                        # Update task progress in message bus
                        self.message_bus.update_task_progress(message.task_id, agent_name)
                        
                        # Get next agent in pipeline
                        pipeline = task_data.get("pipeline", [])
                        current_index = task_data.get("current_agent_index", 0)
                        next_index = current_index + 1
                        
                        if next_index < len(pipeline):
                            # Hand off to next agent
                            next_agent = pipeline[next_index]
                            next_task = {**task_data, **result, "current_agent_index": next_index}
                            
                            self.message_bus.handoff(
                                from_agent=agent_name,
                                to_agent=next_agent,
                                data=next_task,
                                task_id=message.task_id
                            )
                            logger.info(f"✅ [{agent_name}] → Handoff to [{next_agent}] ({self.processed_count + 1} processed)")
                        else:
                            # Pipeline complete
                            logger.info(f"🎉 [{agent_name}] Pipeline complete for {message.task_id[:8]}!")
                            
                            # Store final result in working memory
                            self.working_memory.set(f"result:{message.task_id}", result)
                            self.message_bus.update_task_progress(message.task_id, "COMPLETED")
                            
                            # CRITICAL: Save results to long-term memory (database) so UI can fetch them
                            try:
                                self._save_results_to_database(task_data, result)
                                logger.info(f"✅ Results saved to database for {message.task_id[:8]}")
                            except Exception as e:
                                logger.error(f"❌ Failed to save results to database: {str(e)}", exc_info=True)
                                logger.error("⚠️  TIP: If you see 'table has no column' error, delete the database file and restart the server")
                                # Don't crash - pipeline completed successfully even if DB save failed
                                pass
                        
                        self.processed_count += 1
                        
                    except Exception as e:
                        logger.error(f"❌ [{agent_name}] Error processing task: {str(e)}", exc_info=True)
                        self.message_bus.update_task_progress(message.task_id, f"{agent_name}_failed")
                
                # Minimal sleep - we're in a thread so it's OK
                time.sleep(0.01)  # Reduced from 0.05
                
            except Exception as e:
                logger.error(f"❌ [{agent_name}] Listener error: {str(e)}", exc_info=True)
                time.sleep(1)  # Backoff on error
    
    def _save_results_to_database(self, task_data: Dict[str, Any], result: Dict[str, Any]):
        """
        Save pipeline results to long-term memory (database).
        Uses canonical feedback_id (resolved via text_hash) so re-uploading
        the same CSV never produces duplicate records in any table.
        """
        job_id = task_data.get("job_id", "unknown")
        feedback_id = task_data.get("feedback_id", "unknown")
        
        # ── Step 1: Save Feedback ─────────────────────────────────────────────
        # save_feedback deduplicates by text_hash and returns the CANONICAL id.
        # If the same text was processed in a prior run, it returns the OLD id.
        # IMPORTANT: preprocessing fields live in task_data (accumulated pipeline
        # state), NOT in result (which is only the last agent's output).
        feedback_record = {
            "id": feedback_id,
            "job_id": job_id,
            "original_text": task_data.get("original_text", task_data.get("text", "")),
            "cleaned_text": task_data.get("cleaned_text", ""),
            "text_hash": task_data.get("text_hash", ""),  # <-- key fix: was result.get()
            "is_valid": task_data.get("is_valid", True),
            "processed_by": "preprocessing"
        }
        canonical_id = self.long_term_memory.save_feedback(feedback_record)
        
        # ── Step 2: Use canonical id for all child tables ─────────────────────
        # This ensures cross-run duplicates are caught: all child-table save_*
        # methods check for an existing row by this feedback_id and skip if found.
        if canonical_id:
            feedback_id = canonical_id
        
        # ── Step 3: Save Sentiment Analysis ───────────────────────────────────
        if "sentiment" in task_data:
            sentiment = task_data.get("sentiment", {})
            sentiment_record = {
                "id": str(uuid.uuid4()),
                "feedback_id": feedback_id,
                "label": sentiment.get("label", "neutral"),
                "score": sentiment.get("score", 0),
                "confidence": sentiment.get("confidence", "low"),
                "processed_by": "sentiment"
            }
            self.long_term_memory.save_sentiment(sentiment_record)
        
        # ── Step 4: Save Theme Assignment ─────────────────────────────────────
        if "theme" in task_data:
            theme = task_data.get("theme", {})
            theme_record = {
                "id": str(uuid.uuid4()),
                "feedback_id": feedback_id,
                "theme_id": theme.get("theme_id", theme.get("topic_id", 0)),
                "theme_name": theme.get("topic_name", theme.get("theme_name", "Unknown")),
                "keywords": theme.get("keywords", []),
                "probability": theme.get("probability", 0.0),
                "is_outlier": theme.get("is_outlier", False),
                "processed_by": "theme"
            }
            self.long_term_memory.save_theme(theme_record)
        
        # ── Step 5: Save Bias Check ───────────────────────────────────────────
        if "is_biased" in task_data:
            bias_record = {
                "id": str(uuid.uuid4()),
                "feedback_id": feedback_id,
                "is_biased": task_data.get("is_biased", False),
                "bias_type": task_data.get("bias_type", ""),
                "severity": task_data.get("severity", 0.0),
                "flagged_terms": task_data.get("detected_indicators", []),
                "explanation": task_data.get("explanation", ""),
                "requires_human_review": task_data.get("requires_human_review", False),
                "has_educational_value": task_data.get("has_educational_value", True),
                "processed_by": "bias"
            }
            self.long_term_memory.save_bias_check(bias_record)
        
        # ── Step 6: Save Recommendation ──────────────────────────────────────
        if "recommendation_text" in result or "recommendation" in result:
            recommendation_record = {
                "id": str(uuid.uuid4()),
                "feedback_id": feedback_id,
                "theme_id": result.get("theme_id", 0),
                "theme_name": result.get("theme_name", "Unknown"),
                "recommendation_text": result.get("recommendation_text", result.get("recommendation", "")),
                "priority": result.get("priority", "medium"),
                "action_items": result.get("action_items", []),
                "expected_impact": result.get("expected_impact", ""),
                "fairness_note": result.get("fairness_note", ""),
                "implemented": False,
                "upstream_agents": result.get("upstream_agents", []),
                "processed_by": "recommendation"
            }
            self.long_term_memory.save_recommendation(recommendation_record)
        
        logger.info(f"💾 Persisted all results for feedback {feedback_id} to database")
    
    def get_status(self) -> Dict[str, Any]:
        """Get worker status"""
        return {
            "running": self.running,
            "processed_tasks": self.processed_count,
            "queue_depths": {
                agent_name: self.message_bus.get_queue_depth(agent_name)
                for agent_name in self.agents.keys()
            }
        }
