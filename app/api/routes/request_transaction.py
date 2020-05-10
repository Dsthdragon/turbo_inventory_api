from flask import jsonify

from app.api import bp, login_required

from app.schemas import *
from app.models import *


@bp.route("/request")
@login_required
def get_requests():
    request_models = Request.query.order_by(Request.created.desc()).all()
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
    request_model.store_id = data.get('store_id')
    request_model.comment = data.get('comment')
    request_model.credit = True if data.get("credit") else False

    db.session.add(request_model)

    for transaction in data.get("transactions"):
        stock_model = Stock.query.get(transaction.get("stock_id"))
        if not stock_model:
            return jsonify(status="failed", message="Stock Item not found!")
        if not transaction.get("amount"):
            return jsonify(status="failed", message="No transactions found!")
        if not data.get("credit") and transaction.get("amount") > stock_model.amount:
            return jsonify(status="failed", message="{}'s stock is insufficient!".format(stock_model.catalog.name))

        transaction_model = Transaction()

        transaction_model.request = request_model
        transaction_model.amount = transaction.get("amount")
        transaction_model.stock = stock_model

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
    if not request_model:
        return jsonify(status="failed", message="Request Not Found")

    user_model = User.query.get(User.decode_token(request.cookies.get('auth')))
    response = RequestResponse()
    response.comment = data.get('comment') or 'No Comment'
    response.request_id = request_model.id
    response.user_id = user_model.id
    response.action = data.get('status')
    db.session.add(response)
    if data.get("status").lower() == "approved":
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
    transaction_models = Transaction.query.filter_by(request_id=request_id).order_by(Transaction.created.desc()).all()
    if not transaction_models:
        return jsonify(status='failed', message='No Transactions Found!')
    transaction_schema = TransactionSchema(many=True).dump(transaction_models).data
    return jsonify(status='success', message='Request Transactions Found!', data=transaction_schema)

    
@bp.route("/transaction")
@login_required
def get_transactions():
    transaction_models = Transaction.query.order_by(Transaction.created.desc()).all()
    if not transaction_models:
        return jsonify(status='failed', message='No Transactions Found!')
    transaction_schema = TransactionSchema(many=True).dump(transaction_models).data
    return jsonify(status='success', message='Transactions Found!', data=transaction_schema)

    
@bp.route("/transaction/<transaction_id>")
@login_required
def get_transaction(transaction_id):
    transaction_model = Transaction.query.get(transaction_id)
    if not transaction_model:
        return jsonify(status='failed', message='Transaction Not Found!')
    transaction_schema = TransactionSchema().dump(transaction_model).data
    return jsonify(status='success', message='Transaction Found!', data=transaction_schema)
