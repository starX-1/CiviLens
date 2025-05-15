import json
import redis
import hashlib
from typing import Dict, Any, Optional
from core.config import settings

class CacheService:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
        self.expiry = settings.CACHE_EXPIRY
    
    def _generate_cache_key(self, query: str, detail_level: str) -> str:
        """Generate a unique cache key based on the query and detail level"""
        key_data = f"{query.lower().strip()}:{detail_level}"
        return f"civiclens:query:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    async def get_cached_response(self, query: str, detail_level: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a cached response for a query if available
        
        Args:
            query: The user's political question
            detail_level: 'simplified', 'balanced', or 'detailed'
            
        Returns:
            Cached response dictionary or None if not found
        """
        cache_key = self._generate_cache_key(query, detail_level)
        cached_data = self.redis_client.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        return None
    
    async def cache_response(self, query: str, detail_level: str, response: Dict[str, Any]) -> None:
        """
        Cache a response for future use
        
        Args:
            query: The user's political question
            detail_level: 'simplified', 'balanced', or 'detailed'
            response: The structured response to cache
        """
        cache_key = self._generate_cache_key(query, detail_level)
        self.redis_client.setex(
            cache_key,
            self.expiry,
            json.dumps(response)
        )

cache_service = CacheService()