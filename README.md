# Smart Contract Management System

## Project Overview

This project is a comprehensive Smart Contract Management System built on Odoo 17. It provides a robust backend for managing contracts, termins, payments, and other related entities. It also includes a vendor portal built with Vue.js that allows vendors to view their contracts, upload documents, and track payment status.

## Modules

### `vit_contract`

This is the core module of the system. It defines the data models, views, and business logic for:

-   **Contracts**: The main contract entity, including details like start date, end date, amount, and associated documents.
-   **Termins**: The payment termins associated with a contract.
-   **Syarat Termins**: The conditions and required documents for each termin.
-   **Payments**: The payment records associated with a contract.
-   **Master Data**: Various master data models like contract types, budget RKAP, etc.

### `vit_contract_inherit`

This module inherits from `vit_contract` and extends its functionality. It adds new fields and modifies existing views to cater to specific business requirements.

### `vit_dashboard`

This module provides a dashboard for visualizing contract data. It presents key metrics and contract statuses in an easy-to-understand graphical interface.

### `vit_portal`

This Odoo module provides the backend for the vendor portal. It exposes the necessary data and logic to the Vue.js frontend via JSON-RPC endpoints.

### `vit-portal-vue`

This is a single-page application (SPA) built with Vue.js 3, Vite, and Pinia. It serves as the frontend for the vendor portal, allowing vendors to:

-   Log in to their account.
-   View a list of their contracts.
-   View the detailed information of a contract.
-   Upload required documents for each termin.
-   View the status of their payments.

## Setup and Installation

### Odoo Setup

1.  **Dependencies**: Ensure you have Odoo 17 installed and running.
2.  **Addons**: Place the `vit_contract`, `vit_contract_inherit`, `vit_dashboard`, and `vit_portal` modules into your Odoo addons path.
3.  **Installation**: In your Odoo instance, go to **Apps**, update the app list, and install the "Smart Contract" module.

### Vue.js Portal Setup

1.  **Navigate to the portal directory**:

    ```bash
    cd vit-portal-vue
    ```

2.  **Install dependencies**:

    ```bash
    npm install
    ```

3.  **Configure environment variables**: Create a `.env` file in the `vit-portal-vue` directory and add the following variables:

    ```
    VITE_ODOO_URL=http://your-odoo-instance.com
    VITE_ODOO_DB=your-odoo-database
    ```

4.  **Run the development server**:

    ```bash
    npm run dev
    ```

The portal will be accessible at `http://localhost:5173`.

## Key Features

-   **Centralized Contract Management**: Manage all contracts and related documents in one place.
-   **Vendor Portal**: A modern and user-friendly portal for vendors to interact with their contracts.
-   **Document Upload**: Vendors can upload required documents directly through the portal.
-   **Dynamic Status Tracking**: Contract and payment statuses are dynamically updated and displayed.
-   **Secure Authentication**: The vendor portal uses Odoo's authentication system to ensure secure access.

## Portal Usage

1.  **Login**: Vendors can log in using their Odoo credentials.
2.  **Contract List**: After logging in, vendors will see a list of their contracts with their current status.
3.  **Contract Detail**: Clicking on a contract will take them to the detail page, where they can see all the information about the contract, including termins and payment status.
4.  **Document Upload**: In the contract detail page, vendors can upload the required documents for each termin.
5.  **Document Deletion**: Vendors can delete uploaded documents, with a confirmation step to prevent accidental deletions.
