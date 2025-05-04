import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Optional, Callable
import logging
from ..config import settings

logger = logging.getLogger(__name__)

def clear_cache(pattern: Optional[str] = None) -> int:
    """Clear cached responses matching the optional pattern"""
    if not settings.CACHE_DIR.exists():
        return 0
        
    count = 0
    try:
        for file in settings.CACHE_DIR.glob("*.json"):
            try:
                if pattern:
                    # Read cache file to check content
                    with file.open('r') as f:
                        cache_data = json.load(f)
                        cache_key = cache_data.get('cache_key', '')
                        if pattern in cache_key:
                            file.unlink()
                            count += 1
                else:
                    file.unlink()
                    count += 1
            except Exception as e:
                logger.warning(f"Error processing cache file {file}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        
    return count

def cache_sec_response(expires_after: Optional[timedelta] = None):
    """Decorator to cache SEC API responses"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Generate cache key
            cache_key = f"{func.__name__}_{str(args)}_{str(kwargs)}"
            cache_hash = hashlib.md5(cache_key.encode()).hexdigest()
            cache_file = settings.CACHE_DIR / f"{cache_hash}.json"
            
            # Ensure cache directory exists
            settings.CACHE_DIR.mkdir(exist_ok=True)
            
            if cache_file.exists():
                try:
                    with cache_file.open('r') as f:
                        cached_data = json.load(f)
                        cached_time = datetime.fromisoformat(cached_data['cached_at'])
                        
                        if expires_after and datetime.now() - cached_time > expires_after:
                            logger.debug(f"Cache expired for {func.__name__}")
                        else:
                            logger.debug(f"Cache hit for {func.__name__}")
                            return cached_data['data']
                except Exception as e:
                    logger.warning(f"Error reading cache: {str(e)}")
            
            # Get fresh data
            data = func(*args, **kwargs)
            
            # Cache the response
            try:
                cache_data = {
                    'cached_at': datetime.now().isoformat(),
                    'data': data,
                    'cache_key': cache_key
                }
                with cache_file.open('w') as f:
                    json.dump(cache_data, f)
                logger.debug(f"Cached response for {func.__name__}")
            except Exception as e:
                logger.warning(f"Error caching response: {str(e)}")
            
            return data
            
        return wrapper
    return decorator