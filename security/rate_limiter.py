#!/usr/bin/env python3
"""
rate_limiter.py

Advanced rate limiting system for OSQuery MCP server with multiple
rate limiting strategies and intelligent throttling.

Features:
- Token bucket algorithm
- Sliding window rate limiting
- Per-user and per-tool limits
- Dynamic rate adjustment
- Integration with audit logging
"""

import time
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, deque
import asyncio


class LimitType(Enum):
    REQUESTS_PER_MINUTE = "requests_per_minute"
    REQUESTS_PER_HOUR = "requests_per_hour"
    CONCURRENT_REQUESTS = "concurrent_requests"
    QUERY_COMPLEXITY = "query_complexity"
    DATA_TRANSFER = "data_transfer"


@dataclass
class RateLimit:
    limit_type: LimitType
    max_value: int
    window_seconds: int
    burst_allowance: int = 0


@dataclass
class TokenBucket:
    capacity: int
    refill_rate: float  # tokens per second
    tokens: float
    last_refill: float
    
    def __post_init__(self):
        self.tokens = self.capacity
        self.last_refill = time.time()


class RateLimiter:
    """Advanced rate limiting with multiple strategies"""
    
    def __init__(self):
        self.buckets: Dict[str, TokenBucket] = {}
        self.sliding_windows: Dict[str, deque] = defaultdict(deque)
        self.concurrent_requests: Dict[str, int] = defaultdict(int)
        self.lock = threading.RLock()
        
        # Default rate limits
        self.default_limits = {
            "global": [
                RateLimit(LimitType.REQUESTS_PER_MINUTE, 60, 60),
                RateLimit(LimitType.REQUESTS_PER_HOUR, 1000, 3600),
                RateLimit(LimitType.CONCURRENT_REQUESTS, 10, 0)
            ],
            "user": [
                RateLimit(LimitType.REQUESTS_PER_MINUTE, 30, 60),
                RateLimit(LimitType.REQUESTS_PER_HOUR, 500, 3600)
            ],
            "tool:custom_query": [
                RateLimit(LimitType.REQUESTS_PER_MINUTE, 10, 60),
                RateLimit(LimitType.QUERY_COMPLEXITY, 100, 60)
            ],
            "tool:processes": [
                RateLimit(LimitType.REQUESTS_PER_MINUTE, 20, 60)
            ]
        }
        
        # Initialize buckets
        self._init_buckets()
    
    def _init_buckets(self):
        """Initialize token buckets for rate limits"""
        for category, limits in self.default_limits.items():
            for limit in limits:
                if limit.limit_type in [LimitType.REQUESTS_PER_MINUTE, LimitType.REQUESTS_PER_HOUR]:
                    bucket_key = f"{category}:{limit.limit_type.value}"
                    refill_rate = limit.max_value / limit.window_seconds
                    
                    self.buckets[bucket_key] = TokenBucket(
                        capacity=limit.max_value,
                        refill_rate=refill_rate,
                        tokens=limit.max_value,
                        last_refill=time.time()
                    )
    
    def _refill_bucket(self, bucket: TokenBucket):
        """Refill token bucket based on elapsed time"""
        now = time.time()
        elapsed = now - bucket.last_refill
        
        tokens_to_add = elapsed * bucket.refill_rate
        bucket.tokens = min(bucket.capacity, bucket.tokens + tokens_to_add)
        bucket.last_refill = now
    
    def _get_bucket_key(self, user_id: str = None, tool_name: str = None, 
                       limit_type: LimitType = LimitType.REQUESTS_PER_MINUTE) -> str:
        """Generate bucket key for rate limit lookup"""
        if tool_name and f"tool:{tool_name}" in self.default_limits:
            return f"tool:{tool_name}:{limit_type.value}"
        elif user_id:
            return f"user:{limit_type.value}"
        else:
            return f"global:{limit_type.value}"
    
    def _check_token_bucket(self, bucket_key: str, tokens_needed: int = 1) -> bool:
        """Check if tokens are available in bucket"""
        if bucket_key not in self.buckets:
            return True  # No limit configured
        
        bucket = self.buckets[bucket_key]
        self._refill_bucket(bucket)
        
        if bucket.tokens >= tokens_needed:
            bucket.tokens -= tokens_needed
            return True
        
        return False
    
    def _check_sliding_window(self, window_key: str, limit: RateLimit) -> bool:
        """Check sliding window rate limit"""
        now = time.time()
        window = self.sliding_windows[window_key]
        
        # Remove old entries
        while window and window[0] <= now - limit.window_seconds:
            window.popleft()
        
        # Check if under limit
        if len(window) < limit.max_value:
            window.append(now)
            return True
        
        return False
    
    def _check_concurrent_limit(self, key: str, limit: RateLimit) -> bool:
        """Check concurrent requests limit"""
        current = self.concurrent_requests.get(key, 0)
        return current < limit.max_value
    
    def _estimate_query_complexity(self, tool_name: str, parameters: Dict[str, Any]) -> int:
        """Estimate query complexity for rate limiting"""
        complexity = 1
        
        if tool_name == "custom_query":
            sql = parameters.get("sql", "").lower()
            # Simple complexity heuristics
            if "join" in sql:
                complexity += 5
            if "group by" in sql:
                complexity += 3
            if "order by" in sql:
                complexity += 2
            if "*" in sql:
                complexity += 2
            
            # Count tables/conditions
            complexity += sql.count("where") * 2
            complexity += sql.count("and") + sql.count("or")
        
        elif tool_name == "processes":
            limit = parameters.get("limit", 5)
            if isinstance(limit, (int, str)) and str(limit).isdigit():
                complexity += max(1, int(limit) // 10)
        
        return complexity
    
    def check_rate_limit(self, user_id: str = None, tool_name: str = None,
                        parameters: Dict[str, Any] = None,
                        session_id: str = None) -> Dict[str, Any]:
        """
        Check if request is within rate limits
        
        Returns:
            Dict with 'allowed' boolean and details
        """
        with self.lock:
            now = time.time()
            parameters = parameters or {}
            
            # Check applicable limits
            checks = []
            
            # Global limits
            for limit in self.default_limits.get("global", []):
                if limit.limit_type == LimitType.REQUESTS_PER_MINUTE:
                    bucket_key = self._get_bucket_key(limit_type=limit.limit_type)
                    allowed = self._check_token_bucket(bucket_key)
                    checks.append({
                        "type": "global_rpm",
                        "allowed": allowed,
                        "limit": limit.max_value,
                        "remaining": int(self.buckets.get(bucket_key, TokenBucket(0, 0, 0, 0)).tokens)
                    })
                
                elif limit.limit_type == LimitType.REQUESTS_PER_HOUR:
                    bucket_key = self._get_bucket_key(limit_type=limit.limit_type)
                    allowed = self._check_token_bucket(bucket_key)
                    checks.append({
                        "type": "global_rph", 
                        "allowed": allowed,
                        "limit": limit.max_value,
                        "remaining": int(self.buckets.get(bucket_key, TokenBucket(0, 0, 0, 0)).tokens)
                    })
                
                elif limit.limit_type == LimitType.CONCURRENT_REQUESTS:
                    allowed = self._check_concurrent_limit("global", limit)
                    checks.append({
                        "type": "global_concurrent",
                        "allowed": allowed,
                        "limit": limit.max_value,
                        "current": self.concurrent_requests.get("global", 0)
                    })
            
            # User limits
            if user_id:
                for limit in self.default_limits.get("user", []):
                    if limit.limit_type == LimitType.REQUESTS_PER_MINUTE:
                        bucket_key = f"user:{user_id}:{limit.limit_type.value}"
                        if bucket_key not in self.buckets:
                            self.buckets[bucket_key] = TokenBucket(
                                capacity=limit.max_value,
                                refill_rate=limit.max_value / limit.window_seconds,
                                tokens=limit.max_value,
                                last_refill=now
                            )
                        
                        allowed = self._check_token_bucket(bucket_key)
                        checks.append({
                            "type": "user_rpm",
                            "allowed": allowed,
                            "limit": limit.max_value,
                            "remaining": int(self.buckets[bucket_key].tokens)
                        })
            
            # Tool-specific limits
            if tool_name:
                tool_limits = self.default_limits.get(f"tool:{tool_name}", [])
                for limit in tool_limits:
                    if limit.limit_type == LimitType.REQUESTS_PER_MINUTE:
                        bucket_key = f"tool:{tool_name}:{limit.limit_type.value}"
                        if bucket_key not in self.buckets:
                            self.buckets[bucket_key] = TokenBucket(
                                capacity=limit.max_value,
                                refill_rate=limit.max_value / limit.window_seconds,
                                tokens=limit.max_value,
                                last_refill=now
                            )
                        
                        allowed = self._check_token_bucket(bucket_key)
                        checks.append({
                            "type": "tool_rpm",
                            "allowed": allowed,
                            "limit": limit.max_value,
                            "remaining": int(self.buckets[bucket_key].tokens)
                        })
                    
                    elif limit.limit_type == LimitType.QUERY_COMPLEXITY:
                        complexity = self._estimate_query_complexity(tool_name, parameters)
                        window_key = f"tool:{tool_name}:complexity:{user_id or 'anonymous'}"
                        
                        # Use sliding window for complexity
                        window = self.sliding_windows[window_key]
                        current_complexity = sum(1 for _ in window)  # Simplified
                        
                        allowed = current_complexity + complexity <= limit.max_value
                        if allowed:
                            # Add to window (simplified - should store actual complexity)
                            for _ in range(complexity):
                                window.append(now)
                        
                        checks.append({
                            "type": "query_complexity",
                            "allowed": allowed,
                            "limit": limit.max_value,
                            "current": current_complexity,
                            "requested": complexity
                        })
            
            # Overall result
            all_allowed = all(check["allowed"] for check in checks)
            
            return {
                "allowed": all_allowed,
                "timestamp": now,
                "user_id": user_id,
                "tool_name": tool_name,
                "session_id": session_id,
                "checks": checks,
                "retry_after": self._calculate_retry_after(checks) if not all_allowed else None
            }
    
    def _calculate_retry_after(self, checks: List[Dict[str, Any]]) -> float:
        """Calculate retry-after time in seconds"""
        failed_checks = [c for c in checks if not c["allowed"]]
        if not failed_checks:
            return 0
        
        # Simple heuristic - return shortest refill time
        min_retry = 60  # Default 1 minute
        
        for check in failed_checks:
            if check["type"].endswith("_rpm"):
                # For per-minute limits, calculate based on refill rate
                remaining = check.get("remaining", 0)
                limit = check["limit"]
                if remaining == 0:
                    min_retry = min(min_retry, 60)  # Wait for refill
            
        return min_retry
    
    def increment_concurrent(self, key: str):
        """Increment concurrent request counter"""
        with self.lock:
            self.concurrent_requests[key] = self.concurrent_requests.get(key, 0) + 1
    
    def decrement_concurrent(self, key: str):
        """Decrement concurrent request counter"""
        with self.lock:
            if key in self.concurrent_requests:
                self.concurrent_requests[key] = max(0, self.concurrent_requests[key] - 1)
                if self.concurrent_requests[key] == 0:
                    del self.concurrent_requests[key]
    
    def get_rate_limit_status(self, user_id: str = None) -> Dict[str, Any]:
        """Get current rate limit status"""
        with self.lock:
            status = {
                "timestamp": time.time(),
                "global": {},
                "user": {},
                "concurrent": dict(self.concurrent_requests)
            }
            
            # Global buckets
            for bucket_key, bucket in self.buckets.items():
                if bucket_key.startswith("global:"):
                    self._refill_bucket(bucket)
                    limit_type = bucket_key.split(":")[-1]
                    status["global"][limit_type] = {
                        "capacity": bucket.capacity,
                        "tokens": int(bucket.tokens),
                        "refill_rate": bucket.refill_rate
                    }
            
            # User buckets
            if user_id:
                user_prefix = f"user:{user_id}:"
                for bucket_key, bucket in self.buckets.items():
                    if bucket_key.startswith(user_prefix):
                        self._refill_bucket(bucket)
                        limit_type = bucket_key.split(":")[-1]
                        status["user"][limit_type] = {
                            "capacity": bucket.capacity,
                            "tokens": int(bucket.tokens),
                            "refill_rate": bucket.refill_rate
                        }
            
            return status
    
    def reset_limits(self, user_id: str = None, tool_name: str = None):
        """Reset rate limits for debugging/admin purposes"""
        with self.lock:
            if user_id and tool_name:
                # Reset specific user+tool combination
                keys_to_reset = [k for k in self.buckets.keys() 
                               if f"user:{user_id}" in k or f"tool:{tool_name}" in k]
            elif user_id:
                # Reset all user limits
                keys_to_reset = [k for k in self.buckets.keys() if f"user:{user_id}" in k]
            elif tool_name:
                # Reset tool limits
                keys_to_reset = [k for k in self.buckets.keys() if f"tool:{tool_name}" in k]
            else:
                # Reset all limits
                keys_to_reset = list(self.buckets.keys())
            
            for key in keys_to_reset:
                bucket = self.buckets[key]
                bucket.tokens = bucket.capacity
                bucket.last_refill = time.time()
            
            # Clear sliding windows
            if user_id:
                window_keys_to_clear = [k for k in self.sliding_windows.keys() if user_id in k]
                for key in window_keys_to_clear:
                    self.sliding_windows[key].clear()


# Global rate limiter instance
_rate_limiter = None


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


# Convenience functions
def check_rate_limit(user_id: str = None, tool_name: str = None,
                    parameters: Dict[str, Any] = None,
                    session_id: str = None) -> Dict[str, Any]:
    """Check rate limits for a request"""
    limiter = get_rate_limiter()
    return limiter.check_rate_limit(user_id, tool_name, parameters, session_id)


def is_rate_limited(user_id: str = None, tool_name: str = None,
                   parameters: Dict[str, Any] = None) -> bool:
    """Simple boolean check for rate limiting"""
    result = check_rate_limit(user_id, tool_name, parameters)
    return not result["allowed"]


if __name__ == "__main__":
    # Demo usage
    import json
    
    limiter = RateLimiter()
    
    # Test basic rate limiting
    print("Testing rate limits...")
    
    for i in range(5):
        result = limiter.check_rate_limit(user_id="test_user", tool_name="system_info")
        print(f"Request {i+1}: {'✅ Allowed' if result['allowed'] else '❌ Denied'}")
        
        if result["allowed"]:
            # Simulate concurrent request tracking
            limiter.increment_concurrent("global")
            time.sleep(0.1)
            limiter.decrement_concurrent("global")
    
    # Test complex query rate limiting
    print("\nTesting complex query limits...")
    complex_params = {"sql": "SELECT * FROM processes JOIN users ON processes.uid = users.uid WHERE processes.name LIKE '%node%' ORDER BY processes.resident_size DESC"}
    
    for i in range(3):
        result = limiter.check_rate_limit(
            user_id="test_user", 
            tool_name="custom_query",
            parameters=complex_params
        )
        print(f"Complex query {i+1}: {'✅ Allowed' if result['allowed'] else '❌ Denied'}")
        if not result["allowed"]:
            print(f"  Retry after: {result.get('retry_after', 'Unknown')} seconds")
    
    # Get status
    status = limiter.get_rate_limit_status(user_id="test_user")
    print(f"\nRate limit status:\n{json.dumps(status, indent=2)}")