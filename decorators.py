from flask import abort,session
from functools import wraps


def login_required(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        if 'username' not in session:
            abort(401)
        return func(*args, **kwargs)
    return wrapper


def role_required(required_role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if session['role'] != required_role:
                abort(403)

            return func(*args, **kwargs)
        return wrapper
    return decorator