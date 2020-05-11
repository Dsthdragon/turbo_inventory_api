from flask import jsonify

from app.api import bp, login_required

from app.schemas import *
from app.models import *

from app import db


@bp.route("/hold_item", methods=["POST"])
@login_required
def create_hold_item():
    data = request.get_json()

    if data is None:
        return jsonify(status="failed", message="No Data Sent!")

    if not data.get("stock_id"):
        return jsonify(status="failed", message="Stock Id Required!")
    if not data.get("store_id"):
        return jsonify(status="failed", message="Store Id Required!")
    if not data.get("identity"):
        return jsonify(status="failed", message="Identity Required!")
    if not data.get("reason"):
        return jsonify(status="failed", message="reason Required!")

    stock_model = Stock.query.get(data.get('stock_id'))
    if not stock_model:
        return jsonify(status="failed", message="Stock Not Found!")
    
    store_model = Store.query.get(data.get('store_id'))
    if not store_model:
        return jsonify(status="failed", message="Store Not Found!")

    hold_item_model = HoldItem()
    hold_item_model.store_id = store_model.id
    hold_item_model.stock_id = stock_model.store_id
    hold_item_model.reason = data.get('reason')
    hold_item_model.identity = data.get('identity')
    hold_item_model.in_store = True

    db.session.add(hold_item_model)
    db.session.commit()

    hold_item_schema = HoldItemSchema().dump(hold_item_model).data
    return jsonify(status="success", message="Item Added SuccessFul", data=hold_item_schema)


@bp.route("/hold_item/<hold_item_id>")
@login_required
def get_hold_item(hold_item_id):
    hold_item_model = HoldItem.query.get(hold_item_id)
    if not hold_item_model:
        return jsonify(status="failed", message="Held Item Not Found!")

    hold_item_schema = HoldItemSchema().dump(hold_item_model).data
    return jsonify(status="success", message="Held Item Found", data=hold_item_schema)


@bp.route("/hold_item/<hold_item_id>/remove")
@login_required
def get_remove_hold_item(hold_item_id):
    hold_item_model = HoldItem.query.get(hold_item_id)
    if not hold_item_model:
        return jsonify(status="failed", message="Held Item Not Found!")
    hold_item_model.in_store =False
    db.session.commit()
    hold_item_schema = HoldItemSchema().dump(hold_item_model).data
    return jsonify(status="success", message="Held Item Found", data=hold_item_schema)


@bp.route("/hold_item")
@login_required
def get_hold_items():
    hold_item_model = HoldItem.query.order_by(HoldItem.created.desc())\
        .order_by(HoldItem.created.desc()).all()
    if not hold_item_model:
        return jsonify(status="failed", message="Held Item Not Found!")

    held_item_schema = HoldItemSchema(many=True).dump(hold_item_model).data
    return jsonify(status="success", message="Held Items Found", data=held_item_schema)


@bp.route("/stock/<stock_id>/hold_items")
@login_required
def get_stock_hold_items(stock_id):
    held_item = HoldItem.query.filter_by(stock_id=stock_id)\
        .order_by(HoldItem.created.desc()).all()
    held_item_schema = HoldItemSchema(many=True).dump(held_item).data
    return jsonify(status="success", message="Held Items Found", data=held_item_schema)


@bp.route("/store/<store_id>/hold_items")
@login_required
def get_store_hold_items(store_id):
    held_item = HoldItem.query.filter_by(store_id=store_id)\
        .order_by(HoldItem.created.desc()).all()
    held_item_schema = HoldItemSchema(many=True).dump(held_item).data
    return jsonify(status="success", message="Held Items Found", data=held_item_schema)



