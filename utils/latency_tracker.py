import time
import functools

def track_latency(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        return (result, round(time.time() - start_time, 4))
    return wrapper
