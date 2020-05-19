from flask import request
from sqlalchemy import inspect, event, cast, Date
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm.attributes import get_history
from werkzeug.security import generate_password_hash, check_password_hash

from app import db

from datetime import datetime, date

from config import Config

from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

import json

import jwt

ACTION_CREATE = 1
ACTION_UPDATE = 2
ACTION_DELETE = 3

StoreUser = db.Table(
    "store_user",
    db.Column("store_id", db.Integer, db.ForeignKey("store.id"), primary_key=False),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=False)
)


class AuditableMixin:
    @staticmethod
    def create_audit(connection, object_type, object_id, action, **kwargs):
        user_id = User.decode_token(request.cookies.get('auth'))
        user = User.query.get(user_id)
        if user:
            audit = AuditLog()
            audit.user_id = user_id
            audit.target_type = object_type
            audit.target_id = object_id
            audit.state_action = action
            audit.state_before = kwargs.get("state_before")
            audit.state_after = kwargs.get("state_after")
            audit.save(connection)

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, "after_insert", cls.audit_insert)
        event.listen(cls, "after_delete", cls.audit_delete)
        event.listen(cls, "after_update", cls.audit_update)

    @staticmethod
    def audit_insert(mapper, connection, target):
        """Listen for the `after_insert` event and create an AuditLog entry"""

        state_before = {}
        state_after = {}
        inspector = inspect(target)
        attrs = class_mapper(target.__class__).column_attrs
        for attr in attrs:
            hist = getattr(inspector.attrs, attr.key).history
            if hist.has_changes():
                state_after[attr.key] = getattr(target, attr.key)
        target.create_audit(
            connection,
            target.__tablename__,
            target.id,
            ACTION_CREATE,
            state_before=json.dumps(state_before),
            state_after=json.dumps(state_after),
        )

    @staticmethod
    def audit_delete(mapper, connection, target):
        """Listen for the `after_delete` event and create an AuditLog entry"""
        state_before = {}
        state_after = {}
        attrs = class_mapper(target.__class__).column_attrs
        for attr in attrs:
            if attr.key not in ["created", "updated"]:
                _temp = get_history(target, attr.key)
                state_before[attr.key] = _temp.unchanged[0]
        target.create_audit(
            connection,
            target.__tablename__,
            target.id,
            ACTION_DELETE,
            state_before=json.dumps(state_before),
            state_after=json.dumps(state_after),
        )

    @staticmethod
    def audit_update(mapper, connection, target):
        """Listen for the `after_update` event and create an AuditLog entry with before and after state changes"""
        state_before = {}
        state_after = {}
        inspector = inspect(target)
        attrs = class_mapper(target.__class__).column_attrs
        for attr in attrs:
            hist = getattr(inspector.attrs, attr.key).history
            if hist.has_changes():
                state_before[attr.key] = get_history(target, attr.key)[2].pop()
                state_after[attr.key] = getattr(target, attr.key)

        target.create_audit(
            connection,
            target.__tablename__,
            target.id,
            ACTION_UPDATE,
            state_before=json.dumps(state_before),
            state_after=json.dumps(state_after),
        )


class Store(AuditableMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    address = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)

    users = db.relationship("User", secondary=StoreUser, lazy="subquery", backref=db.backref("stores", lazy=True))


