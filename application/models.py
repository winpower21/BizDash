from sqlalchemy import CheckConstraint, event
from sqlalchemy.orm.attributes import get_history
from .database import db, whooshee
import os
from datetime import datetime

@whooshee.register_model('name', 'email', 'phone')
class Partner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.now())
    order_id = db.relationship('Order', backref='partner', lazy=True)
    revenue_share = db.Column(db.Float, nullable=True, default=0.5)

    def __repr__(self):
        return f'<Partner {self.name}>'

@whooshee.register_model('name', 'email', 'phone', 'address')
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    address = db.Column(db.String(200), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.now())
    orders = db.relationship('Order', backref='client_rel', lazy=True)

    def __repr__(self):
        return f'<Client {self.name}>'

# Association Table (M2M between OrderType and DocumentType)
order_docs_m2m = db.Table('order_docs_m2m', # Renamed slightly to avoid confusion with the OrderDocument model
    db.Column('order_type_id', db.Integer, db.ForeignKey('order_type.id', ondelete="CASCADE"), primary_key=True),
    db.Column('document_type_id', db.Integer, db.ForeignKey('document_type.id', ondelete="RESTRICT"), primary_key=True)
)

@whooshee.register_model('name', 'description')
class OrderType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    documents = db.relationship('DocumentType', secondary=order_docs_m2m, backref='order_types')
    
    def __repr__(self):
        return f'<OrderType {self.name}>'

class DocumentType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<DocumentType {self.name}>'

@whooshee.register_model('name')
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    registrar = db.Column(db.Integer, db.ForeignKey('registrar.id', ondelete="SET NULL"), nullable=False)
    orders = db.relationship('Order', backref='company_rel', lazy=True)

    def __repr__(self):
        return f'<Company {self.name}>'

@whooshee.register_model('name')
class Registrar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    orders = db.relationship('Order', backref='registrar_rel', lazy=True)
    company = db.relationship('Company', backref='registrar_rel', lazy=True)
    def __repr__(self):
        return f'<Registrar {self.name}>'
    
class OrderStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<OrderStatus {self.name}>'


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client = db.Column(db.Integer, db.ForeignKey('client.id', ondelete="SET NULL"), nullable=False)
    partner = db.Column(db.Integer, db.ForeignKey('partner.id', ondelete="SET NULL"), nullable=False)
    order_type = db.Column(db.Integer, db.ForeignKey('order_type.id', ondelete="SET NULL"), nullable=False)
    company = db.Column(db.Integer, db.ForeignKey('company.id', ondelete="SET NULL"), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())
    status = db.Column(db.Integer, db.ForeignKey('order_status.id', ondelete="SET NULL"), nullable=False)
    fees = db.Column(db.Float, nullable=False, default=0.0)
    base_charges = db.Column(db.Float, nullable=False, default=0.0)
    payment_status = db.Column(db.Boolean, default=False)
    settlement_status = db.Column(db.Boolean, default=False)
    documents = db.relationship('OrderDocument', backref='order_ref', lazy=True, cascade="all, delete-orphan")
    document_sent_status = db.relationship('SentOrderDocumentStatus', backref='order_ref', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Order {self.order_number}>'
    

class OrderDocument(db.Model):
    __tablename__ = 'order_documents'
    id = db.Column(db.Integer, primary_key=True)
    
    # Link to Order
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete="CASCADE"), nullable=False)
    # Link to DocumentType
    document_type_id = db.Column(db.Integer, db.ForeignKey('document_type.id'), nullable=False)
    # Optional: Relationship to access the type details (name, etc.)
    document_type = db.relationship('DocumentType')
    
    file_path = db.Column(db.String(255))
    status = db.Column(db.String(50), default='pending')
    uploaded_at = db.Column(db.DateTime)


# --- Event Listener (Correct) ---
@event.listens_for(OrderDocument, 'before_update')
def update_upload_date(mapper, connection, target):
    history = get_history(target, 'file_path')
    if history.has_changes():
        if target.file_path is not None:
            target.uploaded_at = datetime.utcnow() # Ensure this matches column name 'uploaded_at'
            # add status modification
            

class DocumentStatusType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<DocumentStatusType {self.name}>'

class SentOrderDocumentStatus(db.Model):
    __tablename__ = 'sent_order_document_status'
    id = db.Column(db.Integer, primary_key=True)
    order = db.Column(db.Integer, db.ForeignKey('order.id', ondelete="CASCADE"), nullable=False)
    document = db.Column(db.Integer, db.ForeignKey('order_document.id', ondelete="RESTRICT"), nullable=False)
    status = db.Column(db.Integer, db.ForeignKey('document_status_type.id', ondelete="RESTRICT"), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now())


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete="CASCADE"), nullable=False)
    comment_text = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())
    file_path = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Comment {self.id} on Order {self.order_id}>'

class Receipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete="CASCADE"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return f'<Receipt {self.id} for Order {self.order_id}>'
    
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete="CASCADE"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return f'<Expense {self.id} for Order {self.order_id}>'
    
class Settlement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete="CASCADE"), nullable=False)
    partner_id = db.Column(db.Integer, db.ForeignKey('partner.id', ondelete="CASCADE"), nullable=False)
    partner_amount = db.Column(db.Float, nullable=False)
    self_amount = db.Column(db.Float, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return f'<Settlement {self.id} for Partner {self.partner_id}>'
    
@event.listens_for(Order, 'after_update')
def before_order_complete(mapper, connection, target):
    history = get_history(target, 'status')
    if history.has_changes():
        if target.status.name == 'Completed':
            # Logic to trigger settlement calculation
            fees = target.fees
            total_receipts = sum(receipt.amount for receipt in target.receipts)
            total_expenses = sum(expense.amount for expense in target.expenses)
            partner_amount = ((fees - total_expenses)) * target.partner.revenue_share
            self_amount = (fees - total_expenses) * (1-target.partner.revenue_share)
            settlement = Settlement(
                partner_id=target.partner.id,
                order_id=target.id,
                partner_amount=partner_amount,
                self_amount=self_amount
            )
            db.session.add(settlement)
            db.session.commit()
        elif target.status.name == 'Failed':
            fees = target.fees
            total_expenses = sum(expense.amount for expense in target.expenses)
            partner_amount = ((target.base_charges - total_expenses) if (total_expenses < target.base_charges) else target.base_charges) * target.partner.revenue_share
            self_amount = (0.0 if (total_expenses < target.base_charges) else (target.base_charges - total_expenses) * (1 - target.partner.revenue_share)) 
            settlement = Settlement(
                partner_id=target.partner.id,
                order_id=target.id,
                partner_amount=partner_amount,
                self_amount=self_amount
            )
            db.session.add(settlement)
            db.session.commit()
            
@event.listens_for(Order, 'after_update')
def update_settlement_status(mapper, connection, target):
    history = get_history(target, 'payment_status')
    if history.has_changes():
        if target.payment_status:
            target.settlement_status = True
            db.session.commit()
        else:
            pass