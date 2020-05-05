from flask import jsonify

from app.api import bp, login_required

from app.schemas import *
from app.models import *


@bp.route("/stock_report")
@login_required
def get_stock_reports():
    stock_report_models = StockReport.query.order_by(StockReport.created.desc()).all()
    if not stock_report_models:
        return jsonify(status="failed", message="No Report Found")
    return jsonify(
        status="success",
        message="Reports Found",
        data=StockReportSchema(many=True).dump(stock_report_models).data
    )


@bp.route("/stock_report/<stock_id>/reports")
@login_required
def get_stock_report(stock_id):
    stock_report_models = StockReport.query.filter_by(stock_id=stock_id).order_by(StockReport.created.desc()).all()
    if not stock_report_models:
        return jsonify(status="failed", message="No Report Found For Catalog")
    return jsonify(
        status="success",
        message="Reports Found",
        data=StockReportSchema(many=True).dump(stock_report_models).data
    )


@bp.route("/stock_report/<stock_report_id>")
@login_required
def get_single_stock_report(stock_report_id):
    stock_report_model = StockReport.query.get(stock_report_id)
    if not stock_report_model:
        return jsonify(status="failed", message="No Report Found For Catalog")
    return jsonify(
        status="success",
        message="Report Found",
        data=StockReportSchema().dump(stock_report_model).data
    )
