from flask_restful import Api, Resource, fields, marshal_with, abort, marshal
from flask import request
from .models import *


api = Api(prefix='/api')


document_type_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
}


order_document_fields = {
    'id': fields.Integer,
    'order_id': fields.Integer,
    'current_status_id': fields.Integer,
    'file_path': fields.String,
    'uploaded_at': fields.DateTime,
    'submitted_at': fields.DateTime,
    'document_type': fields.List(fields.Nested(document_type_fields))
}


order_status_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
}


order_type_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'required_documents': fields.List(fields.Nested(document_type_fields))
}


registrar_fields = {
    'id': fields.Integer,
    'name': fields.String,
}


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


company_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'registrar': fields.List(fields.Nested(registrar_fields)),
    'orders': fields.List(fields.Nested(order_fields))
}


partners_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String,
    'phone': fields.String,
    'revenue_share': fields.Float,
    'orders': fields.List(fields.Nested(order_fields))
}


clients_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String,
    'phone': fields.String,
    'address': fields.String,
    'orders': fields.List(fields.Nested(order_fields))
}


# ===================================== Partners Resource ===================================== #

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
    
# ===================================== Clients Resource ===================================== #

class ClientResource(Resource):
    @marshal_with(clients_fields)
    def get(self):
        clients = db.session.query(Client).all()
        if not clients:
            abort(404, message="There are no clients. Create one first.")
        return clients
    
    def post(self):
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        address = data.get('address')
        
        if not name or not email or not phone or not address:
            abort(400, message="Name, Email, Phone, and Address are required fields.")
        
        try:
            new_client = Client(
                name=name,
                email=email,
                phone=phone,
                address=address
            )
            db.session.add(new_client)
            db.session.commit()
            return {'message': 'Client created successfully'}, 201
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while creating the client.{e}")


