from flask import jsonify

from app.api import bp, login_required


from app.schemas import *
from app.models import Catalog

from app import db


@bp.route("/catalog", methods=["POST"])
@login_required
def create_catalog():
    data = request.get_json()

    if data is None:
        return jsonify(status="failed", message="No Data Sent!")

    if not data.get("name"):
        return jsonify(status="failed", message="Name required!")
    if not data.get("description"):
        return jsonify(status="failed", message="Description required!")
    if not data.get("stock"):
        return jsonify(status="failed", message="Password required!")
    if not data.get("unit"):
        return jsonify(status="failed", message="Role required!")

    catalog_model = Catalog()
    catalog_model.name = data.get("name")
    catalog_model.description = data.get("description")
    catalog_model.stock = data.get("stock")
    catalog_model.unit = data.get("unit")

    db.session.add(catalog_model)
    db.session.commit()

    catalog_schema = CatalogSchema().dump(catalog_model).data
    return jsonify(status="success", message="Catalog Added SuccessFul", data=catalog_schema)


@bp.route("/catalogs", methods=["POST"])
@login_required
def create_catalogs():
    datas = request.get_json()

    if datas is None:
        return jsonify(status="failed", message="No Data Sent!")
    catalog_models = []
    for data in datas.get("catalogs"):
        if not data.get("name"):
            return jsonify(status="failed", message="Name required!")
        if not data.get("description"):
            return jsonify(status="failed", message="Description required!")
        if not data.get("stock"):
            return jsonify(status="failed", message="Password required!")
        if not data.get("unit"):
            return jsonify(status="failed", message="Role required!")

        catalog_model = Catalog()
        catalog_model.name = data.get("name")
        catalog_model.description = data.get("description")
        catalog_model.stock = data.get("stock")
        catalog_model.unit = data.get("unit")

        db.session.add(catalog_model)
        catalog_models.append(catalog_model)
    db.session.commit()

    catalog_schema = CatalogSchema(many=True).dump(catalog_models).data
    return jsonify(status="success", message="Catalogs Added SuccessFul", data=catalog_schema)


@bp.route("/catalog/<catalog_id>", methods=["PUT"])
@login_required
def update_catalog(catalog_id):
    data = request.get_json()

    if data is None:
        return jsonify(status="failed", message="No Data Sent!")

    if not data.get("name"):
        return jsonify(status="failed", message="Name required!")
    if not data.get("description"):
        return jsonify(status="failed", message="Description required!")
    if not data.get("unit"):
        return jsonify(status="failed", message="Unit required!")

    catalog_model = Catalog.query.get(catalog_id)
    if not catalog_model:
        return jsonify(status="failed", message="Catalog Not Found!")

    catalog_model.name = data.get("name")
    catalog_model.description = data.get("description")
    catalog_model.unit = data.get("unit")

    db.session.commit()

    catalog_schema = CatalogSchema().dump(catalog_model).data
    return jsonify(status="success", message="Catalog Item Update SuccessFul", data=catalog_schema)


@bp.route("/catalog/<catalog_id>")
@login_required
def get_catalog(catalog_id):
    catalog_model = Catalog.query.get(catalog_id)
    if not catalog_model:
        return jsonify(status="failed", message="Catalog Item Not Found!")

    catalog_schema = CatalogSchema().dump(catalog_model).data
    return jsonify(status="success", message="Catalog Item Found", data=catalog_schema)


@bp.route("/catalog")
@login_required
def get_catalogs():
    catalog_model = Catalog.query.order_by(Catalog.created.desc()).all()
    if not catalog_model:
        return jsonify(status="failed", message="Catalog Item Not Found!")

    catalog_schema = CatalogSchema(many=True).dump(catalog_model).data
    return jsonify(status="success", message="Catalog Items Found", data=catalog_schema)


@bp.route("/catalog/<catalog_id>/transaction")
@login_required
def get_catalog_transaction(catalog_id):
    transaction_models = Transaction.query.filter_by(catalog_id=catalog_id).order_by(Transaction.created.desc()).all()
    if not transaction_models:
        return jsonify(status='failed', message='No Transactions Found!')
    transaction_schema = TransactionSchema(many=True).dump(transaction_models).data
    return jsonify(status='success', message='Request Transaction Found!', data=transaction_schema)

