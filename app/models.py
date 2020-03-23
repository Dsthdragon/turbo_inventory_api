from flask import request
from sqlalchemy import inspect, event
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm.attributes import get_history
from werkzeug.security import generate_password_hash, check_password_hash

from app import db

from datetime import datetime

from config import Config

from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

import json

import jwt

import enum


class RoleType(enum.Enum):
    manager = 'Manager'
    supervisor = 'Supervisor'
    storekeeper = 'Store Keeper'


class RequestStatusType(enum.Enum):
    pending = 'Pending'
    approved = 'Approved'
    accepted = 'Accepted'
    rejected = 'Rejected'


ACTION_CREATE = 1
ACTION_UPDATE = 2
ACTION_DELETE = 3


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
        print("Audited")

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


class User(AuditableMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(EncryptedType(db.String, Config.SECRET_KEY, AesEngine, 'pkcs5'), nullable=False)
    fullname = db.Column(EncryptedType(db.String(255), Config.SECRET_KEY, AesEngine, 'pkcs5'), nullable=False)
    password_hash = db.Column(db.String(300), nullable=False)
    role = db.Column(db.Enum(RoleType), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)
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
    staff = db.Column(EncryptedType(db.Boolean), default=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)


class Catalog(AuditableMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    stock = db.Column(db.Float)
    unit = db.Column(db.String(100))
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)


class Request(AuditableMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    other_id = db.Column(db.Integer, db.ForeignKey("other.id"))
    credit = db.Column(db.Boolean, default=True)
    status = db.Column(db.Enum(RequestStatusType), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)


class Transaction(AuditableMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("request.id"), nullable=False)
    catalog_id = db.Column(db.Integer, db.ForeignKey("catalog.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)


class CatalogReport(AuditableMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    catalog_id = db.Column(db.Integer, db.ForeignKey("catalog.id"), nullable=False)
    taken = db.Column(db.Float, nullable=False)
    add = db.Column(db.Float, nullable=False)
    remaining = db.Column(db.Float, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)


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