class User(AuditableMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(EncryptedType(db.String, Config.SECRET_KEY, AesEngine, 'pkcs5'), nullable=False)
    fullname = db.Column(EncryptedType(db.String(255), Config.SECRET_KEY, AesEngine, 'pkcs5'), nullable=False)
    password_hash = db.Column(db.String(300), nullable=False)
    role = db.Column(db.String(255), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)
    blocked = db.Column(db.Boolean, default=False)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_token(self):
        return jwt.encode(
            {
                'id': self.id
            },
            Config.SECRET_KEY,
            algorithm='HS256'
        ).decode()

    @staticmethod
    def decode_token(token):
        try:
            payload = jwt.decode(token, Config.SECRET_KEY)
            return payload['id']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


class Other(AuditableMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(EncryptedType(db.String, Config.SECRET_KEY, AesEngine, 'pkcs5'), nullable=False)
    phone = db.Column(EncryptedType(db.String, Config.SECRET_KEY, AesEngine, 'pkcs5'), nullable=False)
    blocked = db.Column(db.Boolean, default=False)
    staff = db.Column(db.Boolean, default=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)


class Stock(AuditableMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    catalog_id = db.Column(db.Integer, db.ForeignKey("catalog.id"), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey("store.id"), nullable=False)
    amount = db.Column(db.Float, default=0)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)

    store = db.relationship("Store", backref=db.backref("stocks", lazy=True, cascade="all,delete"))
    catalog = db.relationship("Catalog", backref=db.backref("stocks", lazy=True, cascade="all,delete"))


class Catalog(AuditableMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    unit = db.Column(db.String(100))
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)


class RequestResponse(AuditableMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    action = db.Column(db.String(100))
    comment = db.Column(db.Text)
    request_id = db.Column(db.Integer, db.ForeignKey("request.id"), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("responses", lazy=True))
    request = db.relationship("Request", backref=db.backref("responses", lazy=True))


class StoreTransfer(AuditableMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sent_user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    received_user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    approved_user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    from_store_id = db.Column(db.Integer, db.ForeignKey("store.id"), nullable=False)
    to_store_id = db.Column(db.Integer, db.ForeignKey("store.id"), nullable=False)
    status = db.Column(db.String(255), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)

    sent_by = db.relationship("User", backref=db.backref("transfers_sent", lazy=True), foreign_keys=[sent_user_id])
    received_by = db.relationship("User", backref=db.backref("transfers_received", lazy=True), foreign_keys=[received_user_id])
    approved_by = db.relationship("User", backref=db.backref("transfers_approved", lazy=True), foreign_keys=[approved_user_id])

    from_store = db.relationship("Store", backref=db.backref("transferred_from", lazy=True), foreign_keys=[from_store_id])
    to_store = db.relationship("Store", backref=db.backref("transferred_to", lazy=True), foreign_keys=[to_store_id])

    def deduct_from_store(self, status, user_id):
        for item in self.transfer_items:
            stock_model = Stock.query.get(item.stock_id)
            stock_report_model = StockReport.query.filter_by(
                stock_id=stock_model.id
            ).filter(
                cast(StockReport.created, Date) == date.today()
            ).first()
            if not stock_report_model:
                stock_report_model = StockReport()
                stock_report_model.stock_id = stock_model.id
                stock_report_model.add = 0
                stock_report_model.taken = 0
                stock_report_model.transactions = 0
                db.session.add(stock_report_model)

            stock_model.amount -= item.amount
            stock_report_model.taken += item.amount
            stock_report_model.transactions += 1
            stock_report_model.remaining = stock_model.amount

        self.approved_user_id = user_id
        self.status = status
        db.session.commit()

    def add_to_store(self, status, user_id):
        for item in self.transfer_items:

            stock_model = Stock.query.filter_by(store_id=self.to_store_id, catalog_id=item.stock.catalog_id).first()
            if not stock_model:
                stock_model = Stock()
                stock_model.catalog_id = item.stock.catalog_id
                stock_model.store_id = self.to_store_id
                stock_model.amount = 0
                db.session.add(stock_model)

            stock_report_model = StockReport.query.filter_by(
                stock_id=stock_model.id
            ).filter(
                cast(StockReport.created, Date) == date.today()
            ).first()
            if not stock_report_model:
                stock_report_model = StockReport()
                stock_report_model.stock_id = stock_model.id
                stock_report_model.add = 0
                stock_report_model.taken = 0
                stock_report_model.transactions = 0
                db.session.add(stock_report_model)

            item.other_stock_id = stock_model.id
            stock_model.amount += item.amount
            stock_report_model.add += item.amount
            stock_report_model.transactions += 1
            stock_report_model.remaining = stock_model.amount

        self.received_user_id = user_id
        self.status = status
        db.session.commit()


class TransferItem(AuditableMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_transfer_id = db.Column(db.Integer, db.ForeignKey("store_transfer.id"), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey("stock.id"), nullable=False)
    other_stock_id = db.Column(db.Integer, db.ForeignKey("stock.id"))
    amount = db.Column(db.Float, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)

    store_transfer = db.relationship("StoreTransfer", backref=db.backref("transfer_items", lazy=True, cascade="all,delete"))
    stock = db.relationship("Stock", backref=db.backref("transfer_items_deduct", lazy=True, cascade="all,delete"), foreign_keys=[stock_id])
    other_stock = db.relationship("Stock", backref=db.backref("transfer_items_added", lazy=True, cascade="all,delete"), foreign_keys=[other_stock_id])


class HoldItem(AuditableMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey("stock.id"), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey("store.id"), nullable=False)
    amount = db.Column(db.Float, default=1) 
    identity = db.Column(db.Text)
    reason = db.Column(db.Text)
    in_store = db.Column(db.Boolean)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)

    store = db.relationship("Store", backref=db.backref("held_items", lazy=True))
    stock = db.relationship("Stock", backref=db.backref("held_items", lazy=True, cascade="all,delete"))


class Request(AuditableMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    other_id = db.Column(db.Integer, db.ForeignKey("other.id"))
    store_id = db.Column(db.Integer, db.ForeignKey("store.id"), nullable=False)
    credit = db.Column(db.Boolean, default=True)
    comment = db.Column(db.Text)
    status = db.Column(db.String(255), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("requests", lazy=True))
    other = db.relationship("Other", backref=db.backref("requests", lazy=True))
    store = db.relationship("Store", backref=db.backref("requests", lazy=True))

    def validate_transactions(self, status):
        for transaction in self.transactions:
            stock_model = Stock.query.get(transaction.stock_id)
            stock_report_model = StockReport.query.filter_by(
                stock_id=stock_model.id
            ).filter(
                cast(StockReport.created, Date) == date.today()
            ).first()
            if not stock_report_model:
                stock_report_model = StockReport()
                stock_report_model.stock_id = stock_model.id
                stock_report_model.add = 0
                stock_report_model.taken = 0
                stock_report_model.transactions = 0
                db.session.add(stock_report_model)

            if self.credit:
                stock_model.amount += transaction.amount
                stock_report_model.add += transaction.amount
            else:
                stock_model.amount -= transaction.amount
                stock_report_model.taken += transaction.amount
            stock_report_model.transactions += 1
            stock_report_model.remaining = stock_model.amount

        self.status = status
        db.session.commit()


class Transaction(AuditableMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("request.id"), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey("stock.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)

    request = db.relationship("Request", backref=db.backref("transactions", lazy=True, cascade="all,delete"))
    stock = db.relationship("Stock", backref=db.backref("transactions", lazy=True, cascade="all,delete"))

    @hybrid_property
    def store(self):
        return self.request.store

class StockReport(AuditableMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey("stock.id"), nullable=False)
    transactions = db.Column(db.Integer, default=0)
    taken = db.Column(db.Float, nullable=False, default=0)
    add = db.Column(db.Float, nullable=False, default=0)
    remaining = db.Column(db.Float, nullable=False, default=0)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)

    stock = db.relationship("Stock", backref=db.backref("stock_reports", lazy=True))


class AuditLog(AuditableMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    target_type = db.Column(db.String(100), nullable=False)
    target_id = db.Column(db.Integer)
    state_action = db.Column(db.Integer)
    state_before = db.Column(db.Text)
    state_after = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("audits", lazy=True))

    def __repr__(self):
        return "<AuditLog %r: %r -> %r>" % (
            self.user_id,
            self.target_type,
            self.state_action,
        )

    def save(self, connection):
        connection.execute(
            self.__table__.insert(),
            user_id=self.user_id,
            target_type=self.target_type,
            target_id=self.target_id,
            state_action=self.state_action,
            state_before=self.state_before,
            state_after=self.state_after,
        )

    @hybrid_property
    def action(self):
        actions = {1: "CREATED", 2: "UPDATED", 3: "DELETED"}
        return actions.get(self.state_action, "ERROR")

    @hybrid_property
    def state_before_object(self):
        return json.loads(self.state_before)

    @hybrid_property
    def state_after_object(self):
        return json.loads(self.state_after)
