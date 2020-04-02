from flask import jsonify

from app.api import bp, login_required

from app.schemas import *
from app.models import *


@bp.route("/audit_log")
@login_required
def get_logs():
    audit_log_model = AuditLog.query.order_by(AuditLog.created.desc()).all()
    if not audit_log_model:
        return jsonify(status="failed", message="Audit Log Not Found")
    audit_log_schema = AuditLogSchema(many=True).dump(audit_log_model).data

    return jsonify(status="success", message="Audit logs Found", data=audit_log_schema)


@bp.route("/audit_log/<audit_id>")
@login_required
def get_log(audit_id):
    audit_log_model = AuditLog.query.get(audit_id)
    if not audit_log_model:
        return jsonify(status="failed", message="Audit Log Not Found")
    audit_log_schema = AuditLogSchema().dump(audit_log_model).data

    return jsonify(status="success", message="Audit Log Found", data=audit_log_schema)

