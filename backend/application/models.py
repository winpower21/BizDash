from sqlalchemy import CheckConstraint, event, Index
from sqlalchemy.orm import validates
from sqlalchemy.orm.attributes import get_history
from .database import db, whooshee
import os
import re
from datetime import datetime


@whooshee.register_model('name', 'email', 'phone')
class Partner(db.Model):
    __tablename__ = 'partner'
    __table_args__ = (
        Index('idx_partner_email', 'email'),
        CheckConstraint('revenue_share >= 0 AND revenue_share <= 1', name='check_revenue_share_range'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    revenue_share = db.Column(db.Float, nullable=False, default=0.5)
    
    # Relationships
    orders = db.relationship('Order', back_populates='partner', lazy=True)
    settlements = db.relationship('Settlement', back_populates='partner', lazy=True)

    @validates('email')
    def validate_email(self, key, email):
        if not email or '@' not in email:
            raise ValueError("Invalid email address")
        return email.lower().strip()
    
    @validates('revenue_share')
    def validate_revenue_share(self, key, value):
        if not (0 < value < 1):
            raise ValueError("Revenue share must be between 0 and 1")
        return value

    def __repr__(self):
        return f'<Partner {self.name}>'


@whooshee.register_model('name', 'email', 'phone', 'address')
class Client(db.Model):
    __tablename__ = 'client'
    __table_args__ = (
        Index('idx_client_email', 'email'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    address = db.Column(db.String(200), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', back_populates='client', lazy=True)

    @validates('email')
    def validate_email(self, key, email):
        if not email or '@' not in email:
            raise ValueError("Invalid email address")
        return email.lower().strip()

    def __repr__(self):
        return f'<Client {self.name}>'


# Association Table (M2M between OrderType and DocumentType)
order_type_documents = db.Table('order_type_documents',
    db.Column('order_type_id', db.Integer, db.ForeignKey('order_type.id', ondelete="CASCADE"), primary_key=True),
    db.Column('document_type_id', db.Integer, db.ForeignKey('document_type.id', ondelete="RESTRICT"), primary_key=True)
)


@whooshee.register_model('name', 'description')
class OrderType(db.Model):
    __tablename__ = 'order_type'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(200), nullable=True)
    
    # Relationships
    required_documents = db.relationship('DocumentType', secondary=order_type_documents, back_populates='order_types')
    orders = db.relationship('Order', back_populates='order_type', lazy=True)
    
    def __repr__(self):
        return f'<OrderType {self.name}>'


class DocumentType(db.Model):
    __tablename__ = 'document_type'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(200), nullable=True)
    # is_mandatory = db.Column(db.Boolean, default=True, nullable=False)  # Whether this document is mandatory
    
    # Relationships
    order_types = db.relationship('OrderType', secondary=order_type_documents, back_populates='required_documents')
    order_documents = db.relationship('OrderDocument', back_populates='document_type', lazy=True)

    def __repr__(self):
        return f'<DocumentType {self.name}>'


class DocumentStatus(db.Model):
    """
    Predefined statuses for document lifecycle:
    - Pending (waiting for client to upload)
    - Received (client uploaded)
    - Submitted (sent to authorities)
    - Rejected (authorities rejected, needs resubmission)
    - Accepted (authorities accepted)
    """
    __tablename__ = 'document_status'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(200), nullable=True)
    
    # Relationships
    order_documents = db.relationship('OrderDocument', back_populates='current_status_rel', lazy=True)
    document_history = db.relationship('DocumentStatusHistory', back_populates='status', lazy=True)

    def __repr__(self):
        return f'<DocumentStatus {self.name}>'


@whooshee.register_model('name')
class Company(db.Model):
    __tablename__ = 'company'
    __table_args__ = (
        Index('idx_company_registrar', 'registrar_id'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    registrar_id = db.Column(db.Integer, db.ForeignKey('registrar.id', ondelete="RESTRICT"), nullable=False)
    
    # Relationships
    registrar = db.relationship('Registrar', back_populates='companies')
    orders = db.relationship('Order', back_populates='company', lazy=True)

    def __repr__(self):
        return f'<Company {self.name}>'


@whooshee.register_model('name')
class Registrar(db.Model):
    __tablename__ = 'registrar'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    
    # Relationships
    companies = db.relationship('Company', back_populates='registrar', lazy=True)
    
    def __repr__(self):
        return f'<Registrar {self.name}>'

    
class OrderStatus(db.Model):
    """
    Predefined statuses for order lifecycle:
    - Started
    - Documents Pending
    - Documents Submitted
    - In Progress
    - Completed
    - Failed
    - Cancelled
    """
    __tablename__ = 'order_status'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(200), nullable=True)
    
    # Relationships
    orders = db.relationship('Order', back_populates='status', lazy=True)
    status_history = db.relationship('OrderStatusHistory', back_populates='status', lazy=True)

    def __repr__(self):
        return f'<OrderStatus {self.name}>'


class Order(db.Model):
    __tablename__ = 'order'
    __table_args__ = (
        Index('idx_order_client', 'client_id'),
        Index('idx_order_partner', 'partner_id'),
        Index('idx_order_status', 'status_id'),
        Index('idx_order_date', 'date_created'),
        CheckConstraint('fees >= 0', name='check_fees_positive'),
        CheckConstraint('base_charges >= 0', name='check_base_charges_positive'),
        CheckConstraint('share_count >= 0', name='check_shares_positive'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id', ondelete="RESTRICT"), nullable=False)
    partner_id = db.Column(db.Integer, db.ForeignKey('partner.id', ondelete="RESTRICT"), nullable=False)
    order_type_id = db.Column(db.Integer, db.ForeignKey('order_type.id', ondelete="RESTRICT"), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete="RESTRICT"), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('order_status.id', ondelete="RESTRICT"), nullable=False)
    
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    share_count = db.Column(db.Integer, nullable=True)
    share_price = db.Column(db.Float, nullable=True)      
    fees = db.Column(db.Float, nullable=False, default=0.0)
    base_charges = db.Column(db.Float, nullable=False, default=0.0)
    payment_status = db.Column(db.Boolean, default=False, nullable=False)
    settlement_status = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    client = db.relationship('Client', back_populates='orders')
    partner = db.relationship('Partner', back_populates='orders')
    order_type = db.relationship('OrderType', back_populates='orders')
    company = db.relationship('Company', back_populates='orders')
    status = db.relationship('OrderStatus', back_populates='orders')
    
    documents = db.relationship('OrderDocument', back_populates='order', lazy=True, cascade="all, delete-orphan")
    receipts = db.relationship('Receipt', back_populates='order', lazy=True, cascade="all, delete-orphan")
    expenses = db.relationship('Expense', back_populates='order', lazy=True, cascade="all, delete-orphan")
    comments = db.relationship('Comment', back_populates='order', lazy=True, cascade="all, delete-orphan")
    settlements = db.relationship('Settlement', back_populates='order', lazy=True, cascade="all, delete-orphan")
    status_history = db.relationship('OrderStatusHistory', back_populates='order', lazy=True, 
                                     cascade="all, delete-orphan", 
                                     order_by='OrderStatusHistory.date_created')

    @validates('fees', 'base_charges')
    def validate_positive_amounts(self, key, value):
        if value < 0:
            raise ValueError(f"{key} must be non-negative")
        return value

    def calculate_total_receipts(self):
        """Calculate total receipts for this order."""
        return sum(receipt.amount for receipt in self.receipts)
    
    def calculate_total_expenses(self):
        """Calculate total expenses for this order."""
        return sum(expense.amount for expense in self.expenses)
    
    def calculate_settlement(self):
        """
        Calculate settlement amounts for this order.
        Returns tuple of (partner_amount, self_amount)
        """
        total_expenses = self.calculate_total_expenses()
        
        if self.status.name == 'Completed':
            net_amount = self.fees - total_expenses
            partner_amount = net_amount * self.partner.revenue_share
            self_amount = net_amount * (1 - self.partner.revenue_share)
        elif self.status.name == 'Failed':
            # For failed orders, calculate based on base_charges
            net_amount = self.base_charges - total_expenses
            if net_amount >= 0:
                partner_amount = net_amount * self.partner.revenue_share
                self_amount = net_amount * (1 - self.partner.revenue_share)
            else:
                # If expenses exceed base_charges
                partner_amount = 0.0
                self_amount = net_amount  # This will be negative
        else:
            # For other statuses, no settlement
            return None, None
        
        return partner_amount, self_amount
    
    def create_settlement(self):
        """Create a settlement record for this order."""
        partner_amount, self_amount = self.calculate_settlement()
        
        if partner_amount is None:
            return None
        
        settlement = Settlement(
            partner_id=self.partner_id,
            order_id=self.id,
            partner_amount=partner_amount,
            self_amount=self_amount
        )
        return settlement
    
    def update_status(self, new_status_id, notes=None, changed_by=None):
        """
        Update order status and create history record.
        
        Args:
            new_status_id: ID of the new status
            notes: Optional notes about the status change
            changed_by: Optional user ID who made the change
        """
        if self.status_id != new_status_id:
            # Update current status
            self.status_id = new_status_id
            
            # History will be automatically created by the event listener
            # But if you want to add notes or changed_by, create it manually
            if notes or changed_by:
                history = OrderStatusHistory(
                    order_id=self.id,
                    status_id=new_status_id,
                    notes=notes,
                    changed_by=changed_by
                )
                db.session.add(history)
    
    def get_status_timeline(self):
        """Get chronological list of all status changes."""
        return self.status_history
    
    def get_pending_documents(self):
        """Get all documents that are still pending."""
        return [doc for doc in self.documents if doc.current_status_rel.name == 'Pending']
    
    def get_rejected_documents(self):
        """Get all documents that have been rejected."""
        return [doc for doc in self.documents if doc.current_status_rel.name == 'Rejected']
    
    def are_all_documents_accepted(self):
        """Check if all mandatory documents are accepted."""
        for doc in self.documents:
            if doc.document_type.is_mandatory and doc.current_status_rel.name != 'Accepted':
                return False
        return True

    def __repr__(self):
        return f'<Order {self.id}>'


class OrderStatusHistory(db.Model):
    __tablename__ = 'order_status_history'
    __table_args__ = (
        Index('idx_status_history_order', 'order_id'),
        Index('idx_status_history_date', 'date_created'),
        Index('idx_status_history_status', 'status_id'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete="CASCADE"), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('order_status.id', ondelete="RESTRICT"), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    changed_by = db.Column(db.Integer, nullable=True)  # User ID who made the change
    
    # Relationships
    order = db.relationship('Order', back_populates='status_history')
    status = db.relationship('OrderStatus', back_populates='status_history')
    
    def __repr__(self):
        return f'<OrderStatusHistory Order:{self.order_id} Status:{self.status_id} at {self.date_created}>'


class OrderDocument(db.Model):
    """
    Represents a specific document instance for an order.
    Each order will have instances of all required documents for its order type.
    """
    __tablename__ = 'order_document'
    __table_args__ = (
        Index('idx_order_document_order', 'order_id'),
        Index('idx_order_document_type', 'document_type_id'),
        Index('idx_order_document_status', 'current_status_id'),
        # Ensure each document type appears only once per order
        db.UniqueConstraint('order_id', 'document_type_id', name='uq_order_document'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete="CASCADE"), nullable=False)
    document_type_id = db.Column(db.Integer, db.ForeignKey('document_type.id', ondelete="RESTRICT"), nullable=False)
    current_status_id = db.Column(db.Integer, db.ForeignKey('document_status.id', ondelete="RESTRICT"), nullable=False)
    
    file_path = db.Column(db.String(255), nullable=True)
    uploaded_at = db.Column(db.DateTime, nullable=True)
    submitted_at = db.Column(db.DateTime, nullable=True)  # When submitted to authorities
    
    # Relationships
    order = db.relationship('Order', back_populates='documents')
    document_type = db.relationship('DocumentType', back_populates='order_documents')
    current_status_rel = db.relationship('DocumentStatus', back_populates='order_documents')
    status_history = db.relationship('DocumentStatusHistory', back_populates='document', lazy=True, 
                                     cascade="all, delete-orphan",
                                     order_by='DocumentStatusHistory.date_created')
    
    def update_status(self, new_status_id, notes=None, changed_by=None):
        """
        Update document status and create history record.
        
        Args:
            new_status_id: ID of the new status
            notes: Optional notes about the status change
            changed_by: Optional user ID who made the change
        """
        if self.current_status_id != new_status_id:
            # Update current status
            self.current_status_id = new_status_id
            
            # Create history (can also be done via event listener)
            if notes or changed_by:
                history = DocumentStatusHistory(
                    document_id=self.id,
                    status_id=new_status_id,
                    notes=notes,
                    changed_by=changed_by
                )
                db.session.add(history)
    
    def get_status_timeline(self):
        """Get chronological list of all status changes for this document."""
        return self.status_history

    def __repr__(self):
        return f'<OrderDocument {self.id} ({self.document_type.name}) for Order {self.order_id}>'


class DocumentStatusHistory(db.Model):
    """
    Tracks the complete history of status changes for each document.
    Example flow: Pending → Received → Submitted → Rejected → Received → Submitted → Accepted
    """
    __tablename__ = 'document_status_history'
    __table_args__ = (
        Index('idx_doc_history_document', 'document_id'),
        Index('idx_doc_history_status', 'status_id'),
        Index('idx_doc_history_date', 'date_created'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('order_document.id', ondelete="CASCADE"), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('document_status.id', ondelete="RESTRICT"), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    notes = db.Column(db.Text, nullable=True)  # e.g., "Photo unclear, resubmission required"
    changed_by = db.Column(db.Integer, nullable=True)  # User ID who made the change
    
    # Relationships
    document = db.relationship('OrderDocument', back_populates='status_history')
    status = db.relationship('DocumentStatus', back_populates='document_history')
    
    def __repr__(self):
        return f'<DocumentStatusHistory Doc:{self.document_id} Status:{self.status_id}>'


class Comment(db.Model):
    __tablename__ = 'comment'
    __table_args__ = (
        Index('idx_comment_order', 'order_id'),
        Index('idx_comment_date', 'date_created'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete="CASCADE"), nullable=False)
    comment_text = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    file_path = db.Column(db.String(255), nullable=True)
    created_by = db.Column(db.Integer, nullable=True)  # User ID who created the comment
    
    # Relationships
    order = db.relationship('Order', back_populates='comments')

    def __repr__(self):
        return f'<Comment {self.id} on Order {self.order_id}>'


class Receipt(db.Model):
    __tablename__ = 'receipt'
    __table_args__ = (
        Index('idx_receipt_order', 'order_id'),
        CheckConstraint('amount >= 0', name='check_receipt_amount_positive'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete="CASCADE"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    order = db.relationship('Order', back_populates='receipts')

    @validates('amount')
    def validate_amount(self, key, value):
        if value < 0:
            raise ValueError("Receipt amount must be non-negative")
        return value

    def __repr__(self):
        return f'<Receipt {self.id} for Order {self.order_id}>'

    
class Expense(db.Model):
    __tablename__ = 'expense'
    __table_args__ = (
        Index('idx_expense_order', 'order_id'),
        CheckConstraint('amount >= 0', name='check_expense_amount_positive'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete="CASCADE"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    order = db.relationship('Order', back_populates='expenses')

    @validates('amount')
    def validate_amount(self, key, value):
        if value < 0:
            raise ValueError("Expense amount must be non-negative")
        return value

    def __repr__(self):
        return f'<Expense {self.id} for Order {self.order_id}>'

    
class Settlement(db.Model):
    __tablename__ = 'settlement'
    __table_args__ = (
        Index('idx_settlement_order', 'order_id'),
        Index('idx_settlement_partner', 'partner_id'),
        Index('idx_settlement_date', 'date_created'),
        # Ensure only one settlement per order
        db.UniqueConstraint('order_id', name='uq_settlement_order'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete="CASCADE"), nullable=False)
    partner_id = db.Column(db.Integer, db.ForeignKey('partner.id', ondelete="RESTRICT"), nullable=False)
    partner_amount = db.Column(db.Float, nullable=False)
    self_amount = db.Column(db.Float, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    order = db.relationship('Order', back_populates='settlements')
    partner = db.relationship('Partner', back_populates='settlements')

    def __repr__(self):
        return f'<Settlement {self.id} for Partner {self.partner_id}>'


# Event Listeners

@event.listens_for(Order, 'after_insert')
def create_order_documents(mapper, connection, target):
    """
    Automatically create OrderDocument instances for all required documents
    when a new order is created.
    """
    # Get the "Pending" status
    pending_status = db.session.query(DocumentStatus).filter_by(name='Pending').first()
    if not pending_status:
        # If Pending status doesn't exist, create it (or handle error)
        return
    
    # Get all required documents for this order type
    for doc_type in target.order_type.required_documents:
        order_doc = OrderDocument(
            order_id=target.id,
            document_type_id=doc_type.id,
            current_status_id=pending_status.id
        )
        db.session.add(order_doc)
        
        # Create initial status history
        history = DocumentStatusHistory(
            document_id=order_doc.id,
            status_id=pending_status.id,
            notes="Document requirement created with order"
        )
        db.session.add(history)


@event.listens_for(Order, 'after_insert')
def create_initial_order_status_history(mapper, connection, target):
    """
    Create initial status history when order is created.
    """
    initial_history = OrderStatusHistory(
        order_id=target.id,
        status_id=target.status_id,
        notes="Order created"
    )
    db.session.add(initial_history)


@event.listens_for(Order.status_id, 'set', retval=False)
def track_order_status_change(target, value, oldvalue, initiator):
    """
    Automatically create order status history when status_id changes.
    """
    from sqlalchemy.orm.attributes import NO_VALUE
    if oldvalue is NO_VALUE or oldvalue == value:
        return
    
    if target.id is not None:
        new_history = OrderStatusHistory(
            order_id=target.id,
            status_id=value,
            notes=f"Status changed automatically"
        )
        db.session.add(new_history)


@event.listens_for(OrderDocument.current_status_id, 'set', retval=False)
def track_document_status_change(target, value, oldvalue, initiator):
    """
    Automatically create document status history when current_status_id changes.
    """
    from sqlalchemy.orm.attributes import NO_VALUE
    if oldvalue is NO_VALUE or oldvalue == value:
        return
    
    if target.id is not None:
        new_history = DocumentStatusHistory(
            document_id=target.id,
            status_id=value,
            notes="Status changed automatically"
        )
        db.session.add(new_history)


@event.listens_for(OrderDocument, 'before_update')
def update_document_timestamps(mapper, connection, target):
    """Update timestamps when file_path changes or when submitted."""
    file_history = get_history(target, 'file_path')
    if file_history.has_changes() and target.file_path is not None:
        target.uploaded_at = datetime.utcnow()
    
    # Update submitted_at when status changes to Submitted
    status_history = get_history(target, 'current_status_id')
    if status_history.has_changes():
        # Check if new status is "Submitted"
        new_status = db.session.query(DocumentStatus).get(target.current_status_id)
        if new_status and new_status.name == 'Submitted':
            target.submitted_at = datetime.utcnow()


@event.listens_for(Order, 'after_update')
def handle_order_status_change(mapper, connection, target):
    """
    Handle settlement creation when order status changes to Completed or Failed.
    """
    history = get_history(target, 'status_id')
    if history.has_changes():
        if target.status and target.status.name in ('Completed', 'Failed'):
            existing_settlement = db.session.query(Settlement).filter_by(order_id=target.id).first()
            if not existing_settlement:
                settlement = target.create_settlement()
                if settlement:
                    db.session.add(settlement)


@event.listens_for(Order, 'after_update')
def handle_payment_status_change(mapper, connection, target):
    """
    Update settlement_status when payment_status changes.
    """
    history = get_history(target, 'payment_status')
    if history.has_changes():
        if target.payment_status:
            target.settlement_status = True
