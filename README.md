Loan & Utility Sharing System

Overview

This project is a Django REST Framework (DRF) application that allows users to manage loans and utilities, invite other users to share payments, and track balances efficiently. Users can find others via personal number and propose shared payment plans.

Features

User Management: Users have a first name, last name, personal number, and balance.

Loans & Utilities:

Loans include name, due amount, monthly payment, and payment due date.

Utilities include name, due amount, and payment due date.

Payment Sharing:

Users can invite others to share loan payments.

The invited user can accept the proposal, deducting the specified amount from their balance.

REST API Endpoints:

User registration and profile management.

Create and manage loans and utilities.

Invite users and accept shared payment proposals.

Installation

Prerequisites

Python 3.10+

Django & Django REST Framework

PostgreSQL (or SQLite for local development)

Setup

# Clone the repository
git clone https://github.com/yourusername/your-repo.git
cd your-repo

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Create a superuser (optional)
python manage.py createsuperuser

# Start the server
python manage.py runserver

API Endpoints

Method

Endpoint

Description

POST

/api/users/register/

Register a new user

GET

/api/users/{personal_number}/

Get user details by personal number

POST

/api/loans/

Create a loan

GET

/api/loans/

List all loans

POST

/api/utilities/

Create a utility

GET

/api/utilities/

List all utilities

POST

/api/payments/share/

Invite user to share payment

PATCH

/api/payments/share/{id}/accept/

Accept shared payment invitation

Technologies Used

Django & Django REST Framework

PostgreSQL (or SQLite for development)

Celery for background tasks (if required)

Docker (optional for deployment)
