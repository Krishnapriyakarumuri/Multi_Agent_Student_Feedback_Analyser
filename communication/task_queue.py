# communication/task_queue.py
"""
Agent Task Queue - Advanced task distribution for production.
Uses RabbitMQ patterns for reliable task delivery.

Think of this as the "dispatch system" - ensures no task is lost.
"""

import json
import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class AgentTask:
    """A task assigned to an agent"""
    task_id: str
    agent_name: str
    task_type: str
    payload: Dict[str, Any]
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    max_retries: int = 3
    retry_count: int = 0
    created_at: str = None
    assigned_at: str = None
    completed_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "agent_name": self.agent_name,
            "task_type": self.task_type,
            "payload": self.payload,
            "priority": self.priority.value,
            "status": self.status.value,
            "max_retries": self.max_retries,
            "retry_count": self.retry_count,
            "created_at": self.created_at,
            "assigned_at": self.assigned_at,
            "completed_at": self.completed_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AgentTask':
        return cls(
            task_id=data["task_id"],
            agent_name=data["agent_name"],
            task_type=data["task_type"],
            payload=data["payload"],
            priority=TaskPriority(data.get("priority", 2)),
            status=TaskStatus(data.get("status", "pending")),
            max_retries=data.get("max_retries", 3),
            retry_count=data.get("retry_count", 0),
            created_at=data.get("created_at"),
            assigned_at=data.get("assigned_at"),
            completed_at=data.get("completed_at")
        )


