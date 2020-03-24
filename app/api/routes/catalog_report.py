from flask import jsonify

from app.api import bp, login_required

from app.schemas import *
from app.models import *

from app import db


@bp.route("/catalog_report")
@login_required
def get_catalog_reports():
    catalog_report_models = CatalogReport.query.all()
    if not catalog_report_models:
        return jsonify(status="failed", message="No Report Found")
    return jsonify(
        status="success",
        message="Reports Found",
        data=CatalogReportSchema(many=True).dump(catalog_report_models).data
    )


@bp.route("/catalog_report/<catalog_id>/reports")
@login_required
def get_catalog_report(catalog_id):
    catalog_report_models = CatalogReport.query.filter_by(catalog_id=catalog_id).all()
    if not catalog_report_models:
        return jsonify(status="failed", message="No Report Found For Catalog")
    return jsonify(
        status="success",
        message="Reports Found",
        data=CatalogReportSchema(many=True).dump(catalog_report_models).data
    )


@bp.route("/catalog_report/<catalog_report_id>")
@login_required
def get_single_catalog_report(catalog_report_id):
    catalog_report_model = CatalogReport.query.get(catalog_report_id)
    if not catalog_report_model:
        return jsonify(status="failed", message="No Report Found For Catalog")
    return jsonify(
        status="success",
        message="Report Found",
        data=CatalogReportSchema().dump(catalog_report_model).data
    )




