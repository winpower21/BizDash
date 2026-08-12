from flask_restful import Api, Resource, fields, marshal_with, abort
from flask import request, send_from_directory
from .config import UPLOAD_FOLDER, COMMENTS_FOLDER
from sqlalchemy import extract, func
from .models import *
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import calendar


api = Api(prefix='/api')

# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# os.makedirs(os.path.join(UPLOAD_FOLDER, 'comments'), exist_ok=True)


# ========================================= Marshal Fields ========================================= #

class AbsoluteFilePath(fields.Raw):
    """Resolves a relative path stored in the DB to an absolute path under UPLOAD_FOLDER."""
    def format(self, value):
        if not value:
            return None
        print(os.path.abspath(os.path.join(UPLOAD_FOLDER, value)))
        return os.path.abspath(os.path.join(UPLOAD_FOLDER, value))


document_type_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
}

document_status_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
}

order_document_fields = {
    'id': fields.Integer,
    'order_id': fields.Integer,
    'current_status_rel': fields.Nested(document_status_fields),
    'file_path': AbsoluteFilePath,
    'uploaded_at': fields.DateTime,
    'submitted_at': fields.DateTime,
    'document_type': fields.Nested(document_type_fields)
}

order_comment_fields = {
    'id': fields.Integer,
    'order_id': fields.Integer,
    'comment_text': fields.String,
    'date_created': fields.DateTime,
    'file_path': AbsoluteFilePath
}

order_status_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
}

activity_timeline_fields = {
    'id': fields.Integer,
    'notes': fields.String,
    'changed_at': fields.DateTime,
    'order_id': fields.Integer,
    'status': fields.Nested(order_status_fields)
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
    'email': fields.String,
    'address': fields.String,
    'link': fields.String,
}

order_part_fields = {
    'id': fields.Integer,
    'client_id': fields.Integer,
    'partner_id': fields.Integer,
    'company_id': fields.Integer,
    'date_created': fields.DateTime,
    'settlement_status': fields.Boolean,
}


company_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'registrar': fields.Nested(registrar_fields),
    'orders': fields.List(fields.Nested(order_part_fields))
}


partners_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String,
    'phone': fields.String,
    'revenue_share': fields.Float,
    'orders': fields.List(fields.Nested(order_part_fields))
}


clients_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String,
    'phone': fields.String,
    'address': fields.String,
    'orders': fields.List(fields.Nested(order_part_fields))
}

receipt_fields = {
    'id': fields.Integer,
    'amount': fields.Float,
    'description': fields.String,
    'date_created': fields.DateTime
}

expense_fields = {
    'id': fields.Integer,
    'amount': fields.Float,
    'description': fields.String,
    'date_created': fields.DateTime
}

settlement_fields = {
    'id': fields.Integer,
    'order_id': fields.Integer,
    'partner_id': fields.Integer,
    'partner_share': fields.Float,
    'self_share': fields.Float,
    'date': fields.DateTime,
}

order_fields = {
    'name': fields.String,
    'description': fields.String,
    'id': fields.Integer,
    'date_created': fields.DateTime,
    'share_count': fields.Integer,
    'share_price': fields.Float,
    'fees': fields.Float,
    'base_charges': fields.Float,
    'payment_status': fields.Boolean,
    'settlement_status': fields.Boolean,
    # Nested fields for detailed responses
    'client': fields.Nested(clients_fields),
    'partner': fields.Nested(partners_fields),
    'company': fields.Nested(company_fields),
    'order_type': fields.Nested(order_type_fields),
    'status': fields.Nested(order_status_fields),
    'documents': fields.List(fields.Nested(order_document_fields)),
    'receipts': fields.List(fields.Nested(receipt_fields)),
    'expenses': fields.List(fields.Nested(expense_fields)),
    'settlements': fields.Nested(settlement_fields)
}


task_fields = {
    'id': fields.Integer,
    'order_id': fields.Integer,
    'order': fields.Nested(order_fields),
    'title': fields.String,
    'description': fields.String,
    'due_date': fields.DateTime,
    'is_completed': fields.Boolean
}


# ========================================= Partners Resource ========================================= #

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
            abort(
                500, message=f"An error occurred while creating the partner.{e}")


class PartnerIdResouce(Resource):
    @marshal_with(partners_fields)
    def get(self, partner_id):
        partner = db.session.query(Partner).filter(
            Partner.id == partner_id).first()
        if not partner:
            abort(404, message="Partner with given ID doesn't exist.")
        return partner

    def put(self, partner_id):
        data = request.get_json()
        partner = db.session.query(Partner).filter(
            Partner.id == partner_id).first()
        if not partner:
            abort(404, message="Partner with given ID doesn't exist.")
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        revenue_share = float(data.get('revenue_share')) if data.get(
            'revenue_share') is not None else None
        if not name or not email or not phone or revenue_share is None:
            abort(
                400, message="Name, Email, Phone, and Revenue Share are required fields.")
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
            abort(
                500, message=f"An error occurred while updating the partner.{e}")

    def delete(self, partner_id):
        partner = db.session.query(Partner).filter(
            Partner.id == partner_id).first()
        if not partner:
            abort(404, message="Partner with given ID doesn't exist.")

        try:
            db.session.delete(partner)
            db.session.commit()
            return {'message': 'Partner deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(
                500, message=f"An error occurred while deleting the partner.{e}")


