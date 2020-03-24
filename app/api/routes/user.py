from flask import jsonify, make_response

from app.api import bp, login_required

from app.schemas import *
from app.models import *

from app import db

import re

email_regex = "^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"


@bp.route("/user", methods=["POST"])
@login_required
def create_user():
    data = request.get_json()

    if data is None:
        return jsonify(status="failed", message="No Data Sent!")
    if not data.get("email"):
        return jsonify(status="failed", message="Email Address required!")
    if not re.search(email_regex, data.get("email")):
        return jsonify(status="failed", message="Invalid Email Address!")
    if not data.get("fullname"):
        return jsonify(status="failed", message="Fullname required!")
    if not data.get("password"):
        return jsonify(status="failed", message="Password required!")
    if not data.get("role"):
        return jsonify(status="failed", message="Role required!")

    user = User.query.filter_by(email=data["email"]).first()
    if user:
        return jsonify(status="failed", message="Email Address already in system!")

    user = User()
    user.email = data.get("email")
    user.fullname = data.get("fullname")
    user.role = data.get("role")

    user.set_password(data.get("password"))

    db.session.add(user)
    db.session.commit()

    user = UserSchema().dump(user)
    return jsonify(status="success", message="Registration SuccessFul", data=user.data)


@bp.route("/user")
@login_required
def get_users():
    user = User.query.all()
    user_schema = UserSchema(many=True, strict=True).dump(user)
    return jsonify(status="success", message="Users Found", data=user_schema.data)


@bp.route("/user/login",  methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify(status='failed', message="No data sent!")
    user = User.query.filter_by(email=data.get("email")).first()
    if user and user.check_password(data.get("password")):
        user_schema = UserSchema().dump(user)
        auth = user.generate_token()
        resp = make_response(jsonify(status="success", message="Login Successful!", data=user_schema.data, auth=auth))
        resp.set_cookie('auth', auth)
        return resp
    return jsonify(status="failed", message="Invalid login details")
