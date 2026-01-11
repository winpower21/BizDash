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

@app.route('/view-partners', methods=['GET'])
def view_partners():
    partners = Partner.query.all()
    return render_template('view-partners.html', partners=partners)

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
        return redirect(url_for('index'))
    return render_template('new-client.html')

@app.route('/view-clients', methods=['GET'])
def view_clients():
    clients = Client.query.all()
    return render_template('view-clients.html', clients=clients)

@app.route('/new-order', methods=['GET', 'POST'])
def order_new():
    partners = Partner.query.all()
    clients = Client.query.all()
    companies = Company.query.all()
    if request.method == 'POST':
        partner_id = request.form['partner_id']
        client_id = request.form['client_id']
        description = request.form['description']
        amount = request.form['amount']
        if not partner_id or not client_id or not amount:
            flash('Partner, Client, and Amount are required fields.', 'danger')
            return redirect(url_for('order_new'))
        new_order = Order(partner_id=partner_id, client_id=client_id,
                            description=description, amount=amount,
                            order_date=datetime.datetime.now())
        db.session.add(new_order)
        db.session.commit()
        flash('New order created successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('new-order.html', partners=partners, clients=clients, companies=companies)