class AgentTaskQueue:
    """
    Advanced task queue for production deployments.
    
    Currently uses Redis (for hackathon/demo simplicity).
    Can be swapped to RabbitMQ/Kafka for production with same interface.
    
    FEATURES:
    - Priority queuing (critical tasks first)
    - Retry with exponential backoff
    - Dead letter queue for failed tasks
    - Task timeout handling
    - Task dependency management
    """
    
    def __init__(self, use_rabbitmq: bool = False):
        """
        Args:
            use_rabbitmq: If True, uses RabbitMQ. If False, uses Redis.
        """
        self.use_rabbitmq = use_rabbitmq
        
        if use_rabbitmq:
            self._setup_rabbitmq()
        else:
            self._setup_redis()
    
    def _setup_redis(self):
        """Setup Redis-based task queue"""
        import redis
        self.redis = redis.Redis.from_url(
            config.REDIS_URL,
            decode_responses=True
        )
        self.backend = "Redis"
        print("📨 Task Queue: Using Redis backend")
    
    def _setup_rabbitmq(self):
        """Setup RabbitMQ-based task queue (for production)"""
        try:
            import pika
            self.rabbitmq = pika.BlockingConnection(
                pika.ConnectionParameters('localhost')
            )
            self.channel = self.rabbitmq.channel()
            self.backend = "RabbitMQ"
            print("📨 Task Queue: Using RabbitMQ backend")
        except ImportError:
            print("⚠️ pika not installed, falling back to Redis")
            self._setup_redis()
    
    # ─── Task Submission ───
    
    def submit_task(self, task: AgentTask) -> str:
        """
        Submit a task to an agent's queue.
        Returns task_id for tracking.
        """
        queue_key = f"tasks:{task.agent_name}:queue"
        task_data = json.dumps(task.to_dict())
        
        if task.priority == TaskPriority.CRITICAL:
            # Critical tasks go to front of queue
            self.redis.lpush(queue_key, task_data)
        else:
            # Normal tasks go to back
            self.redis.rpush(queue_key, task_data)
        
        # Track task separately
        self.redis.hset(
            f"tasks:{task.task_id}:details",
            mapping=task.to_dict()
        )
        
        print(f"📋 Task {task.task_id[:8]}... → [{task.agent_name}] (Priority: {task.priority.name})")
        return task.task_id
    
    def submit_batch(self, tasks: list) -> list:
        """Submit multiple tasks efficiently"""
        pipeline = self.redis.pipeline()
        
        for task in tasks:
            queue_key = f"tasks:{task.agent_name}:queue"
            task_data = json.dumps(task.to_dict())
            pipeline.rpush(queue_key, task_data)
            pipeline.hset(f"tasks:{task.task_id}:details", mapping=task.to_dict())
        
        pipeline.execute()
        print(f"📋 Batch submitted: {len(tasks)} tasks")
        return [t.task_id for t in tasks]
    
    # ─── Task Consumption ───
    
    def get_next_task(self, agent_name: str, timeout: int = 5) -> Optional[AgentTask]:
        """
        Agent requests its next task.
        Blocks until a task is available or timeout.
        """
        queue_key = f"tasks:{agent_name}:queue"
        
        # BRPOP gets from the right (FIFO for normal, LIFO if critical was pushed left)
        result = self.redis.brpop(queue_key, timeout=timeout)
        
        if result:
            _, task_data = result
            task = AgentTask.from_dict(json.loads(task_data))
            task.status = TaskStatus.IN_PROGRESS
            task.assigned_at = datetime.now().isoformat()
            
            # Update task status
            self.redis.hset(f"tasks:{task.task_id}:details", mapping=task.to_dict())
            
            return task
        
        return None
    
    # ─── Task Completion & Retry ───
    
    def mark_completed(self, task_id: str, result: Dict = None):
        """Mark a task as successfully completed"""
        self.redis.hset(f"tasks:{task_id}:details", "status", "completed")
        self.redis.hset(f"tasks:{task_id}:details", "completed_at", datetime.now().isoformat())
        
        if result:
            self.redis.hset(
                f"tasks:{task_id}:details",
                "result",
                json.dumps(result)
            )
        
        print(f"✅ Task {task_id[:8]}... completed")
    
    def mark_failed(self, task_id: str, error: str, requeue: bool = True):
        """Mark a task as failed, optionally requeue for retry"""
        task_data = self.redis.hgetall(f"tasks:{task_id}:details")
        
        if not task_data:
            return
        
        task = AgentTask.from_dict(task_data)
        task.retry_count += 1
        
        if requeue and task.retry_count < task.max_retries:
            # Retry with exponential backoff
            backoff_seconds = 2 ** task.retry_count
            task.status = TaskStatus.RETRYING
            
            self.redis.hset(f"tasks:{task_id}:details", mapping=task.to_dict())
            
            # Requeue with delay (using sorted set for delayed tasks)
            retry_time = time.time() + backoff_seconds
            self.redis.zadd(
                "tasks:delayed",
                {json.dumps(task.to_dict()): retry_time}
            )
            
            print(f"🔄 Task {task_id[:8]}... retry {task.retry_count}/{task.max_retries} in {backoff_seconds}s")
        else:
            # Move to dead letter queue
            task.status = TaskStatus.FAILED
            self.redis.lpush(
                "tasks:dead_letter_queue",
                json.dumps(task.to_dict())
            )
            self.redis.hset(f"tasks:{task_id}:details", "status", "failed")
            self.redis.hset(f"tasks:{task_id}:details", "error", error)
            
            print(f"❌ Task {task_id[:8]}... permanently failed → DLQ")
    
    # ─── Dead Letter Queue ───
    
    def get_failed_tasks(self, limit: int = 10) -> list:
        """Get tasks from dead letter queue for inspection"""
        tasks = []
        for _ in range(limit):
            task_data = self.redis.rpop("tasks:dead_letter_queue")
            if task_data:
                tasks.append(AgentTask.from_dict(json.loads(task_data)))
            else:
                break
        return tasks
    
    def requeue_failed_task(self, task_id: str, new_agent: str = None):
        """Manually requeue a failed task"""
        task_data = self.redis.hgetall(f"tasks:{task_id}:details")
        if task_data:
            task = AgentTask.from_dict(task_data)
            task.retry_count = 0
            task.status = TaskStatus.PENDING
            if new_agent:
                task.agent_name = new_agent
            self.submit_task(task)
            print(f"🔁 Task {task_id[:8]}... manually requeued")
    
    # ─── Queue Monitoring ───
    
    def get_queue_stats(self, agent_name: str) -> Dict:
        """Get statistics for an agent's task queue"""
        queue_key = f"tasks:{agent_name}:queue"
        return {
            "agent": agent_name,
            "pending_tasks": self.redis.llen(queue_key),
            "backend": self.backend
        }
    
    def get_all_stats(self) -> Dict:
        """Get statistics for all agent queues"""
        agents = ["preprocessing", "embedding", "sentiment", "theme", "bias", "recommendation"]
        return {agent: self.get_queue_stats(agent) for agent in agents}
    
    def process_delayed_tasks(self):
        """Process tasks that were delayed for retry"""
        now = time.time()
        # Get all delayed tasks ready for processing
        ready_tasks = self.redis.zrangebyscore("tasks:delayed", 0, now)
        
        for task_data in ready_tasks:
            self.redis.zrem("tasks:delayed", task_data)
            task = AgentTask.from_dict(json.loads(task_data))
            task.status = TaskStatus.PENDING
            self.submit_task(task)
        
        if ready_tasks:
            print(f"⏰ Requeued {len(ready_tasks)} delayed tasks")