from .models import Client, Company, DocumentStatus, DocumentType, OrderStatus, OrderType, Partner, Partner, Registrar, db

def create_default_document_status():
    default_statuses = {
        "Pending": "Pending (waiting for client to upload)",
        "Received": "Received (client uploaded)",
        "Submitted": "Submitted (sent to authorities)",
        "Rejected": "Rejected (authorities rejected, needs resubmission)",
        "Accepted": "Accepted (authorities accepted)"
    }
    
    for key, value in default_statuses.items():
        existing_status = db.session.query(DocumentStatus).filter_by(name=key).first()
        if not existing_status:
            new_status = DocumentStatus(name=key, description=value)
            db.session.add(new_status)
    db.session.commit()
    
def create_order_statuses():
    default_statuses = {
        "Received": "Received",
        "Confirmed": "Confirmed",
        "In-Progress": "In-Progress",
        "Documents Pending": "Documents Pending",
        "Documents Received": "Documents Received",
        "Documents Submitted": "Documents Submitted",
        "Documents Approved": "Documents Approved",
        "Documents Rejected": "Documents Rejected",
        "Success": "Success",
        "Failed": "Failed"
    }
    
    for key, value in default_statuses.items():
        existing_status = db.session.query(OrderStatus).filter_by(name=key).first()
        if not existing_status:
            new_status = OrderStatus(name=key, description=value)
            db.session.add(new_status)
    
    db.session.commit()
    
# def create_sample_data():
#     items = []
#     doc_type_index = []
#     if db.session.query(Client).count() == 0:
#         client = Client(name="Sample Client", email="sample@client.com", phone="1234567890", address="123 Sample St, Sample City")
#         items.append(client)
#     if db.session.query(Partner).count() == 0:
#         partner = Partner(name="Sample Partner", email="sample@partner.com", phone="9876543210")
#         items.append(partner)
#     if db.session.query(Registrar).count() == 0:
#         registrar = Registrar(name="Sample Registrar")
#         items.append(registrar)
#     if db.session.query(Company).count() == 0:
#         company = Company(name="Sample Company", registrar=registrar)
#         items.append(company)
#     if db.session.query(DocumentType).count() == 0:
#         document_types = ["Type A", "Type B", "Type C"]
#         for doc_type in document_types:
#             description = "Description for " + doc_type
#             new_doc_type = DocumentType(name=doc_type, description=description)
#             items.append(new_doc_type)
#             doc_type_index.append(items.index(new_doc_type))
#     if db.session.query(OrderType).count() == 0:
#         order_types = ["Order Type 1", "Order Type 2"]
#         for order_type in order_types:
#             description = "Description for " + order_type
#             new_order_type = OrderType(name=order_type, description=description)
#             new_order_type.required_documents = [items[i] for i in doc_type_index]
#             items.append(new_order_type)
#     db.session.add_all(items)
#     db.session.commit()