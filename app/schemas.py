from app import ma

from app.models import *

from marshmallow import fields


class UserSchema(ma.TableSchema):
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
    user_id = fields.Int()
    other_id = fields.Int()


class TransactionSchema(ma.TableSchema):
    class Meta:
        table = Transaction.__table__
    catalog_id = fields.Int()
    request_id = fields.Int()


class CatalogReportSchema(ma.TableSchema):
    class Meta:
        table = CatalogReport.__table__
    catalog_id = fields.Int()


class AuditLogSchema(ma.TableSchema):
    class Meta:
        table = AuditLog.__table__
    user_id = fields.Int()



