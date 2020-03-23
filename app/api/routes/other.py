from flask import jsonify, make_response

from app.api import bp, login_required

from app.schemas import *
from app.models import *

from app import db

import re


@login_required
@bp.route("/other", methods=["POST"])
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