# ============================================= Clients Resource ============================================= #

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
            abort(
                500, message=f"An error occurred while creating the client.{e}")


class ClientIdResource(Resource):
    @marshal_with(clients_fields)
    def get(self, client_id):
        client = db.session.query(Client).filter(
            Client.id == client_id).first()
        if not client:
            abort(404, message="Client with given ID doesn't exist.")
        return client

    def put(self, client_id):
        data = request.get_json()
        client = db.session.query(Client).filter(
            Client.id == client_id).first()
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
            abort(
                500, message=f"An error occurred while updating the client.{e}")

    def delete(self, client_id):
        client = db.session.query(Client).filter(
            Client.id == client_id).first()
        if not client:
            abort(404, message="Client with given ID doesn't exist.")

        try:
            db.session.delete(client)
            db.session.commit()
            return {'message': 'Client deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(
                500, message=f"An error occurred while deleting the client.{e}")


# ============================================= Order Routes ============================================= #

class OrderResource(Resource):
    @marshal_with(order_fields)
    def get(self):
        orders = db.session.query(Order).order_by(
            Order.date_created.desc()).all()
        return orders

    def post(self):
        data = request.get_json()
        if not data:
            abort(400, message="Request body cannot be empty.")

        # Extract IDs from request
        name = data.get('name')
        description = data.get('description')
        client_id = data.get('client_id')
        partner_id = data.get('partner_id')
        order_type_id = data.get('order_type_id')
        company_id = data.get('company_id')
        status_id = data.get('status_id')
        share_count = data.get('share_count')
        share_price = data.get('share_price')
        fees = data.get('fees')
        base_charges = data.get('base_charges')

        # Validate required fields
        required_fields = {'name': name, 'description': description, 'client_id': client_id,
                           'partner_id': partner_id, 'order_type_id': order_type_id,
                           'company_id': company_id, 'status_id': status_id,
                           'share_count': share_count, 'share_price': share_price,
                           'fees': fees, 'base_charges': base_charges}
        for field, value in required_fields.items():
            if value is None:
                abort(400, message=f"'{field}' is a required field.")

        try:
            # Step 1: Create the main Order object
            new_order = Order(
                name=name, description=description,
                client_id=client_id, partner_id=partner_id, order_type_id=order_type_id,
                company_id=company_id, status_id=status_id, share_count=share_count,
                share_price=share_price, fees=fees, base_charges=base_charges
            )
            db.session.add(new_order)

            # Step 2: Create the initial OrderStatusHistory record
            initial_history = OrderStatusHistory(
                order=new_order, status_id=status_id, notes="Order created")
            db.session.add(initial_history)

            # Step 3: Create pending OrderDocument entries based on the OrderType
            order_type = db.session.query(
                OrderType).filter_by(id=order_type_id).first()
            pending_status = db.session.query(
                DocumentStatus).filter_by(name='Pending').first()

            if order_type and pending_status:
                for doc_type in order_type.required_documents:
                    order_doc = OrderDocument(
                        order=new_order,
                        document_type_id=doc_type.id,
                        current_status_id=pending_status.id
                    )
                    db.session.add(order_doc)

            # Commit the entire transaction
            db.session.commit()
            return {'message': 'Order created successfully', 'order_id': new_order.id}, 201

        except IntegrityError:
            db.session.rollback()
            abort(
                400, message="Integrity error: One of the provided IDs (client, partner, etc.) does not exist.")
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An unexpected error occurred: {e}")


class OrderIdResource(Resource):
    @marshal_with(order_fields)
    def get(self, order_id):
        order = db.session.query(Order).filter(Order.id == order_id).first()
        if not order:
            abort(404, message=f"Order with ID {order_id} not found.")
        return order

    def put(self, order_id):
        order = db.session.query(Order).filter(Order.id == order_id).first()
        if not order:
            abort(404, message=f"Order with ID {order_id} not found.")

        data = request.get_json()
        if not data:
            abort(400, message="Request body cannot be empty.")

        try:
            # Handle status change and potential settlement creation
            if 'status_id' in data and data['status_id'] != order.status_id:
                new_status_id = data['status_id']
                order.update_status(new_status_id=new_status_id)

                # Explicitly check for settlement creation condition
                new_status = db.session.query(
                    OrderStatus).filter_by(id=new_status_id).first()
                if new_status and new_status.name in ('Success', 'Failed'):
                    existing_settlement = db.session.query(
                        Settlement).filter_by(order_id=order.id).first()
                    if not existing_settlement:
                        settlement = order.create_settlement()
                        if settlement:
                            db.session.add(settlement)

            # Update other fields directly
            order.client_id = data.get('client_id', order.client_id)
            order.partner_id = data.get('partner_id', order.partner_id)
            order.order_type_id = data.get(
                'order_type_id', order.order_type_id)
            order.company_id = data.get('company_id', order.company_id)
            order.share_count = data.get('share_count', order.share_count)
            order.share_price = data.get('share_price', order.share_price)
            order.fees = data.get('fees', order.fees)
            order.base_charges = data.get('base_charges', order.base_charges)

            db.session.commit()
            return {'message': f'Order {order_id} updated successfully'}, 200
        except IntegrityError:
            db.session.rollback()
            abort(400, message="Integrity error: One of the provided IDs does not exist.")
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An unexpected error occurred: {e}")

    def delete(self, order_id):
        order = db.session.query(Order).filter(Order.id == order_id).first()
        if not order:
            abort(404, message=f"Order with ID {order_id} not found.")

        try:
            db.session.delete(order)
            db.session.commit()
            return {'message': f'Order {order_id} deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(
                500, message=f"An error occurred while deleting the order: {e}")


