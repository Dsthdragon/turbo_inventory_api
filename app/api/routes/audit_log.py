from flask import jsonify

from app.api import bp, login_required

from app.schemas import *
from app.models import *


@login_required
@bp.route("/audit_log")
def get_logs():
    audit_log_model = AuditLog.query.all()
    if not audit_log_model:
        return jsonify(status="failed", message="Audit Log Not Found")
    audit_log_schema = AuditLogSchema(many=True).dump(audit_log_model).data

    return jsonify(status="success", message="Audit logs Found", data=audit_log_schema)


@login_required
@bp.route("/audit_log/<audit_id>")
def get_log(audit_id):
    audit_log_model = AuditLog.query.get(audit_id)
    if not audit_log_model:
        return jsonify(status="failed", message="Audit Log Not Found")
    audit_log_schema = AuditLogSchema().dump(audit_log_model).data

    return jsonify(status="success", message="Audit Log Found", data=audit_log_schema)

