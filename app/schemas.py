from app import ma

from app.models import *

from marshmallow import fields


class UserSchema(ma.TableSchema):
    class Meta:
        table = User.__table__
        
    #requests = fields.Nested('RequestSchema',  many=True, only=["id", "transactions", "other", "credit", "status"])
    #audits = fields.Nested('AuditLogSchema',  many=True, only=["id", "target_type", "target_id", "state_before", "state_after"])
    

class OtherSchema(ma.TableSchema):
    class Meta:
        table = Other.__table__
        
    requests = fields.Nested('RequestSchema',  many=True, only=["id", "user", "transactions", "credit", "status"])


class CatalogSchema(ma.TableSchema):
    class Meta:
        table = Catalog.__table__
        
    transactions = fields.Nested("TransactionSchema", many=True, only=["id", "request", "amount"])


class RequestSchema(ma.TableSchema):
    class Meta:
        table = Request.__table__
    user_id = fields.Int()
    other_id = fields.Int()
    
    transactions = fields.Nested("TransactionSchema", many=True, only=["id", "catalog", "amount"])
    user = fields.Nested('UserSchema', only=["id", "email", "fullname", "role"])
    other = fields.Nested('OtherSchema', only=["id", "fullname", "phone", "staff"])


class TransactionSchema(ma.TableSchema):
    class Meta:
        table = Transaction.__table__
    catalog_id = fields.Int()
    request_id = fields.Int()
    
    stock = fields.Nested('StockSchema', only=["id", "name", "description", "unit"])
    request = fields.Nested('RequestSchema', only=["id", "user", "other", "credit", "status"])


class StockReportSchema(ma.TableSchema):
    class Meta:
        table = StockReport.__table__
    stock_id = fields.Int()


class AuditLogSchema(ma.TableSchema):
    class Meta:
        table = AuditLog.__table__
    user_id = fields.Int()
    action = fields.String()
    
    user = fields.Nested('UserSchema', only=["id", "email", "fullname", "role"])


class StockSchema(ma.TableSchema):
    class Meta:
        table = Stock.__table__
    catalog_id = fields.Int()
    store_id = fields.Int()

    catalog = fields.Nested('StockSchema', only=["id", "name", "description", "unit"])


class StoreSchema(ma.TableSchema):
    class Meta:
        table = Store.__table__