class ClientIdResource(Resource):
    @marshal_with(clients_fields)
    def get(self, client_id):
        client = db.session.query(Client).filter(Client.id == client_id).first()
        if not client:
            abort(404, message="Client with given ID doesn't exist.")
        return client
    
    def put(self, client_id):
        data = request.get_json()
        client = db.session.query(Client).filter(Client.id == client_id).first()
        if not client:
            abort(404, message="Client with given ID doesn't exist.")
        
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        address = data.get('address')

        if not name or not email or not phone or not address:
            abort(400, message="Name, Email, Phone, and Address are required fields.")
        
        try:
            if name and client.name != name:
                client.name = name
            if email and client.email != email:
                client.email = email
            if phone and client.phone != phone:
                client.phone = phone
            if address and client.address != address:
                client.address = address
            
            db.session.commit()
            return {'message': 'Client updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while updating the client.{e}")
            
    def delete(self, client_id):
        client = db.session.query(Client).filter(Client.id == client_id).first()
        if not client:
            abort(404, message="Client with given ID doesn't exist.")
        
        try:
            db.session.delete(client)
            db.session.commit()
            return {'message': 'Client deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while deleting the client.{e}")
            
            
# ===================================== Order Routes ===================================== #

class OrderResource(Resource):
    @marshal_with(order_fields)
    def get(self):
        orders = db.session.query(Order).all()
        if not orders:
            abort(404, message="There are no orders. Create one first.")
        return orders


# ===================================== Other Routes ===================================== #

class DocumentTypeResource(Resource):
    @marshal_with(document_type_fields)
    def get(self):
        document_types = db.session.query(DocumentType).all()
        # if not document_types:
        #     abort(404, message="There are no document types. Create one first.")
        return document_types
    
    def post(self):
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        
        if not name:
            abort(400, message="Name is a required field.")
        
        try:
            new_document_type = DocumentType(
                name=name,
                description=description
            )
            db.session.add(new_document_type)
            db.session.commit()
            return {'message': 'Document type created successfully'}, 201
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while creating the document type.{e}")


class DocumentTypeIdResource(Resource):
    @marshal_with(document_type_fields)
    def get(self, document_type_id):
        document_type = db.session.query(DocumentType).filter(DocumentType.id == document_type_id).first()
        if not document_type:
            abort(404, message="Document type with given ID doesn't exist.")
        return document_type
    
    def put(self, document_type_id):
        data = request.get_json()
        document_type = db.session.query(DocumentType).filter(DocumentType.id == document_type_id).first()
        if not document_type:
            abort(404, message="Document type with given ID doesn't exist.")
        
        name = data.get('name')
        description = data.get('description')

        if not name:
            abort(400, message="Name is a required field.")
        
        try:
            if name and document_type.name != name:
                document_type.name = name
            if description and document_type.description != description:
                document_type.description = description
            
            db.session.commit()
            return {'message': 'Document type updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while updating the document type.{e}")
            
            
    def delete(self, document_type_id):
        document_type = db.session.query(DocumentType).filter(DocumentType.id == document_type_id).first()
        if not document_type:
            abort(404, message="Document type with given ID doesn't exist.")
        
        try:
            db.session.delete(document_type)
            db.session.commit()
            return {'message': 'Document type deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while deleting the document type.{e}")



class OrderStatusResource(Resource):
    @marshal_with(order_status_fields)
    def get(self):
        order_statuses = db.session.query(OrderStatus).all()
        if not order_statuses:
            abort(404, message="There are no order statuses. Create one first.")
        return order_statuses
    
    def post(self):
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        
        if not name:
            abort(400, message="Name is a required field.")
        
        try:
            new_order_status = OrderStatus(
                name=name,
                description=description
            )
            db.session.add(new_order_status)
            db.session.commit()
            return {'message': 'Order status created successfully'}, 201
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while creating the order status.{e}")



class OrderTypesResource(Resource):
    @marshal_with(order_type_fields)
    def get(self):
        order_types = db.session.query(OrderType).all()
        return order_types
    
    def post(self):
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        required_documents_ids = data.get('required_documents_ids', [])
        
        if not name or not required_documents_ids:
            abort(400, message="Name and Documents are required.")
        
        try:
            new_order_type = OrderType(
                name=name,
                description=description
            )
            if required_documents_ids:
                document_types = db.session.query(DocumentType).filter(DocumentType.id.in_(required_documents_ids)).all()
                new_order_type.required_documents = document_types
            
            db.session.add(new_order_type)
            db.session.commit()
            return {'message': 'Order type created successfully'}, 201
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while creating the order type.{e}")
            
class OrderTypeIdResource(Resource):
    @marshal_with(order_type_fields)
    def get(self, order_type_id):
        order_type = db.session.query(OrderType).filter(OrderType.id == order_type_id).first()
        if not order_type:
            abort(404, message="Order type with given ID doesn't exist.")
        return order_type
    
    def put(self, order_type_id):
        data = request.get_json()
        order_type = db.session.query(OrderType).filter(OrderType.id == order_type_id).first()
        if not order_type:
            abort(404, message="Order type with given ID doesn't exist.")
        
        name = data.get('name')
        description = data.get('description')
        required_documents_ids = data.get('required_documents_ids', [])
        
        if not name or not required_documents_ids:
            abort(400, message="Name and Documents are required.")
        
        try:
            if name and order_type.name != name:
                order_type.name = name
            if description and order_type.description != description:
                order_type.description = description
            if required_documents_ids:
                print(required_documents_ids)
                document_types = db.session.query(DocumentType).filter(DocumentType.id.in_(required_documents_ids)).all()
                order_type.required_documents = document_types
            
            db.session.commit()
            return {'message': 'Order type updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while updating the order type.{e}")
    
    def delete(self, order_type_id):
        order_type = db.session.query(OrderType).filter(OrderType.id == order_type_id).first()
        if not order_type:
            abort(404, message="Order type with given ID doesn't exist.")
        
        try:
            db.session.delete(order_type)
            db.session.commit()
            return {'message': 'Order type deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while deleting the order type.{e}")



class CompanyResource(Resource):
    @marshal_with(company_fields)
    def get(self):
        companies = db.session.query(Company).all()
        if not companies:
            abort(404, message="There are no companies. Create one first.")
        return companies

    def post(self):
        data = request.get_json()
        name = data.get('name')
        registrar_id = data.get('registrar_id')
        
        if not name or not registrar_id:
            abort(400, message="Name and Registrar ID are required fields.")
        
        try:
            registrar = db.session.query(Registrar).filter(Registrar.id == registrar_id).first()
            if not registrar:
                abort(404, message="Registrar with given ID doesn't exist.")
            
            new_company = Company(
                name=name,
                registrar=registrar
            )
            db.session.add(new_company)
            db.session.commit()
            return {'message': 'Company created successfully'}, 201
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while creating the company.{e}")
            
            
            
class CompanyIdResource(Resource):
    @marshal_with(company_fields)
    def get(self, company_id):
        company = db.session.query(Company).filter(Company.id == company_id).first()
        if not company:
            abort(404, message="Company with given ID doesn't exist.")
        return company
    
    def put(self, company_id):
        data = request.get_json()
        company = db.session.query(Company).filter(Company.id == company_id).first()
        if not company:
            abort(404, message="Company with given ID doesn't exist.")
        
        name = data.get('name')
        registrar_id = data.get('registrar_id')

        if not name or not registrar_id:
            abort(400, message="Name and Registrar ID are required fields.")
        
        try:
            registrar = db.session.query(Registrar).filter(Registrar.id == registrar_id).first()
            if not registrar:
                abort(404, message="Registrar with given ID doesn't exist.")
            
            if name and company.name != name:
                company.name = name
            if registrar and company.registrar != registrar:
                company.registrar = registrar
            
            db.session.commit()
            return {'message': 'Company updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while updating the company.{e}")
            
    def delete(self, company_id):
        company = db.session.query(Company).filter(Company.id == company_id).first()
        if not company:
            abort(404, message="Company with given ID doesn't exist.")
        
        try:
            db.session.delete(company)
            db.session.commit()
            return {'message': 'Company deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while deleting the company.{e}")



class RegistrarResource(Resource):
    @marshal_with(registrar_fields)
    def get(self):
        registrars = db.session.query(Registrar).all()
        if not registrars:
            abort(404, message="There are no registrars. Create one first.")
        return registrars
    
    def post(self):
        data = request.get_json()
        name = data.get('name')
        
        if not name:
            abort(400, message="Name is a required field.")
        
        try:
            new_registrar = Registrar(
                name=name
            )
            db.session.add(new_registrar)
            db.session.commit()
            return {'message': 'Registrar created successfully'}, 201
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while creating the registrar.{e}")



# ===================================== Register Resources ===================================== #
api.add_resource(PartnerResource, '/partners')
api.add_resource(PartnerIdResouce, '/partners/<int:partner_id>')

api.add_resource(ClientResource, '/clients')
api.add_resource(ClientIdResource, '/clients/<int:client_id>')

api.add_resource(DocumentTypeResource, '/document-types')
api.add_resource(DocumentTypeIdResource, '/document-types/<int:document_type_id>')

api.add_resource(OrderStatusResource, '/order-status')

api.add_resource(OrderTypesResource, '/order-types')
api.add_resource(OrderTypeIdResource, '/order-types/<int:order_type_id>')

api.add_resource(CompanyResource, '/companies')
api.add_resource(CompanyIdResource, '/companies/<int:company_id>')

api.add_resource(RegistrarResource, '/registrars')