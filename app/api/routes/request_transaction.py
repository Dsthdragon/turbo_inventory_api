from flask import jsonify

from app.api import bp, login_required

from app.schemas import *
from app.models import *


@bp.route("/request")
@login_required
def get_requests():
    request_models = Request.query.all()
    if not request_models:
        return jsonify(status='failed', message='Requests not found')

    request_schema = RequestSchema(many=True).dump(request_models).data

    return jsonify(status='success', message="Request Found", data=request_schema)


@bp.route("/request", methods=["POST"])
@login_required
def create_request():
    data = request.get_json()
    if not data:
        return jsonify(status="failed", message="No Data sent")

    other_model = Other.query.get(data.get('other_id'))
    if not other_model:
        return jsonify(status="failed", message="Other User Not found!")

    if not data.get("transactions"):
        return jsonify(status="failed", message="No transactions found!")

    request_model = Request()
    request_model.user_id = User.decode_token(request.cookies.get('auth'))
    request_model.status = "pending"
    request_model.other_id = other_model.id
    request_model.credit = True if data.get("credit") else False

    db.session.add(request_model)

    for transaction in data.get("transactions"):
        catalog_model = Catalog.query.get(transaction.get("catalog_id"))
        if not catalog_model:
            return jsonify(status="failed", message="Catalog Item not found!")
        if not transaction.get("amount"):
            return jsonify(status="failed", message="No transactions found!")
        if not data.get("credit") and transaction.get("amount") > catalog_model.stock:
            return jsonify(status="failed", message="{}'s stock is insufficient!".format(catalog_model.name))

        transaction_model = Transaction()

        transaction_model.request = request_model
        transaction_model.amount = transaction.get("amount")
        transaction_model.catalog = catalog_model

        db.session.add(transaction_model)
    db.session.commit()
    request_schema = RequestSchema().dump(request_model).data
    return jsonify(status='success', message="Request Created", data=request_schema)


@bp.route("/request/<request_id>")
@login_required
def get_request(request_id):
    request_model = Request.query.get(request_id)
    if not request_model:
        return jsonify(status="failed", message="Request not found")
    return jsonify(
        status="success",
        message="Request Found",
        data=RequestSchema().dump(request_model).data
    )


@bp.route("/request/<request_id>", methods=["PUT"])
@login_required
def update_request(request_id):
    data = request.get_json()
    if not data:
        return jsonify(status="failed", message="No Data sent")

    if not data.get("status"):
        return jsonify(status="failed", message="Status Required")
    request_model = Request.query.get(request_id)

    if data.get("status").lower() == "approved":
        user_model = User.query.get(User.decode_token(request.cookies.get('auth')))
        if user_model.role == 'Store Keeper':
            return jsonify(status="failed", message="Do not have access to this task!")
        if request_model.status == "pending":
            request_model.status = data.get("status").lower()
            db.session.commit()
            return jsonify(status="success", message="Request Approved", data=RequestSchema().dump(request_model).data)
    elif data.get("status").lower() == "accepted":
        if request_model.status == 'approved':
            request_model.validate_transactions(data.get("status").lower())
            return jsonify(status="success", message="Request Accepted", data=RequestSchema().dump(request_model).data)
    elif data.get("status").lower() == "rejected":
        if request_model.status != 'accepted':
            request_model.status = data.get("status").lower()
            db.session.commit()
            return jsonify(status="success", message="Request Rejected", data=RequestSchema().dump(request_model).data)

    return jsonify(status="failed", message="Invalid Status Sent")


@bp.route("/request/<request_id>/transaction")
@login_required
def get_request_transaction(request_id):
    transaction_models = Transaction.query.filter_by(request_id=request_id).all()
    if not transaction_models:
        return jsonify(status='failed', message='No Transactions Found!')
    transaction_schema = TransactionSchema(many=True).dump(transaction_models).data
    return jsonify(status='success', message='Request Transaction Found!', data=transaction_schema)

