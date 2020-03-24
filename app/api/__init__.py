from functools import wraps

from flask import Blueprint, jsonify, request

from app.models import User

bp = Blueprint('api', __name__)


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        user_id = User.decode_token(request.cookies.get('auth'))
        user = User.query.get(user_id)
        if not user:
            return jsonify(status="failed", message="Login to continue", isAuth=False)
        return f(*args, **kwargs)
    return wrap


from app.api.routes import user, catalog, audit_log, other, request_transaction, catalog_report