class OrderDocumentResource(Resource):
    def put(self, order_id):
        data = request.get_json()
        required_document_ids = data.get('required_document_ids', [None])
        order = db.session.query(Order).filter(Order.id == order_id).first()
        if not order:
            abort(404, message="Order not found.")
        doc_types = db.session.query(DocumentType).filter(
            DocumentType.id.in_(required_document_ids)
        ).all()
        if len(doc_types) != len(required_document_ids):
            return {'message': 'One or more Document Types not found'}, 404
        try:
            for document_type in doc_types:
                order_doc = OrderDocument(
                    order_id=order_id,
                    document_type_id=document_type.id,
                    current_status_id=db.session.query(
                        DocumentStatus).filter_by(name='Pending').first().id
                )
                db.session.add(order_doc)
            db.session.commit()
            return {'message': 'Order Documents added successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'An error occurred: {e}'}, 500


# ========================================= Document Types Routes ========================================= #

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
            abort(
                500, message=f"An error occurred while creating the document type.{e}")


class DocumentTypeIdResource(Resource):
    @marshal_with(document_type_fields)
    def get(self, document_type_id):
        document_type = db.session.query(DocumentType).filter(
            DocumentType.id == document_type_id).first()
        if not document_type:
            abort(404, message="Document type with given ID doesn't exist.")
        return document_type

    def put(self, document_type_id):
        data = request.get_json()
        document_type = db.session.query(DocumentType).filter(
            DocumentType.id == document_type_id).first()
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
            abort(
                500, message=f"An error occurred while updating the document type.{e}")

    def delete(self, document_type_id):
        document_type = db.session.query(DocumentType).filter(
            DocumentType.id == document_type_id).first()
        if not document_type:
            abort(404, message="Document type with given ID doesn't exist.")

        try:
            db.session.delete(document_type)
            db.session.commit()
            return {'message': 'Document type deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(
                500, message=f"An error occurred while deleting the document type.{e}")

# ========================================= Order Status Resource ========================================= #


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
            abort(
                500, message=f"An error occurred while creating the order status.{e}")

# ========================================= Order Types Resource ========================================= #


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
                document_types = db.session.query(DocumentType).filter(
                    DocumentType.id.in_(required_documents_ids)).all()
                new_order_type.required_documents = document_types

            db.session.add(new_order_type)
            db.session.commit()
            return {'message': 'Order type created successfully'}, 201
        except Exception as e:
            db.session.rollback()
            abort(
                500, message=f"An error occurred while creating the order type.{e}")


class OrderTypeIdResource(Resource):
    @marshal_with(order_type_fields)
    def get(self, order_type_id):
        order_type = db.session.query(OrderType).filter(
            OrderType.id == order_type_id).first()
        if not order_type:
            abort(404, message="Order type with given ID doesn't exist.")
        return order_type

    def put(self, order_type_id):
        data = request.get_json()
        order_type = db.session.query(OrderType).filter(
            OrderType.id == order_type_id).first()
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
                document_types = db.session.query(DocumentType).filter(
                    DocumentType.id.in_(required_documents_ids)).all()
                order_type.required_documents = document_types

            db.session.commit()
            return {'message': 'Order type updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(
                500, message=f"An error occurred while updating the order type.{e}")

    def delete(self, order_type_id):
        order_type = db.session.query(OrderType).filter(
            OrderType.id == order_type_id).first()
        if not order_type:
            abort(404, message="Order type with given ID doesn't exist.")

        try:
            db.session.delete(order_type)
            db.session.commit()
            return {'message': 'Order type deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(
                500, message=f"An error occurred while deleting the order type.{e}")


# ========================================= Company Resource ========================================= #

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
            registrar = db.session.query(Registrar).filter(
                Registrar.id == registrar_id).first()
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
            abort(
                500, message=f"An error occurred while creating the company.{e}")


class CompanyIdResource(Resource):
    @marshal_with(company_fields)
    def get(self, company_id):
        company = db.session.query(Company).filter(
            Company.id == company_id).first()
        if not company:
            abort(404, message="Company with given ID doesn't exist.")
        return company

    def put(self, company_id):
        data = request.get_json()
        company = db.session.query(Company).filter(
            Company.id == company_id).first()
        if not company:
            abort(404, message="Company with given ID doesn't exist.")

        name = data.get('name')
        registrar_id = data.get('registrar_id')

        if not name or not registrar_id:
            abort(400, message="Name and Registrar ID are required fields.")

        try:
            registrar = db.session.query(Registrar).filter(
                Registrar.id == registrar_id).first()
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
            abort(
                500, message=f"An error occurred while updating the company.{e}")

    def delete(self, company_id):
        company = db.session.query(Company).filter(
            Company.id == company_id).first()
        if not company:
            abort(404, message="Company with given ID doesn't exist.")

        try:
            db.session.delete(company)
            db.session.commit()
            return {'message': 'Company deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(
                500, message=f"An error occurred while deleting the company.{e}")


# ========================================= Registrar Resource ========================================= #

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
        email = data.get('email')
        address = data.get('address')
        link = data.get('link')

        if not name:
            abort(400, message="Name is a required field.")

        try:
            new_registrar = Registrar(
                name=name,
                email=email,
                address=address,
                link=link
            )
            db.session.add(new_registrar)
            db.session.commit()
            return {'message': 'Registrar created successfully'}, 201
        except Exception as e:
            db.session.rollback()
            abort(
                500, message=f"An error occurred while creating the registrar.{e}")


class RegistrarIdResource(Resource):
    @marshal_with(registrar_fields)
    def get(self, registrar_id):
        registrar = db.session.query(Registrar).filter(
            Registrar.id == registrar_id).first()
        if not registrar:
            abort(404, message="Registrar with given ID doesn't exist.")
        return registrar

    def put(self, registrar_id):
        data = request.get_json()
        registrar = db.session.query(Registrar).filter(
            Registrar.id == registrar_id).first()
        if not registrar:
            abort(404, message="Registrar with given ID doesn't exist.")

        name = data.get('name')
        email = data.get('email')
        address = data.get('address')
        link = data.get('link')

        if not name:
            abort(400, message="Name is a required field.")

        try:
            if name and registrar.name != name:
                registrar.name = name
            if email and registrar.email != email:
                registrar.email = email
            if address and registrar.address != address:
                registrar.address = address
            if link and registrar.link != link:
                registrar.link = link

            db.session.commit()
            return {'message': 'Registrar updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(
                500, message=f"An error occurred while updating the registrar.{e}")

    def delete(self, registrar_id):
        registrar = db.session.query(Registrar).filter(
            Registrar.id == registrar_id).first()
        if not registrar:
            abort(404, message="Registrar with given ID doesn't exist.")

        try:
            db.session.delete(registrar)
            db.session.commit()
            return {'message': 'Registrar deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(
                500, message=f"An error occurred while deleting the registrar.{e}")


# ========================================= Order Docuement Resource ========================================= #

class OrderDocumentUploadResource(Resource):
    def post(self, order_id):
        order = db.session.query(Order).filter(Order.id == order_id).first()
        if not order:
            abort(404, message="Order not found.")

        if 'file' not in request.files:
            abort(400, message="No file part in the request.")
        file = request.files['file']
        doc_type_id = request.form.get('document_type_id')
        if not doc_type_id:
            abort(400, message="document_type_id is required.")

        # Create the directory structure
        client_name = order.client.name.replace(" ", "_").lower()
        order_upload_dir = os.path.join(UPLOAD_FOLDER, client_name, str(order.id))
        os.makedirs(order_upload_dir, exist_ok=True)

        # Create the new filename
        doc_type = db.session.query(DocumentType).filter(DocumentType.id == doc_type_id).first()
        if not doc_type:
            abort(404, message="Document type not found.")
        
        original_extension = os.path.splitext(file.filename)[1]
        new_filename = f"{doc_type.name.lower().replace(' ', '_')}{original_extension}"
        
        # Save the file
        file_path = os.path.join(order_upload_dir, new_filename)
        file.save(file_path)
        
        relative_path = os.path.join(client_name, str(order.id), new_filename)

        order_doc = db.session.query(OrderDocument).filter_by(
            order_id=order_id, document_type_id=doc_type_id).first()
        received_status = db.session.query(
            DocumentStatus).filter_by(name='Received').first()
        if not received_status:
            abort(
                500, message="DocumentStatus 'Received' not found. Please seed the database.")

        if order_doc.file_path:
            existing_file_path = os.path.join(
                UPLOAD_FOLDER, order_doc.file_path)
            if os.path.exists(existing_file_path):
                try:
                    os.remove(existing_file_path)
                except Exception as E:
                    return abort(500, message=f"Error deleting existing file.: {E}")

        if not order_doc:
            order_doc = OrderDocument(
                order_id=order_id, document_type_id=doc_type_id, current_status_id=received_status.id)
            db.session.add(order_doc)

        order_doc.uploaded_at = datetime.utcnow()
        order_doc.file_path = relative_path
        order_doc.current_status_id = received_status.id

        db.session.commit()
        return {'message': 'File uploaded and document updated successfully.'}, 200


class OrderDocumentIdResource(Resource):
    def delete(self, order_id, document_id):
        order_doc = db.session.query(OrderDocument).filter_by(
            order_id=order_id, id=document_id).first()

        if not order_doc:
            abort(404, message="Document not found for this order.")

        if order_doc.file_path:
            try:
                # Construct the full path to the file
                full_file_path = os.path.join(UPLOAD_FOLDER, order_doc.file_path)
                if os.path.exists(full_file_path):
                    os.remove(full_file_path)
            except Exception as e:
                # Log the error but don't abort
                print(f"Error deleting file {order_doc.file_path}: {e}")

        try:
            # Reset the document's state
            pending_status = db.session.query(DocumentStatus).filter_by(name='Pending').first()
            if not pending_status:
                abort(500, message="DocumentStatus 'Pending' not found.")

            order_doc.file_path = None
            order_doc.uploaded_at = None
            order_doc.current_status_id = pending_status.id

            db.session.commit()
            return {'message': 'Document deleted and reset successfully.'}, 200
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while deleting the document: {e}")


# ========================================= Receipts/Expensees/Settlement Resource ========================================= #

class ReceiptResource(Resource):
    def post(self, order_id):
        data = request.get_json()
        order = db.session.query(Order).filter(Order.id == order_id).first()
        if not order:
            abort(404, message="Order not found.")
        amount = data.get('amount')
        description = data.get('description')
        if not amount or not description:
            abort(400, message="Amount and Description are required fields.")
        new_receipt = Receipt(
            order_id=order_id,
            amount=amount,
            description=description
        )
        db.session.add(new_receipt)
        db.session.commit()
        order.validate_payment_status()
        return {'message': 'Receipt added successfully'}, 201


class ReceiptIdResource(Resource):
    def put(self, receipt_id, order_id):
        receipt = db.session.query(Receipt).filter(
            Receipt.id == receipt_id).first()
        if not receipt:
            abort(404, message="Receipt not found.")

        data = request.get_json()
        amount = data.get('amount')
        description = data.get('description')

        if not amount or not description:
            abort(400, message="Amount and Description are required fields.")

        receipt.amount = amount
        receipt.description = description
        db.session.commit()
        return {'message': 'Receipt updated successfully'}, 200

    def delete(self, receipt_id, order_id):
        receipt = db.session.query(Receipt).filter(
            Receipt.id == receipt_id).first()
        if not receipt:
            abort(404, message="Receipt not found.")
        db.session.delete(receipt)
        db.session.commit()
        return {'message': 'Receipt deleted successfully'}, 200


class ExpenseResource(Resource):
    def post(self, order_id):
        data = request.get_json()
        new_expense = Expense(
            order_id=order_id,
            amount=data.get('amount'),
            description=data.get('description')
        )
        db.session.add(new_expense)
        db.session.commit()
        return {'message': 'Expense added successfully'}, 201


class ExpenseIdResource(Resource):
    def put(self, expense_id, order_id):
        expense = db.session.query(Expense).filter(
            Expense.id == expense_id).first()
        if not expense:
            abort(404, message="Expense not found.")
        data = request.get_json()
        amount = data.get('amount')
        description = data.get('description')

        if not amount or not description:
            abort(400, message="Amount and Description are required fields.")

        expense.amount = amount
        expense.description = description
        db.session.commit()
        return {'message': 'Expense updated successfully'}, 200

    def delete(self, expense_id, order_id):
        expense = db.session.query(Expense).filter(
            Expense.id == expense_id).first()
        if not expense:
            abort(404, message="Expense not found.")
        db.session.delete(expense)
        db.session.commit()
        return {'message': 'Expense deleted successfully'}, 200


class OrderSettlementResource(Resource):
    def post(self, order_id):
        order = db.session.query(Order).filter(Order.id == order_id).first()
        if not order:
            abort(404, message="Order not found.")

        if order.status.name not in ['Success', 'Failed']:
            abort(
                400, message="Order status must be 'Success' or 'Failed' to generate a settlement.")

        if order.payment_status == False:
            abort(
                400, message="Order payment status must be 'Paid' to generate a settlement.")

        order.settlement_status = True
        db.session.commit()
        return {'message': 'Settlement created successfully.'}, 201


class RevenueSummaryResource(Resource):
    def get(self):
        # Realized Revenue (based on completed settlements)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)

        realized_30_days = db.session.query(db.func.sum(Settlement.self_share)).filter(
            Settlement.date >= thirty_days_ago).scalar() or 0.0
        realized_90_days = db.session.query(db.func.sum(Settlement.self_share)).filter(
            Settlement.date >= ninety_days_ago).scalar() or 0.0

        # Unrealized Revenue (from orders that are not fully paid)
        unrealized = db.session.query(db.func.sum(Order.fees)).filter(
            Order.payment_status == False).scalar() or 0.0

        return {
            'realized_revenue_30_days': realized_30_days,
            'realized_revenue_90_days': realized_90_days,
            'unrealized_revenue': unrealized
        }


class ActivityTimelineResource(Resource):
    @marshal_with(activity_timeline_fields)
    def get(self):
        # Get the 10 most recent order status changes
        timeline_events = db.session.query(OrderStatusHistory).order_by(
            OrderStatusHistory.changed_at.desc()).limit(10).all()
        return timeline_events


# ========================================= Comments Resources ========================================= #

class OrderCommentsResource(Resource):
    @marshal_with(order_comment_fields)
    def get(self, order_id):
        order = db.session.query(Order).filter_by(id=order_id).first()
        if not order:
            abort(404, message='Order does not exist')
        comments = db.session.query(Comment).filter_by(
            order_id=order_id).order_by(Comment.date_created.desc()).all()
        if not comments:
            abort(404, message='No comments for this order')
        return comments

    def post(self, order_id):
        order = db.session.query(Order).filter_by(id=order_id).first()
        if not order:
            abort(404, message='Order does not exist')
        comment_text = request.form.get('comment_text')
        file_path = None

        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                # Create order-specific comments directory
                order_comments_dir = os.path.join(COMMENTS_FOLDER, str(order_id))
                os.makedirs(order_comments_dir, exist_ok=True)
                
                filename = secure_filename(file.filename)
                full_file_path = os.path.join(order_comments_dir, filename)
                file.save(full_file_path)
                file_path = os.path.join('comments', str(order_id), filename)

        comment = Comment(comment_text=comment_text, file_path=file_path, order_id=order_id)
        try:
            db.session.add(comment)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            abort(500, message=f'Error creating comment: {e}')
        return {'message': 'Comment created successfully'}, 200


class OrderCommentIdResource(Resource):
    @marshal_with(order_comment_fields)
    def get(self, order_id, comment_id):
        order = db.session.query(Order).filter_by(id=order_id).first()
        comment = db.session.query(Comment).filter_by(id=comment_id).first()
        if not order or not comment:
            abort(404, message='Comment does not exist')

        return comment

    def put(self, order_id, comment_id):
        order = db.session.query(Order).filter_by(id=order_id).first()
        comment = db.session.query(Comment).filter_by(id=comment_id).first()
        if not order or not comment:
            abort(404, message='Comment does not exist')

        comment_text = request.form.get('comment_text')
        
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename:
                # Delete old file if it exists
                if comment.file_path:
                    try:
                        full_old_file_path = os.path.join(UPLOAD_FOLDER, comment.file_path)
                        if os.path.exists(full_old_file_path):
                            os.remove(full_old_file_path)
                    except OSError as e:
                        print(f"Error deleting old comment file {full_old_file_path}: {e}")
                
                # Create order-specific comments directory
                order_comments_dir = os.path.join(UPLOAD_FOLDER, 'comments', str(order_id))
                os.makedirs(order_comments_dir, exist_ok=True)

                filename = secure_filename(file.filename)
                full_new_file_path = os.path.join(order_comments_dir, filename)
                file.save(full_new_file_path)
                comment.file_path = os.path.join('comments', str(order_id), filename)
            elif comment.file_path and request.form.get('clear_file') == 'true': # Option to clear existing file
                try:
                    full_old_file_path = os.path.join(UPLOAD_FOLDER, comment.file_path)
                    if os.path.exists(full_old_file_path):
                        os.remove(full_old_file_path)
                    comment.file_path = None
                except OSError as e:
                    print(f"Error deleting old comment file {full_old_file_path}: {e}")
        elif request.form.get('clear_file') == 'true' and comment.file_path:
            # If no new file is uploaded but clear_file is true, just remove the old file
            try:
                full_old_file_path = os.path.join(UPLOAD_FOLDER, comment.file_path)
                if os.path.exists(full_old_file_path):
                    os.remove(full_old_file_path)
                comment.file_path = None
            except OSError as e:
                print(f"Error deleting old comment file {full_old_file_path}: {e}")

        if comment_text is not None:
            comment.comment_text = comment_text

        db.session.commit()
        return {'message': 'Comment edited successfully'}, 200

    def delete(self, order_id, comment_id):
        order = db.session.query(Order).filter_by(id=order_id).first()
        comment = db.session.query(Comment).filter_by(id=comment_id).first()
        if not order or not comment:
            abort(404, message='Comment does not exist')

        file_path_to_delete = comment.file_path

        try:
            db.session.delete(comment)
            db.session.commit()
            if file_path_to_delete:
                full_file_path = os.path.join(UPLOAD_FOLDER, file_path_to_delete)
                if os.path.exists(full_file_path):
                    os.remove(full_file_path)
            return {'message': 'Comment deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(500, message=f'Error deleting message: {e}')

# ========================================= Task Resources ========================================= #


class AllTasksResource(Resource):
    @marshal_with(task_fields)
    def get(self):
        tasks = db.session.query(Task).order_by(Task.due_date.asc()).all()
        return tasks


class TaskResource(Resource):
    @marshal_with(task_fields)
    def get(self, order_id):
        tasks = db.session.query(Task).filter_by(
            order_id=order_id).order_by(Task.due_date.asc()).all()
        return tasks

    def post(self, order_id):
        data = request.get_json()
        if not data or not data.get('title'):
            abort(400, message="Title is a required field.")

        # Ensure the parent order exists
        order = db.session.query(Order).filter_by(id=order_id).first()
        if not order:
            abort(404, message=f"Order with ID {order_id} not found.")

        title = data.get('title')
        description = data.get('description')
        due_date = data.get('due_date')

        print(datetime.fromisoformat(due_date))

        if not title or not due_date:
            abort(400, message="Title and Due Date are required fields.")

        new_task = Task(
            order_id=order_id,
            title=title,
            description=description,
            due_date=datetime.fromisoformat(due_date) if due_date else None
        )
        db.session.add(new_task)
        db.session.commit()
        return {'message': 'Task created successfully'}, 201


class TaskIdResource(Resource):
    @marshal_with(task_fields)
    def get(self, task_id):
        task = db.session.query(Task).filter_by(id=task_id).first()
        if not task:
            abort(404, message=f"Task with ID {task_id} not found.")
        return task

    @marshal_with(task_fields)
    def put(self, task_id):
        task = db.session.query(Task).filter_by(id=task_id).first()
        if not task:
            abort(404, message=f"Task with ID {task_id} not found.")

        data = request.get_json()
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.due_date = datetime.fromisoformat(
            data.get('due_date')) if data.get('due_date') else task.due_date
        if 'is_completed' in data:
            task.is_completed = data.get('is_completed')

        db.session.commit()
        return task

    def delete(self, task_id):
        task = db.session.query(Task).filter_by(id=task_id).first()
        if not task:
            abort(404, message=f"Task with ID {task_id} not found.")

        db.session.delete(task)
        db.session.commit()
        return {'message': 'Task deleted successfully'}, 200

# ========================================= Document Status Resouce ========================================= #


class DocumentStatusResource(Resource):
    @marshal_with(document_status_fields)
    def get(self):
        document_statuses = db.session.query(DocumentStatus).all()
        return document_statuses


class UpdateDocumentStatusResource(Resource):
    def put(self, order_id):
        data = request.get_json()
        if not data or not isinstance(data, list):
            abort(
                400, message="Invalid request body. Expected a list of document statuses.")

        try:
            for item in data:
                doc_id = item.get('document_id')
                status_id = item.get('status_id')
                if not doc_id or not status_id:
                    abort(
                        400, message="Each item must contain 'document_id' and 'status_id'.")

                order_doc = db.session.query(OrderDocument).filter_by(
                    id=doc_id, order_id=order_id).first()
                if not order_doc:
                    abort(
                        404, message=f"Document with ID {doc_id} not found for this order.")

                order_doc.current_status_id = status_id

            db.session.commit()
            return {'message': 'Document statuses updated successfully.'}, 200
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An unexpected error occurred: {e}")

# ========================================= Revenue Reports Resource ========================================= #


class RevenueReportsResource(Resource):
    def get(self):
        try:
            year = int(request.args.get('year', datetime.utcnow().year))
            print(year)
        except (ValueError, TypeError):
            year = datetime.utcnow().year

        now = datetime.utcnow()
        is_current_year = (year == now.year)

        # =================== 1. Date Ranges ===================
        start_of_year = datetime(year, 1, 1)
        end_of_year = datetime(year, 12, 31, 23, 59, 59)

        start_of_month = now.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0)
        month_days = calendar.monthrange(now.year, now.month)[1]
        end_of_month = start_of_month.replace(
            day=month_days, hour=23, minute=59, second=59)

        quarter_starts = [datetime(year, 1, 1), datetime(
            year, 4, 1), datetime(year, 7, 1), datetime(year, 10, 1)]
        current_quarter_start = quarter_starts[(now.month - 1) // 3]
        next_quarter_start_month = current_quarter_start.month + 3
        if next_quarter_start_month > 12:
            next_quarter_start = datetime(year + 1, 1, 1)
        else:
            next_quarter_start = datetime(year, next_quarter_start_month, 1)
        current_quarter_end = next_quarter_start - timedelta(seconds=1)

        # =================== 2. Realized Revenue Calculations ===================
        def get_realized_revenue(start_date, end_date):
            result = db.session.query(
                func.sum(Settlement.self_share).label('total_self_share'),
                func.sum(Settlement.partner_share).label('total_partner_share')
            ).filter(Settlement.date.between(start_date, end_date)).first()

            self_share = result.total_self_share or 0.0
            partner_share = result.total_partner_share or 0.0
            return {
                "total": self_share + partner_share,
                "self_share": self_share,
                "partner_share": partner_share
            }

        realized_revenue = {
            "year": get_realized_revenue(start_of_year, end_of_year)
        }
        if is_current_year:
            realized_revenue["month"] = get_realized_revenue(
                start_of_month, end_of_month)
            realized_revenue["quarter"] = get_realized_revenue(
                current_quarter_start, current_quarter_end)
        else:
            realized_revenue["month"] = None
            realized_revenue["quarter"] = None

        # =================== 3. Unrealized Revenue (Year) ===================
        unrealized_revenue_year = db.session.query(
            func.sum(Order.fees)
        ).filter(
            Order.payment_status == False,
            extract('year', Order.date_created) == year
        ).scalar() or 0.0

        total_revenue_year = realized_revenue["year"]["total"] + \
            unrealized_revenue_year

        # =================== 4. Average Order Completion Duration ===================
        received_status = db.session.query(
            OrderStatus).filter_by(name='Received').first()
        success_status = db.session.query(
            OrderStatus).filter_by(name='Success').first()

        avg_duration_seconds = None
        if received_status and success_status:
            # Subquery to find the earliest 'Received' timestamp for each order
            received_times = db.session.query(
                OrderStatusHistory.order_id,
                func.min(OrderStatusHistory.changed_at).label('received_at')
            ).filter(OrderStatusHistory.status_id == received_status.id).group_by(OrderStatusHistory.order_id).subquery()

            # Subquery to find the latest 'Success' timestamp for each order
            success_times = db.session.query(
                OrderStatusHistory.order_id,
                func.max(OrderStatusHistory.changed_at).label('success_at')
            ).filter(
                OrderStatusHistory.status_id == success_status.id,
                extract('year', OrderStatusHistory.changed_at) == year
            ).group_by(OrderStatusHistory.order_id).subquery()

            # Join the subqueries and calculate the average duration
            duration_query = db.session.query(
                func.avg(func.julianday(success_times.c.success_at) -
                         func.julianday(received_times.c.received_at))
            ).join(
                received_times, received_times.c.order_id == success_times.c.order_id
            ).first()

            if duration_query and duration_query[0]:
                # Convert days to seconds
                avg_duration_seconds = duration_query[0] * 86400

        # =================== 5. Average Order Value ===================
        avg_values = db.session.query(
            func.avg(Order.fees).label('avg_fees'),
            func.avg(Order.share_count *
                     Order.share_price).label('avg_order_value')
        ).filter(extract('year', Order.date_created) == year).first()

        average_order_value = {
            "fees": avg_values.avg_fees or 0.0,
            "order_value": avg_values.avg_order_value or 0.0
        }

        # =================== 6. Revenue Share by Partner ===================
        partner_revenue = db.session.query(
            Partner.id,
            Partner.name,
            func.sum(Settlement.partner_share).label('total_share')
        ).join(
            Settlement, Partner.id == Settlement.partner_id
        ).filter(
            extract('year', Settlement.date) == year
        ).group_by(Partner.id, Partner.name).order_by(func.sum(Settlement.partner_share).desc()).all()

        partner_revenue_share = [
            {"partner_id": p.id, "partner_name": p.name,
                "total_share": p.total_share or 0.0}
            for p in partner_revenue
        ]

        # =================== 7. Assemble Response ===================
        return {
            "selected_year": year,
            "is_current_year": is_current_year,
            "realized_revenue": realized_revenue,
            "unrealized_revenue_year": unrealized_revenue_year,
            "total_revenue_year": total_revenue_year,
            "average_order_completion_duration_seconds": avg_duration_seconds,
            "average_order_value": average_order_value,
            "partner_revenue_share": partner_revenue_share
        }

# ========================================= File Downloads Resources ========================================= #


class DownloadFileResource(Resource):
    def get(self, filename):
        return send_from_directory(UPLOAD_FOLDER, filename)

# ========================================= Register Resources ========================================= #


api.add_resource(RevenueSummaryResource, '/dashboard/revenue-summary')
api.add_resource(ActivityTimelineResource, '/dashboard/activity-timeline')

api.add_resource(PartnerResource, '/partners')
api.add_resource(PartnerIdResouce, '/partners/<int:partner_id>')

api.add_resource(ClientResource, '/clients')
api.add_resource(ClientIdResource, '/clients/<int:client_id>')

api.add_resource(DocumentTypeResource, '/document-types')
api.add_resource(DocumentTypeIdResource,
                 '/document-types/<int:document_type_id>')

api.add_resource(OrderResource, '/orders')
api.add_resource(OrderIdResource, '/orders/<int:order_id>')
api.add_resource(OrderStatusResource, '/order-status')
api.add_resource(OrderTypesResource, '/order-types')
api.add_resource(OrderTypeIdResource, '/order-types/<int:order_type_id>')
api.add_resource(OrderDocumentResource, '/orders/<int:order_id>/add_documents')
api.add_resource(OrderCommentsResource, '/orders/<int:order_id>/comments')
api.add_resource(OrderCommentIdResource,
                 '/orders/<int:order_id>/comments/<int:comment_id>')
api.add_resource(OrderDocumentUploadResource,
                 '/orders/<int:order_id>/documents')
api.add_resource(OrderDocumentIdResource,
                 '/orders/<int:order_id>/documents/<int:document_id>')
api.add_resource(OrderSettlementResource, '/orders/<int:order_id>/settle')

api.add_resource(CompanyResource, '/companies')
api.add_resource(CompanyIdResource, '/companies/<int:company_id>')

api.add_resource(RegistrarResource, '/registrars')
api.add_resource(RegistrarIdResource, '/registrars/<int:registrar_id>')

api.add_resource(ReceiptResource, '/orders/<int:order_id>/receipts')
api.add_resource(ReceiptIdResource,
                 '/orders/<int:order_id>/receipts/<int:receipt_id>')

api.add_resource(ExpenseResource, '/orders/<int:order_id>/expenses')
api.add_resource(ExpenseIdResource,
                 '/orders/<int:order_id>/expenses/<int:expense_id>')

api.add_resource(RevenueReportsResource, '/reports/revenue-stats')

api.add_resource(DocumentStatusResource, '/document-status')
api.add_resource(UpdateDocumentStatusResource,
                 '/orders/<int:order_id>/documents/statuses')

api.add_resource(AllTasksResource, '/tasks')
api.add_resource(TaskResource, '/orders/<int:order_id>/tasks')
api.add_resource(TaskIdResource, '/tasks/<int:task_id>')

api.add_resource(DownloadFileResource, '/uploads/<path:filename>')
