from app import ma

from app.models import *

from marshmallow import fields

from marshmallow_enum import EnumField


class UserSchema(ma.TableSchema):
    role = EnumField(RoleType, by_value=True)

    class Meta:
        table = User.__table__


class OtherSchema(ma.TableSchema):
    class Meta:
        table = Other.__table__


class CatalogSchema(ma.TableSchema):
    class Meta:
        table = Catalog.__table__


class RequestSchema(ma.TableSchema):
    class Meta:
        table = Request.__table__


class TransactionSchema(ma.TableSchema):
    class Meta:
        table = Transaction.__table__


class CatalogReportSchema(ma.TableSchema):
    class Meta:
        table = CatalogReport.__table__


class AuditLogSchema(ma.TableSchema):
    class Meta:
        table = AuditLog.__table__




