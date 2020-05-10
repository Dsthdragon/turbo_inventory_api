from flask import jsonify

from app.api import bp, login_required

from app.schemas import *
from app.models import *

from app import db


@bp.route("/store", methods=["POST"])
@login_required
def create_store():
    data = request.get_json()

    if data is None:
        return jsonify(status="failed", message="No Data Sent!")

    if not data.get("name"):
        return jsonify(status="failed", message="Name is Required")

    store_model = Store.query.filter_by(
        name=data.get('name')
    ).first()
    if store_model:
        return jsonify(status="failed", message="Store already in System!")

    store_model = Store()
    store_model.name = data.get("name")
    store_model.address = data.get("address")

    db.session.add(store_model)
    db.session.commit()

    store_schema = StoreSchema().dump(store_model).data
    return jsonify(status="success", message="Store Added SuccessFul", data=store_schema)


@bp.route("/store/<store_id>")
@login_required
def get_store(store_id):
    store_model = Store.query.get(store_id)
    if not store_model:
        return jsonify(status="failed", message="Store Item Not Found!")

    store_schema = StoreSchema().dump(store_model).data
    return jsonify(status="success", message="Store Item Found", data=store_schema)


@bp.route("/store")
@login_required
def get_stores():
    store_model = Store.query.order_by(Store.created.desc()).all()
    if not store_model:
        return jsonify(status="failed", message="Store Item Not Found!")

    store_schema = StoreSchema(many=True).dump(store_model).data
    return jsonify(status="success", message="Store Items Found", data=store_schema)


@bp.route("/store/<int:store_id>", methods=['PUT'])
@login_required
def update_store(store_id):
    data = request.get_json()

    if data is None:
        return jsonify(status="failed", message="No Data Sent!")
    store_model = Store.query.get(store_id)
    if not store_model:
        return jsonify(status="failed", message="Store not Found!")
    if not data.get("name"):
        return jsonify(status="failed", message="Name is Required")

    store_model.name = data.get("name")
    store_model.address = data.get("address")
    db.session.commit()
    store_schema = StoreSchema().dump(store_model).data

    return jsonify(
        status="success",
        message="Store Details Update",
        data=store_schema
    )


@bp.route("/store/<int:store_id>/users")
@login_required
def get_store_users(store_id):
    users = User.query.filter(User.stores.any(Store.id == store_id))

    return jsonify(
        status="success", message="Store Users",
        data=UserSchema(many=True).dump(users).data
    )


@bp.route("/store/<int:store_id>/requests")
@login_required
def get_store_requests(store_id):
    requests = Request.query.filter_by(store_id=store_id).order_by(Request.created.desc()).all()

    return jsonify(
        status="success", message="Store Requests",
        data=RequestSchema(many=True).dump(requests).data
    )


@bp.route("/store/<int:store_id>/transactions")
@login_required
def get_store_transactions(store_id):
    transactions = Transaction.query.filter(Stock.transactions.any(Store.id == store_id)).order_by(Transaction.created.desc()).all()

    return jsonify(
        status="success", message="Store Transactions",
        data=TransactionSchema(many=True).dump(transactions).data
    )


@bp.route("/store/<int:store_id>/users", methods=['PUT'])
@login_required
def add_user_to_store(store_id):
    data = request.get_json()

    if data is None:
        return jsonify(status="failed", message="No Data Sent!")
    store_model = Store.query.get(store_id)
    if not store_model:
        return jsonify(status="failed", message="Store not Found!")
    user_model = User.query.get(data.get('user_id'))
    if not user_model:
        return jsonify(status="failed", message="User not Found!")
    print(user_model)
    store_model.users.append(user_model)
    print(store_model.users)
    db.session.commit()

    return jsonify(
        status="success", message="User added to Store",
        data=UserSchema(many=True).dump(store_model.users).data
    )

