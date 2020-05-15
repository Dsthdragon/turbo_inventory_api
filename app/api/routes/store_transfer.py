from flask import jsonify

from sqlalchemy import or_

from app.api import bp, login_required

from app.schemas import *
from app.models import *


@bp.route("/store_transfer")
@login_required
def get_store_transfers():
    store_transfers = StoreTransfer.query.order_by(StoreTransfer.created.desc()).all()
    if not store_transfers:
        return jsonify(status='failed', message='Store Transfer not found')

    store_transfer_schema = StoreTransferSchema(many=True).dump(store_transfers).data

    return jsonify(status='success', message="Store Transfer Found", data=store_transfer_schema)


@bp.route("/store/<store_id>/transfers")
@login_required
def get_store_single_transfers(store_id):
    store_transfers = StoreTransfer.query.filter(
        or_(
            StoreTransfer.from_store_id == store_id,
            StoreTransfer.to_store_id == store_id
        )
    )\
        .order_by(StoreTransfer.created.desc()).all()

    store_transfer_schema = StoreTransferSchema(many=True).dump(store_transfers).data

    return jsonify(status='success', message="Store Transfer Found", data=store_transfer_schema)


@bp.route("/store/<store_id>/transfers/to")
@login_required
def get_store_single_transfers_to(store_id):
    store_transfers = StoreTransfer.query.filter_by(to_store_id=store_id).order_by(StoreTransfer.created.desc()).all()

    store_transfer_schema = StoreTransferSchema(many=True).dump(store_transfers).data

    return jsonify(status='success', message="Store Transfer Found", data=store_transfer_schema)


@bp.route("/store/<store_id>/transfers/from")
@login_required
def get_store_single_transfers_from(store_id):
    store_transfers = StoreTransfer.query.filter_by(from_store_id=store_id)\
        .order_by(StoreTransfer.created.desc()).all()

    store_transfer_schema = StoreTransferSchema(many=True).dump(store_transfers).data

    return jsonify(status='success', message="Store Transfer Found", data=store_transfer_schema)


@bp.route("/store_transfer", methods=["POST"])
@login_required
def create_store_transfer():
    data = request.get_json()
    if not data:
        return jsonify(status="failed", message="No Data sent")

    if not data.get("items"):
        return jsonify(status="failed", message="No Transfer Items found!")

    store_transfer_model = StoreTransfer()
    store_transfer_model.sent_user_id = User.decode_token(request.cookies.get('auth'))
    store_transfer_model.from_store_id = data.get('from_store_id')
    store_transfer_model.to_store_id = data.get('to_store_id')
    store_transfer_model.status = 'pending'

    db.session.add(store_transfer_model)
    items = []
    for item in data.get("items"):
        if item.get("stock_id") in items:
            return jsonify(status="failed", message="Cant make multi request for stock item!")
        stock_model = Stock.query.get(item.get("stock_id"))
        if not stock_model:
            return jsonify(status="failed", message="Stock Item not found!")
        if not item.get("amount"):
            return jsonify(status="failed", message="Amount Required found!")
        if item.get("amount") > stock_model.amount:
            return jsonify(status="failed", message="{}'s stock is insufficient!".format(stock_model.catalog.name))
        
        items.append(item.get("stock_id"))
        transfer_item_model = TransferItem()
        transfer_item_model.stock_id = stock_model.id
        transfer_item_model.amount = item.get("amount")
        transfer_item_model.store_transfer = store_transfer_model

        db.session.add(transfer_item_model)
    db.session.commit()
    store_transfer_schema = StoreTransferSchema().dump(store_transfer_model).data
    return jsonify(
        status='success',
        message="Store Transfer Created",
        data=store_transfer_schema
    )


@bp.route("/store_transfer/<store_transfer_id>")
@login_required
def get_store_transfer(store_transfer_id):
    store_transfer_model = StoreTransfer.query.get(store_transfer_id)
    if not store_transfer_model:
        return jsonify(status="failed", message="Store Transfer not found")
    return jsonify(
        status="success",
        message="Store Transfer Found",
        data=StoreTransferSchema().dump(store_transfer_model).data
    )


@bp.route("/store_transfer/<store_transfer_id>", methods=["PUT"])
@login_required
def update_store_transfer(store_transfer_id):
    data = request.get_json()
    if not data:
        return jsonify(status="failed", message="No Data sent")

    if not data.get("status"):
        return jsonify(status="failed", message="Status Required")
    store_transfer_model = StoreTransfer.query.get(store_transfer_id)
    if not store_transfer_model:
        return jsonify(status="failed", message="Store Transfer Not Found")

    user_model = User.query.get(User.decode_token(request.cookies.get('auth')))
    if data.get("status").lower() == "approved" and store_transfer_model.status == "pending":
        store_transfer_model.deduct_from_store(data.get("status").lower(), user_model.id)
        return jsonify(
            status="success",
            message="Store Transfer Approved",
            data=StoreTransferSchema().dump(store_transfer_model).data
        )
    elif data.get("status").lower() == "accepted" and store_transfer_model.status == 'approved':
        store_transfer_model.add_to_store(data.get("status").lower(), user_model.id)
        return jsonify(
            status="success",
            message="Store Transfer Accepted",
            data=StoreTransferSchema().dump(store_transfer_model).data
        )
    elif data.get("status").lower() == "rejected" and store_transfer_model.status == 'pending':
        store_transfer_model.status = data.get("status").lower()
        db.session.commit()
        return jsonify(status="success", message="Request Rejected And Deleted")

    return jsonify(status="failed", message="Invalid Status Sent")
    
    
@bp.route("/store_transfer/<store_transfer_id>/items")
@login_required
def get_store_transfer_items(store_transfer_id):
    transfer_items_models = TransferItem.query.filter_by(store_transfer_id=store_transfer_id)\
        .order_by(TransferItem.created.desc()).all()
    if not transfer_items_models:
        return jsonify(status='failed', message='No Items Found!')
    transfer_item_schema = TransferItemSchema(many=True).dump(transfer_items_models).data
    return jsonify(status='success', message='Store Transfer Item Found!', data=transfer_item_schema)

    
@bp.route("/transfer_item")
@login_required
def get_transfers_items():
    transfer_items_models = TransferItem.query.order_by(TransferItem.created.desc()).all()
    if not transfer_items_models:
        return jsonify(status='failed', message='No Transfer Items Found!')
    transfer_item_schema = TransferItemSchema(many=True).dump(transfer_items_models).data
    return jsonify(status='success', message='Transfer Items Found!', data=transfer_item_schema)

    
@bp.route("/transfer_item/<transfer_item_id>")
@login_required
def get_transfer_item(transfer_item_id):
    transfer_items_model = TransferItem.query.get(transfer_item_id)
    if not transfer_items_model:
        return jsonify(status='failed', message='Transfer Item Not Found!')
    transfer_items_schema = TransferItemSchema().dump(transfer_items_model).data
    return jsonify(status='success', message='Transfer Item Found!', data=transfer_items_schema)
