Project Overview

This project is a Django REST Framework (DRF) application that allows users to manage loans and utilities, invite other users to share payments, and track balances.

Features

User registration and authentication

Loan and utility management

User invitations for sharing payments

Automatic balance deductions upon agreement

API endpoints for managing users, loans, utilities, and invitations

Installation

Prerequisites

Python 3.10+

Django

Django REST Framework

PostgreSQL (or any preferred database)

Setup

Clone the repository:

git clone <repository_url>
cd <project_directory>

Create a virtual environment and activate it:

python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

Install dependencies:

pip install -r requirements.txt

Configure your .env file (if used) for database settings.

Apply migrations:

python manage.py migrate

Create a superuser (optional, for admin access):

python manage.py createsuperuser

Run the development server:

python manage.py runserver

API Endpoints

User Management

POST /api/register/ - Register a new user

POST /api/token/ - Get authentication token

Loan & Utility Management

GET /api/loans/ - List user loans

POST /api/loans/ - Create a new loan

GET /api/utilities/ - List user utilities

POST /api/utilities/ - Add a new utility

Payment Sharing

POST /api/invitations/ - Invite a user to share payment

PATCH /api/invitations/<id>/ - Accept or reject invitation

Technologies Used

Django & Django REST Framework

PostgreSQL

Celery (for background tasks, if needed)

Redis (for caching, if used)
