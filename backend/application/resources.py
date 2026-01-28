from flask_restful import Api, Resource, fields, marshal_with, abort, marshal
from flask import request
from .models import *


api = Api(prefix='/api')


order_fields = {
    'id': fields.Integer,
    'client_id': fields.Integer,
    'partner_id': fields.Integer,
    'company_id': fields.Integer,
    'date_created': fields.DateTime,
    'share_count': fields.Integer,
    'share_price': fields.Float,
    'fees': fields.Float,
    'base_charges': fields.Float,
    'payment_status': fields.Boolean,
    'settlement_status': fields.Boolean,
}

partners_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String,
    'phone': fields.String,
    'revenue_share': fields.Float,
    'orders': fields.List(fields.Nested(order_fields))
}


class PartnerResource(Resource):
    @marshal_with(partners_fields)
    def get(self):
        partner = db.session.query(Partner).all()
        if not partner:
            abort(404, message="There are no partners. Create one first.")
        return partner
    
    def post(self):
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        revenue_share = data.get('revenue_share')
        
        if not name or not email or not phone:
            abort(400, message="Name, Email, and Phone are required fields.")
        
        try:
            if revenue_share:
                new_partner = Partner(
                    name=name,
                    email=email,
                    phone=phone,
                    revenue_share=revenue_share
                )
            else:
                new_partner = Partner(
                    name=name,
                    email=email,
                    phone=phone
                )
            db.session.add(new_partner)
            db.session.commit()
            return {'message': 'Partner created successfully'}, 201
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while creating the partner.{e}")
        
        
    

class PartnerIdResouce(Resource):
    @marshal_with(partners_fields)
    def get(self, partner_id):
        partner = db.session.query(Partner).filter(Partner.id == partner_id).first()
        if not partner:
            abort(404, message="Partner with given ID doesn't exist.")
        return partner
    
    def put(self, partner_id):
        data = request.get_json()
        partner = db.session.query(Partner).filter(Partner.id == partner_id).first()
        if not partner:
            abort(404, message="Partner with given ID doesn't exist.")
        
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        revenue_share = float(data.get('revenue_share')) if data.get('revenue_share') is not None else None

        if not name or not email or not phone or revenue_share is None:
            abort(400, message="Name, Email, Phone, and Revenue Share are required fields.")
        
        try:
            if name and partner.name != name:
                partner.name = name
            if email and partner.email != email:
                partner.email = email
            if phone and partner.phone != phone:
                partner.phone = phone
            if revenue_share is not None and partner.revenue_share != revenue_share:
                partner.revenue_share = revenue_share
            
            db.session.commit()
            return {'message': 'Partner updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while updating the partner.{e}")
    
    def delete(self, partner_id):
        partner = db.session.query(Partner).filter(Partner.id == partner_id).first()
        if not partner:
            abort(404, message="Partner with given ID doesn't exist.")
        
        try:
            db.session.delete(partner)
            db.session.commit()
            return {'message': 'Partner deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while deleting the partner.{e}")
    
api.add_resource(PartnerResource, '/partners')
api.add_resource(PartnerIdResouce, '/partners/<int:partner_id>')