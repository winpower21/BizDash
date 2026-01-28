from xml.dom.minidom import Document
from flask import render_template, request, redirect, url_for, flash
from flask import current_app as app
from flask import send_file
from sqlalchemy import func
from werkzeug.utils import secure_filename
from .models import *
from .functions import *
import datetime
import os

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/flash', methods=['GET'])
def flash_message():
    flash('This is a flash message!', 'warning')
    return redirect(url_for('index'))


# ----------------------- Partner Routes -----------------------
@app.route('/new-partner', methods=['GET', 'POST'])
def partner_new():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        if not name or not email:
            flash('Name and Email are required fields.', 'danger')
            return redirect(url_for('partner_new'))
        new_partner = Partner(name=name, email=email, phone=phone)
        db.session.add(new_partner)
        db.session.commit()
        flash('New partner added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('new-partner.html')


@app.route('/partners', methods=['GET'])
def partners():
    partners = Partner.query.all()
    return render_template('partners.html', partners=partners)

@app.route('/partner-info/<int:partner_id>', methods=['GET', 'PUT', 'DELETE'])
def partner_info(partner_id):
    partner = Partner.query.get_or_404(partner_id)
    if request.method == 'PUT':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        if not name or not email:
            flash('Name and Email are required fields.', 'danger')
            return redirect(url_for('partner_info', partner_id=partner.id))
        partner.name = name
        partner.email = email
        partner.phone = phone
        db.session.commit()
        flash('Partner information updated successfully!', 'success')
    elif request.method == 'DELETE':
        db.session.delete(partner)
        db.session.commit()
        flash('Partner deleted successfully!', 'success')
        return redirect(url_for('partners'))
    return redirect(url_for('partners'))



# ----------------------- Client Routes -----------------------

@app.route('/clients', methods=['GET'])
def clients():
    clients = Client.query.all()
    return render_template('clients.html', clients=clients)

@app.route('/new-client', methods=['GET', 'POST'])
def client_new():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        if not name or not email:
            flash('Name and Email are required fields.', 'danger')
            return redirect(url_for('client_new'))
        client = Client.query.filter_by(email=email).first()
        if client:
            flash('Client with this email already exists.', 'danger')
            return redirect(url_for('client_new'))
        new_client = Client(name=name, email=email, phone=phone, address=address)
        db.session.add(new_client)
        db.session.commit()
        flash('New client added successfully!', 'success')
        return redirect(url_for('clients'))
    return render_template('new-client.html')

@app.route('/client-info/<int:client_id>', methods=['GET', 'PUT', 'DELETE'])
def client_info(client_id):
    client = Client.query.get_or_404(client_id)
    if request.method == 'PUT':
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        address = data.get('address')
        # name = request.form['name']
        # email = request.form['email']
        # phone = request.form['phone']
        # address = request.form['address']
        if not name or not email or not phone:
            flash('Name, Phone and Email are required fields.', 'danger')
            return redirect(url_for('clients'))
        try:
            existing_client = Client.query.filter(Client.email == email, Client.id != client.id).first()
            if existing_client:
                flash('Another client with this email already exists.', 'danger')
                return redirect(url_for('clients'))
            client.name = name
            client.email = email
            client.phone = phone
            client.address = address
            db.session.commit()            
            flash('Client information updated successfully!', 'success')
            return redirect(url_for('clients'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating client: {str(e)}', 'danger')
            return redirect(url_for('clients'))
    elif request.method == 'DELETE':
        db.session.delete(client)
        db.session.commit()
        flash('Client deleted successfully!', 'success')
        return redirect(url_for('clients'))
    # return render_template('client-info.html', client=client)


# ----------------------- Order Type Routes -----------------------
@app.route('/order-type', methods=['GET', 'POST'])
def order_type():
    if request.method == 'GET':
        order_types = db.session.query(Order.category, func.count(Order.id)).group_by(Order.category).all()
        return render_template('order-type.html', type=order_types)
    elif request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        if not name:
            flash('Category name is required.', 'danger')
            return redirect(url_for('order_type'))
        new_category = OrderType(name=name, description=description)
        db.session.add(new_category)
        db.session.commit()
        flash('New category added successfully!', 'success')
        return redirect(url_for('order_type'))
    


# ----------------------- Document Type Routes -----------------------
@app.route('/document-types', methods=['GET', 'POST'])
def document_types():
    if request.method == 'GET':
        doc_types = db.session.query(DocumentType.name, func.count(Document.id)).group_by(DocumentType.name).all()
        return render_template('document-types.html', type=doc_types)
    elif request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        if not name:
            flash('Document type name is required.', 'danger')
            return redirect(url_for('document_types'))
        new_type = DocumentType(name=name, description=description)
        db.session.add(new_type)
        db.session.commit()
        flash('New document type added successfully!', 'success')
        return redirect(url_for('document_types'))



# ----------------------- Company Routes -----------------------
@app.route('/companies', methods=['GET', 'POST'])
def companies():
    if request.method == 'GET':
        companies = Company.query.all()
        return render_template('companies.html', companies=companies)
    elif request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        if not name:
            flash('Company name is required.', 'danger')
            return redirect(url_for('companies'))
        new_company = Company(name=name, address=address)
        db.session.add(new_company)
        db.session.commit()
        flash('New company added successfully!', 'success')
        return redirect(url_for('companies'))    



@app.route('/company-info/<int:company_id>', methods=['GET', 'PUT', 'DELETE'])
def company_info(company_id):
    company = Company.query.get_or_404(company_id)
    if request.method == 'PUT':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        email = request.form['email']
        if not name or not email:
            flash('Company Name and Email are required fields.', 'danger')
            return redirect(url_for('company_info', company_id=company.id))
        company.name = name
        company.address = address
        company.phone = phone
        company.email = email
        db.session.commit()
        flash('Company information updated successfully!', 'success')
    elif request.method == 'DELETE':
        db.session.delete(company)
        db.session.commit()
        flash('Company deleted successfully!', 'success')
        return redirect(url_for('companies'))
    return render_template('company-info.html', company=company)

# ----------------------- Registrar Routes -----------------------
@app.route('/registrars', methods=['GET', 'POST'])
def registrars():
    if request.method == 'GET':
        registrars = Registrar.query.all()
        return render_template('registrars.html', registrars=registrars)
    elif request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        if not name or not email:
            flash('Registrar Name and Email are required fields.', 'danger')
            return redirect(url_for('registrars'))
        new_registrar = Registrar(name=name, email=email, phone=phone)
        db.session.add(new_registrar)
        db.session.commit()
        flash('New registrar added successfully!', 'success')
        return redirect(url_for('registrars'))


# ----------------------- Order Status Routes -----------------------

@app.route('/order-statuses', methods=['GET', 'POST'])
def order_statuses():
    if request.method == 'GET':
        statuses = OrderStatus.query.all()
        return render_template('order-statuses.html', statuses=statuses)
    elif request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        if not name:
            flash('Status Name is required.', 'danger')
            return redirect(url_for('order_statuses'))
        new_status = OrderStatus(name=name, description=description)
        db.session.add(new_status)
        db.session.commit()
        flash('New order status added successfully!', 'success')
        return redirect(url_for('order_statuses'))

# ----------------------- Order Routes -----------------------
@app.route('/orders', methods=['GET'])
def orders():
    orders = db.session.query(Order).all()
    return render_template('orders.html', orders=orders)


@app.route('/order/update/<int:order_id>/fields/<string:fields>', methods=['GET','PUT'])
def update_order_dynamic(order_id, fields):
    # 1. Convert "status,quantity" into ['status', 'quantity']
    target_fields = fields.split(',')

    # 2. Get the actual data from the JSON body
    data = request.get_json()

    if not data:
        flash('No JSON data provided.', 'danger')
        return redirect(url_for('orders'))

    updates = {}
    errors = []
    for field in target_fields:
        # if field in data:
        value = request.form.get(field)
        if value is not None:
            updates[field] = value
        else:
            errors.append(f"Field '{field}' promised in URL but missing in JSON")
        if errors:
            flash('\n'.join(errors), 'danger')
            return redirect(url_for('orders'))
    try:
        order = db.session.query(Order).get(order_id)
        if not order:
            flash('Order not found.', 'danger')
            return redirect(url_for('orders'))
        for field, value in updates.items():
            if hasattr(order, field):
                setattr(order, field, value)
            else:
                flash(f"Order has no attribute '{field}'", 'danger')
                return redirect(url_for('orders'))
        db.session.commit()
        flash('Order updated successfully!', 'success')
        return redirect(url_for('order_info', order_id=order.id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating order: {str(e)}', 'danger')
        return redirect(url_for('orders'))
    
    

@app.route('/order-info/<int:order_id>', methods=['GET', 'PUT', 'DELETE'])
def order_info(order_id):
    order = db.session.query(Order).get(order_id)
    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('orders'))
    if request.method == 'PUT':
        company_id = request.form.get('company_id', type=int)
        client_id = request.form.get('client_id', type=int)
        partner_id = request.form.get('partner_id', type=int)
        status_id = request.form.get('status_id', type=int)
        order_type_id = request.form.get('order_type_id', type=int)


        if not company_id or not client_id or not partner_id or not status_id or not order_type_id:
            flash('Company, Client, Partner, Status, and Order Type are required fields.', 'danger')
            return redirect(url_for('order_info', order_id=order.id))
        
        order.company_id = company_id
        order.client_id = client_id
        order.partner_id = partner_id
        order.status_id = status_id
        order.order_type_id = order_type_id
        db.session.commit()
        flash('Order information updated successfully!', 'success')
    elif request.method == 'DELETE':
        db.session.delete(order)
        db.session.commit()
        flash('Order deleted successfully!', 'success')
        return redirect(url_for('orders'))
    return render_template('order-info.html', order=order)


@app.route('/new-order', methods=['GET', 'POST'])
def order_new():
    if request.method == 'POST':
        company_id = request.form.get('company_id', type=int)
        client_id = request.form.get('client_id', type=int)
        partner_id = request.form.get('partner_id', type=int)
        order_type_id = request.form.get('order_type_id', type=int)

        if not company_id or not client_id or not partner_id or not order_type_id:
            flash('Company, Client, Partner, and Order Type are required fields.', 'danger')
            return redirect(url_for('order_new'))
        
        shares_count = request.form.get('shares_count', type=int)
        share_price = request.form.get('share_price', type=float)
        fees = request.form.get('fees', type=float)
        base_charges = request.form.get('base_charges', type=float)
        if not shares_count or not share_price or not fees or not base_charges:
            flash('Shares Count, Price per Share, Fees, and Base Charges are required fields.', 'danger')
            return redirect(url_for('order_new'))
        
        order_status = db.session.query(OrderStatus).filter_by(name='Started').first()
        
        if not order_status:
            flash('Default order status "Started" not found. Please create it first.', 'danger')
            return redirect(url_for('order_new'))
        
        
        new_order = Order(
            company_id=company_id,
            client_id=client_id,
            partner_id=partner_id,
            status_id=order_status.id,
            order_type_id=order_type_id,
            share_count=shares_count,
            share_price=share_price,
            fees=fees,
            base_charges=base_charges)
            
            
        try:
            db.session.add(new_order)
            db.session.commit()
            flash('New order created successfully!', 'success')
            return redirect(url_for('orders'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating order: {str(e)}', 'danger')
            return redirect(url_for('order_new'))
        
    if request.method == 'GET':
        clients = db.session.query(Client).all()
        companies = db.session.query(Company).all()
        partners = db.session.query(Partner).all()
        order_types = db.session.query(OrderType).all()
        order_status = db.session.query(OrderStatus).all()
        if not clients or not companies or not partners or not order_types or not order_status:
            flash('Please ensure that Clients, Companies, Partners, Order Types, and Order Statuses exist before creating an order.', 'danger')
            return redirect(url_for('orders'))
        return render_template('new-order.html', clients=clients, companies=companies, partners=partners, order_types=order_types, order_status=order_status)