from flask import jsonify

from app.api import bp, login_required

from app.schemas import *
from app.models import *

from app import db


@bp.route("/stock", methods=["POST"])
@login_required
def create_stock():
    data = request.get_json()

    if data is None:
        return jsonify(status="failed", message="No Data Sent!")

    if not data.get("catalog_id"):
        return jsonify(status="failed", message="Catalog Id Required!")
    if not data.get("store_id"):
        return jsonify(status="failed", message="Store Id Required!")

    catalog_model = Catalog.query.get(data.get('catalog_id'))
    if not catalog_model:
        return jsonify(status="failed", message="Catalog Not Found!")
    
    store_model = Store.query.get(data.get('store_id'))
    if not store_model:
        return jsonify(status="failed", message="Store Not Found!")
    
    stock_model = Stock.query.filter_by(
        catalog_id=data.get('catalog_id'),
        store_id=data.get('store_id'),
    ).first()
    if stock_model:
        return jsonify(status="failed", message="Catalog already stocked for Store!")

    stock_model = Stock()
    stock_model.amount = data.get("amount") or 0
    stock_model.catalog_id = data.get("catalog_id")
    stock_model.store_id = data.get("store_id")

    db.session.add(stock_model)
    db.session.commit()

    stock_schema = StockSchema().dump(stock_model).data
    return jsonify(status="success", message="Stock Added SuccessFul", data=stock_schema)


@bp.route("/stocks", methods=["POST"])
@login_required
def create_stocks():
    datas = request.get_json()

    if datas is None:
        return jsonify(status="failed", message="No Data Sent!")
    if not datas.get("stocks"):
        return jsonify(status="failed", message="No Stocks Sent!")
    stock_models = []
    for data in datas.get("stocks"):
        if data is None:
            return jsonify(status="failed", message="No Data Sent!")

        if not data.get("catalog_id"):
            return jsonify(status="failed", message="Catalog Id Required!")
        if not data.get("store_id"):
            return jsonify(status="failed", message="Store Id Required!")

        catalog_model = Catalog.query.get(data.get('catalog_id'))
        if not catalog_model:
            return jsonify(status="failed", message="Catalog Not Found!")

        store_model = Store.query.get(data.get('store_id'))
        if not store_model:
            return jsonify(status="failed", message="Store Not Found!")

        stock_model = Stock.query.filter_by(
            catalog_id=data.get('catalog_id'),
            store_id=data.get('store_id'),
        ).first()
        if stock_model:
            return jsonify(status="failed", message="Catalog already stocked for Store!")

        stock_model = Stock()
        stock_model.amount = data.get("amount") or 0
        stock_model.catalog_id = data.get("catalog_id")
        stock_model.store_id = data.get("store_id")

        db.session.add(stock_model)
        stock_models.append(stock_model)
    db.session.commit()

    stock_schema = StockSchema(many=True).dump(stock_models).data
    return jsonify(status="success", message="Stocks Added SuccessFul", data=stock_schema)


@bp.route("/stock/<stock_id>")
@login_required
def get_stock(stock_id):
    stock_model = Stock.query.get(stock_id)
    if not stock_model:
        return jsonify(status="failed", message="Stock Item Not Found!")

    stock_schema = StockSchema().dump(stock_model).data
    return jsonify(status="success", message="Stock Item Found", data=stock_schema)


@bp.route("/stock")
@login_required
def get_stocks():
    stock_model = Stock.query.order_by(Stock.created.desc()).all()
    if not stock_model:
        return jsonify(status="failed", message="Stock Item Not Found!")

    stock_schema = StockSchema(many=True).dump(stock_model).data
    return jsonify(status="success", message="Stock Items Found", data=stock_schema)


@bp.route("/stock/<stock_id>/transactions")
@login_required
def get_stock_transactions(stock_id):
    stock_model = Stock.query.get(stock_id)
    if not stock_model:
        return jsonify(status="failed", message="Stock Item Not Found!")
    transactions = Transaction.query.filter_by(stock_id=stock_id).all()
    transactions_schema = TransactionSchema(many=True).dump(transactions).data
    return jsonify(status="success", message="Stock Transactions Found", data=transactions_schema)


