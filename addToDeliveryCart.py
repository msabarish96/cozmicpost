from flask_restful import Resource
from hipbar.decorators import only_json, check_role
from hipbar.exceptions import InvalidUsage
from hipbar.common import consumerEmailStatus
from datetime import datetime, timezone
from hipbar.database import db_session as sm, session_scope, DeliveryCart, DeliveryCartItemNormal, DeliveryCartItemCashback, DeliveryCartList
from marshmallow import Schema, fields
from flask.ext.babel import format_currency, format_timedelta
from sqlalchemy.orm import lazyload
from sqlalchemy import desc


class DeliveryCartSchemaForProcess(Schema):

    class Meta:
        fields = [
            'item_id',
            'brand_name',
            'volume',
            'type',
            'price',
            'offer_price',
            'count',
            'expiry',
            'available',
            'created_at']

delivery_cart_schema_for_process = DeliveryCartSchemaForProcess(many = True)

class DeliveryCartSchema(Schema):

    class Meta:
        fields = [
            'type',
            'image',
            'count',
            'available',
            'item_id',
            'product_id',
            'brand_name',
            'volume',
            'price',
            'brand_short_name',
            'genre_short_name',
            'company_name',
            'category_name',
            'description',
            'offer_price',
            'expiry',
            'state_short_name',
            'is_on_pack',
            'promo_description']

    price = fields.Method('getPrice')
    offer_price = fields.Method('offerPrice')
    expiry = fields.Method('format_expiry')
    offerValid = fields.Method('offerValidate')

    def getPrice(self, obj):
        return format_currency(obj.price, 'INR', u'¤#,##0.00')

r   def offerPrice(self, obj):
        return format_currency(obj.offer_price, 'INR', u'¤#,##0.00')

    def format_expiry(self, obj):
        if obj.expiry:
            return format_timedelta(
                obj.expiry -
                datetime.now(
                    timezone.utc),
                add_direction=True)
        else:
            return None

    def offerValidate(self, obj):
        return 'ss'


class AddItemDelivery(Resource):

    @only_json
    @check_role(['user', 'admin'])
    def __init__(self, params, user_role, user_id):
        self.user_role = user_role
        self.user_id = user_id
        self.params = params
        self.session = sm()

        interfaces_map = {
            'normal': NormalItem,
            'cashback': CashbackItem,
        }

        # To manage get requests, which doesn't have type in req params
        if 'type' in self.params:
            if self.params['type']:
                self.ItemInterface = interfaces_map[self.params['type']]

        # Error message payloads
        self.invalid_product = {
            'errorCode': 'invalid-product',
            'message': 'Sorry! product is not valid anymore'
        }
        self.unexpected_error = {
            'errorCode': 'unexpected-error',
            'message': 'Sorry! we are not able to process your request'
        }
        self.item_not_found = {
            'errorCode': 'item-not-found',
            'message': 'Sorry! we are not able to process your request'
        }

    def post(self):
        delivery_cart_data = self.session.query(DeliveryCart).filter_by(
                consumer_id = self.user_id).order_by(
                DeliveryCart.craeted_at.desc()).limit(1).all()
        unexpected_error = {
            'status_code' = 401,
            'payload' = self.unexpected_error
        }

        with session_scope(unexpected_error) as session:
            if len(delivery_cart_data) == 0:
                self.createDeliveryCart(session)
            else:
                self.delivery_cart_id = delivery_cart_data[0].id

            item_interface = self.ItemInterface(
                self.delivery_cart_id,
                self.params['type'],
                self.params['product_id']
            )
        return item_interface.add_item()

    def put(self):
        delivery_cart_data = self.session.query(DeliveryCart).filter_by(
                consumer_id = self.user_id).order_by(
                DeliveryCart.created_at.desc()).limit(1).all()

        self.delivery_cart_id = delivery_cart_data[0].id
        item_interface = self.ItemInterface(
                self.delivery_cart_id,
                self.params['type'],
                self.params['product_id'])
        return item_interface.delete_item()

    def delete(self):
        print(self.params['delivery_cart_clear'])
        if self.params['delivery_cart_clear'] is True:
            interfaces_map = {
                'normal':NormalItem,
                'cashback':CashbackItem
            }
            self.delivery_cart_clear(session)

        else:
            with session_scope() as session:
                delivery_cart_data = session.query(DeliveryCart).filter_by(
                        consumer_id=self.user_id).order_by(
                        DeliveryCart.created_at.desc()).limit(1).all()
                self.delivery_cart_id = delivery_cart_data[0].id
                item_interface = self.ItemInterface(
                    self.delivery_cart_id,
                    self.params['type'],
                    self.params['product_id'])
                return item_interface.delete_all_items(session)


    def createDeliveryCart(self, session);
        delivery_cart_data = DeliveryCart(consumer_id = self.user_id)
        session.add(delivery_cart_data)
        session.flush()
        self.delivery_cart_id = delivery_cart_data.id


    def delivery_cart_clear(self, session):
        with session_scope() as session:
            delivery_cart_data = session.query(DeliveryCart).filter_by(
                consumer_id=self.user_id).order_by(
                DeliveryCart.created_at.desc()).limit(1).all()
            self.delivery_cart_id = delivery_cart_data[0].id
            deliverycartlist = session.query(DeliveyCartList).filter_by(
                consumer_id=self.user_id).all()
            DeliverCartListForProcess = delivery_cart_schema_for_process.dump
                (deliverycartlist).data
            for item in deliverycartlist:
                ItemInterface = interfaces_map[item.type]
                item_interface = ItemInterface(
                    item.delivery_cart_id,
                    item.type,
                    item.product_id)
                item_interface.delete_all_items(session)
            return {'message': 'Items Removed - Delivery Cart Cleared' }


