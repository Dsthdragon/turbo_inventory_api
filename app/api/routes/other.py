from flask import jsonify, make_response

from app.api import bp, login_required

from app.schemas import *
from app.models import *

from app import db

import re


@bp.route("/other_user", methods=["POST"])
@login_required
def create_other():
    data = request.get_json()

    if data is None:
        return jsonify(status="failed", message="No Data Sent!")
    if not data.get("fullname"):
        return jsonify(status="failed", message="Full Name required!")
    if not data.get("phone"):
        return jsonify(status="failed", message="Phone Number required!")

    other = Other.query.filter_by(phone=data["phone"]).first()
    if other:
        return jsonify(status="failed", message="Phone Number in system!")

    other = Other()
    other.fullname = data.get("fullname")
    other.phone = data.get("phone")
    other.staff = data.get("staff")

    db.session.add(other)
    db.session.commit()

    other = OtherSchema().dump(other).data
    return jsonify(status="success", message="Task SuccessFul", data=other)


@bp.route("/other_user")
@login_required
def get_others():
    other_model = Other.query.all()
    if not other_model:
        return jsonify(status='failed', message="No Other User Found!")
    other_schema = OtherSchema(many=True).dump(other_model).data

    return jsonify(status="success", message="Other Users Found!", data=other_schema)


@bp.route("/other_user/<int:user_id>/state", methods=["PUT"])
@login_required
def change_other_user_state(user_id):
    data = request.get_json()
    if not data:
        return jsonify(status='failed', message="No data sent!")

    other = Other.query.get(user_id)

    if not other:
        return jsonify(status='failed', message="Other User Not Found!")
    other.blocked = data.get("blocked")
    db.session.commit()

    return jsonify(status='success', message="Other User State Updated!", data=OtherSchema().dump(other).data)
