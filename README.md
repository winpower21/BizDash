# BizDash: Business Management Portal

A customized webapp dashboard and management portal for a service-oriented business. BizDash provides a comprehensive suite of tools to manage clients, partners, orders, and financials in a single, integrated platform.

## App Functionality

BizDash is designed to streamline the entire lifecycle of a service order, from initial creation to final settlement. It provides a role-based interface for managing all aspects of the business.

### Core Features

*   **Dashboard:** A central hub providing at-a-glance information about recent activity, revenue summaries (realized and unrealized), and key performance indicators like average order value and completion time.
*   **Order Management:**
    *   Create, view, update, and delete orders.
    *   Track the status of each order through a detailed lifecycle (e.g., Started, Documents Pending, In Progress, Completed, Failed).
    *   Full history and timeline of all status changes for each order.
*   **Client & Partner Management:** Maintain a database of clients and partners, including contact information and associated orders.
*   **Document Management:**
    *   Define required documents for different types of orders.
    *   Upload and manage all documents related to an order.
    *   Track the status of each document (e.g., Pending, Received, Submitted, Rejected, Accepted).
*   **Financials & Settlements:**
    *   Record fees, base charges, receipts, and expenses for each order.
    *   Automatically calculate and create settlements based on the revenue share agreement with partners.
    *   Track payment and settlement status for each order.
*   **Task Management:** Create and track tasks associated with each order, with due dates and completion status.
*   **Reporting:** Generate detailed revenue reports for specific time periods, including breakdowns by partner.
*   **Resource Management:** A flexible interface to manage core business resources like Companies, Registrars, Document Types, and Order Types.

## Tech Stack

BizDash is a modern full-stack application with a clear separation between the frontend and backend.

*   **Frontend:**
    *   **Framework:** Vue.js
    *   **Routing:** Vue Router
    *   **State Management:** Pinia
    *   **UI:** Bootstrap
    *   **Desktop Shell:** Tauri (cross-platform for Windows and Linux)
*   **Backend:**
    *   **Framework:** Flask
    *   **API:** Flask-RESTful
    *   **Database:** SQLAlchemy (with a local SQLite database)
    *   **Migrations:** Flask-Migrate
    *   **Web Server:** Waitress

## Project Structure

The project is organized into two main applications: `frontend` (Vue.js) and `backend` (Flask), along with configuration and build-related files.

*   `./.github/workflows/`: Contains GitHub Actions workflow definitions for CI/CD, including automated releases.
*   `./backend/`: The Python Flask backend application.
    *   `./backend/application/`: Core Flask application logic, including database models, API resources, configuration, and utility functions.
    *   `./backend/migrations/`: Database migration scripts managed by Flask-Migrate (Alembic).
    *   `./backend/app.py`: The main Flask application entry point.
    *   `./backend/requirements.txt`: Python dependencies.
    *   `./backend/pyproject.toml`: Project metadata and dependencies (e.g., managed by `uv`).
*   `./frontend/`: The Vue.js frontend application.
    *   `./frontend/src/`: Source code for the Vue.js application.
        *   `./frontend/src/views/`: Vue components representing main application pages.
        *   `./frontend/src/components/`: Reusable Vue components.
        *   `./frontend/src/router/`: Vue Router configuration.
        *   `./frontend/src/stores/`: Pinia stores for state management.
        *   `./frontend/src/assets/`: Static assets like CSS.
        *   `./frontend/src/utils/`: Utility functions (e.g., API helpers, validators).
    *   `./frontend/public/`: Static assets served directly (e.g., favicon).
    *   `./frontend/node_modules/`: Node.js package dependencies.
    *   `./frontend/package.json`: Node.js project metadata and dependencies.
    *   `./frontend/vite.config.js`: Vite build configuration.
    *   `./frontend/src-tauri/`: Tauri-specific configurations and Rust source code.
        *   `./frontend/src-tauri/tauri.conf.json`: Tauri application configuration.
        *   `./frontend/src-tauri/src/main.rs`: Rust entry point for the Tauri application.
*   `./.gitignore`: Specifies intentionally untracked files to ignore.
*   `./LICENSE`: Project license information.
*   `./README.md`: This README file.

## Storage Structure (Uploaded Files)

Beyond the application's source code, BizDash manages uploaded files (documents and comment attachments) on the local filesystem. These files are organized in a structured manner within the `uploads/` directory.

*   **Order-Specific Document Uploads:**
    *   **Path:** `uploads/<client_name_slug>/<order_id>/<document_name>.<ext>`
    *   Documents related to specific orders are stored in a hierarchy. First, a folder is created based on the client's name (slugified for filesystem compatibility), then a subfolder for the `order_id`, and finally the individual document files are placed within. This ensures all documents for a particular order are grouped and easily identifiable.
*   **Comment Attachments:**
    *   **Path:** `uploads/comments/<order_id>/<filename>.<ext>`
    *   Files attached to comments are stored within a dedicated `comments` directory, further organized by `order_id`.

The paths to these stored files are recorded in the `file_path` columns of the `OrderDocument` and `Comment` tables within the database, allowing the application to retrieve them as needed.

## Database Models

The application uses a relational database (SQLite) to store all its data. The schema is designed to be robust and maintain data integrity.

*   **`Order`:** The central model, linking together clients, partners, order types, companies, and statuses. It also tracks financial details like fees and charges.
*   **`Client` & `Partner`:** Store information about the clients and partners of the business.
*   **`OrderType` & `DocumentType`:** Define the different types of services offered and the documents required for each.
*   **`OrderStatus` & `OrderStatusHistory`:** Track the lifecycle of an order.
*   **`OrderDocument` & `DocumentStatus`:** Manage the documents associated with an order and their individual statuses.
*   **`Company` & `Registrar`:** Manage a list of companies and their registrars.
*   **`Receipt` & `Expense`:** Track all financial transactions related to an order.
*   **`Settlement`:** Records the outcome of the revenue share calculation for completed or failed orders.
*   **`Task` & `Comment`:** Allow for task management and communication within the context of an order.



