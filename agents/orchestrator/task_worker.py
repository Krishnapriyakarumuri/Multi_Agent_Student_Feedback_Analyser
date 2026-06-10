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
import logging
import time
import inspect

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
                            
                            # Store final result
                            self.working_memory.set(f"result:{message.task_id}", result)
                            self.message_bus.update_task_progress(message.task_id, "COMPLETED")
                        
                        self.processed_count += 1
                        
                    except Exception as e:
                        logger.error(f"❌ [{agent_name}] Error processing task: {str(e)}", exc_info=True)
                        self.message_bus.update_task_progress(message.task_id, f"{agent_name}_failed")
                
                # Minimal sleep - we're in a thread so it's OK
                time.sleep(0.01)  # Reduced from 0.05
                
            except Exception as e:
                logger.error(f"❌ [{agent_name}] Listener error: {str(e)}", exc_info=True)
                time.sleep(1)  # Backoff on error
    
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
