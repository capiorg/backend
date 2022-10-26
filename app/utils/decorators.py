from functools import wraps


def standardize_response(status_code: int):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result_func = await func(*args, **kwargs)
            response = {
                "status": True,
                "code": status_code,
                "result": result_func,
            }
            return response

        return wrapper

    return decorator
