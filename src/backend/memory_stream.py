
from datetime import datetime
import uuid
import numpy as np
import json
from typing import Dict, List, Any, Optional, Tuple, Union
import os
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import math

class MemoryStream:
    """
    Central memory repository for the agent, storing different types of memory pieces
    with retrieval capabilities based on importance, relevance, and recency.
    """
    
    def __init__(self, embedding_model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize a new MemoryStream.
        
        Args:
            embedding_model_name: Name of the sentence transformer model to use for embeddings
        """
        self.memories = []
        self.model = SentenceTransformer(embedding_model_name)
        
    def add_memory(self, 
                  memory_type: str,
                  content: str,
                  source_module: str,
                  importance_score: Optional[float] = None,
                  related_ids: Optional[List[str]] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a new memory to the stream.
        
        Args:
            memory_type: Type of memory (observation, action_taken, plan_step, reflection, wonder, etc.)
            content: The natural language content of the memory
            source_module: The module that generated this memory
            importance_score: Optional score (1-10) indicating how important this memory is
            related_ids: Optional list of IDs of related memories
            metadata: Optional additional structured data
            
        Returns:
            The ID of the newly created memory
        """
        memory_id = str(uuid.uuid4())
        embedding = self.model.encode([content])[0].tolist()
        
        memory = {
            "id": memory_id,
            "type": memory_type,
            "content": content,
            "timestamp": datetime.now().timestamp(),
            "source_module": source_module,
            "embedding": embedding,
            "importance_score": importance_score,
            "related_ids": related_ids or [],
            "metadata": metadata or {}
        }
        
        self.memories.append(memory)
        return memory_id
    
    def retrieve_memories(self,
                         query_text: str,
                         current_time: Optional[float] = None,
                         num_memories: int = 5,
                         weights: Dict[str, Union[float, Dict[str, float]]] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories based on a weighted combination of importance, relevance, and recency.
        
        Args:
            query_text: The text to search for relevant memories
            current_time: Current timestamp (defaults to now)
            num_memories: Maximum number of memories to retrieve
            weights: Dictionary with weight factors for each component
                {
                    'importance': float,
                    'relevance': float,
                    'recency': float,
                    'type_weights': {
                        'observation': float,
                        'action_taken': float,
                        ...
                    }
                }
                
        Returns:
            List of memories ordered by relevance score
        """
        if not self.memories:
            return []
        
        if current_time is None:
            current_time = datetime.now().timestamp()
            
        # Default weights if not provided
        if weights is None:
            weights = {
                'importance': 0.3,
                'relevance': 0.4,
                'recency': 0.3,
                'type_weights': {
                    'observation': 1.0,
                    'action_taken': 1.0,
                    'plan_step': 1.0,
                    'reflection': 1.0,
                    'wonder': 0.7,
                    'persona_detail': 1.2,
                    'intent': 1.5
                }
            }
        
        # Generate embedding for query
        query_embedding = self.model.encode([query_text])[0]
        
        # Calculate scores for each memory
        scored_memories = []
        for memory in self.memories:
            # Calculate relevance score (cosine similarity)
            relevance_score = float(cosine_similarity([query_embedding], [memory['embedding']])[0][0])
            
            # Calculate recency score
            time_diff = current_time - memory['timestamp']
            recency_score = 1.0 / math.exp(1 * max(0, time_diff / 3600))  # k=1, convert to hours
            
            # Get importance score (default to 5.0 if not set)
            importance_score = memory.get('importance_score', 5.0)
            
            # Get memory type weight (default to 1.0)
            memory_type = memory['type']
            type_weight = weights['type_weights'].get(memory_type, 1.0)
            
            # Calculate final score
            final_score = (
                (importance_score / 10.0) * weights['importance'] + 
                relevance_score * weights['relevance'] + 
                recency_score * weights['recency']
            ) * type_weight
            
            scored_memories.append((final_score, memory))
        
        # Sort by score (descending) and return top memories
        scored_memories.sort(reverse=True)
        return [memory for _, memory in scored_memories[:num_memories]]
    
    def get_all_memories(self) -> List[Dict[str, Any]]:
        """Get all memories in the stream."""
        return self.memories
    
    def get_memories_by_type(self, memory_type: str) -> List[Dict[str, Any]]:
        """Get all memories of a specific type."""
        return [m for m in self.memories if m['type'] == memory_type]
    
    def get_recent_memories(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent memories."""
        sorted_memories = sorted(self.memories, key=lambda m: m['timestamp'], reverse=True)
        return sorted_memories[:count]
    
    def save_to_file(self, filepath: str) -> None:
        """Save the memory stream to a JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.memories, f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str, embedding_model_name: str = "all-MiniLM-L6-v2") -> 'MemoryStream':
        """Load a memory stream from a JSON file."""
        instance = cls(embedding_model_name)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                instance.memories = json.load(f)
        return instance
