# 🛒 Senova Store - E-Commerce Backend API

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/Django_REST_Framework-3.16-red?style=for-the-badge&logo=django&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-SimpleJWT_5.5-orange?style=for-the-badge&logo=json-web-tokens&logoColor=white)
![Chapa](https://img.shields.io/badge/Payment-Chapa_API-green?style=for-the-badge)
![Swagger](https://img.shields.io/badge/API_Docs-Swagger%2FReDoc-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)

**Senova Store Backend** is a feature-rich, high-performance RESTful API built with Python, Django, and Django REST Framework (DRF). Designed specifically to power the Senova Store e-commerce platform, it features user management, product cataloging, order lifecycle tracking, customer reviews, and payment processing integrated with the **Chapa Payment Gateway**.

---

## 🌟 Key Features

### 🔐 1. User Management & Authentication
* **Custom User Model**: Extended Django user system supporting custom fields (profile picture, phone number, address, customer vs. admin roles).
* **JWT Authentication**: Secure access and refresh token authentication using `djangorestframework-simplejwt`.
* **Djoser Integration**: Automated account registration, profile management, and password reset email workflows.
* **Email Service**: SMTP email integration (Gmail SMTP) for verification links and password recovery.

### 🛍️ 2. Product Catalog & Inventory
* **Categories & Subcategories**: Hierarchical taxonomy for organized inventory navigation.
* **Product Variants & Attributes**: Support for item attributes (headwear, colors, sizes, stock levels, pricing, discounts).
* **Media Management**: Image uploads for product showcases and category banners powered by Pillow.
* **Advanced Search & Filtering**: Built-in search, filtering, and ordering via `django-filter` and DRF Filter backends.

### 💳 3. Payment Processing & Order Management
* **Chapa Payment Gateway**: Full integration with Chapa API for online payments in Ethiopia.
* **Order Creation & Tracking**: Automated checkout processing and real-time order status updates (`PENDING`, `COMPLETED`, `FAILED`).
* **Webhook Handling**: Secure backend webhook receiver (`/payments/webhook/`) to verify transaction payloads signed by Chapa.

### 💬 4. Customer Reviews & Support
* **Product & Site Reviews**: Customer review submission, moderation system, and overall store rating calculations.
* **Contact & Support Messages**: Contact form backend with message categorization and admin response tracking.

### 📄 5. API Documentation & Architecture
* **Interactive API Docs**: Auto-generated Swagger UI (`/swagger/`) and ReDoc (`/redoc/`) via `drf-yasg`.
* **Modular Settings**: Structured configuration (`base.py`, `dev.py`, `prod.py`) using environment separation.
* **WhiteNoise Static Serving**: Optimized static asset delivery for development and production environments.

---

## 📁 Directory Structure

```
senova_deployment_backend/
├── apps/                        # Modular Django Applications
│   ├── user_management/         # User models, Djoser serializers, auth views
│   │   ├── admin.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── utils.py
│   │   └── views.py
│   ├── products/                # Products, categories, headwear, inventory
│   │   ├── admin.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── payments/                # Chapa checkout, transactions, webhooks & orders
│   │   ├── admin.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   └── views.py
│   └── contact_review/          # Ratings, product reviews & contact inquiries
│       ├── admin.py
│       ├── models.py
│       ├── serializers.py
│       ├── urls.py
│       └── views.py
├── senova_deployment/           # Core Project Configuration
│   ├── settings/                # Settings Module
│   │   ├── __init__.py
│   │   ├── base.py              # Common settings (Installed apps, Middleware, JWT, Djoser)
│   │   ├── dev.py               # Development settings
│   │   └── prod.py              # Production settings
│   ├── asgi.py                  # ASGI config
│   ├── urls.py                  # Main API routing table
│   └── wsgi.py                  # WSGI config
├── templates/                   # HTML templates (Email templates)
├── manage.py                    # Django CLI management script
├── passenger_wsgi.py            # WSGI script for cPanel hosting deployment
├── requirements.txt             # Python project dependencies
└── .gitignore                   # Git exclusion rules
```

---

## ⚙️ Environment Variables Setup

Create a `.env` file in the root directory of `senova_deployment_backend`:

```env
# Django Settings
SECRET_KEY=your_django_secret_key_here
DJANGO_ENV=dev
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Base URLs
BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
DOMAIN=localhost:5173
SITE_NAME=Senova Store

# Email Settings (Gmail SMTP)
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

# Chapa Payment Credentials
CHAPA_SECRET_KEY=CHASECK_TEST-xxx
CHAPA_PUBLIC_KEY=CHAPUBK_TEST-xxx
```

---

## 🚀 How to Run locally

Follow these steps to set up and run the backend locally:

### 1. Prerequisites
Ensure you have **Python 3.10+** and `pip` installed on your machine.

### 2. Clone the Repository
```bash
git clone <repository-url>
cd senova_deployment_backend
```

### 3. Create & Activate Virtual Environment
* **On Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
* **On Windows:**
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run Database Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser (Admin Account)
```bash
python manage.py createsuperuser
```

### 7. Start Development Server
```bash
python manage.py runserver
```

The backend server will be available at: **`http://localhost:8000`**

### 8. Ensure Frontend is Running

NOTE - THERE IS A FRONTEND FOR THIS BACKEND IN THE REPO - https://github.com/DrLeroK/senova_deployment_frontend.git

---




## 🔌 API Endpoints Summary

| Module | Endpoint | Method | Description |
| :--- | :--- | :--- | :--- |
| **Auth** | `/user_management/login/` | `POST` | Authenticate user & obtain JWT tokens |
| **Auth** | `/user_management/register/` | `POST` | Register a new user |
| **Auth** | `/api/token/refresh/` | `POST` | Refresh expired JWT access token |
| **Auth** | `/auth/users/` | `GET/POST` | Djoser user management |
| **Products** | `/products/` | `GET/POST` | List and search products |
| **Products** | `/products/<id>/` | `GET/PUT/DELETE` | Detailed product view & CRUD |
| **Products** | `/products/categories/` | `GET/POST` | Category management |
| **Payments** | `/payments/initialize/` | `POST` | Initialize Chapa transaction |
| **Payments** | `/payments/verify/<tx_ref>/` | `GET` | Verify payment status |
| **Payments** | `/payments/webhook/` | `POST` | Chapa webhook callback listener |
| **Reviews** | `/contact_review/reviews/` | `GET/POST` | View and post product reviews |
| **Contact** | `/contact_review/contact/` | `POST` | Submit customer support inquiry |
| **Docs** | `/swagger/` | `GET` | Interactive Swagger API Documentation |
| **Docs** | `/redoc/` | `GET` | ReDoc API Documentation |

---


## 🤝 Contributing

- Fork the repository
- Create your feature branch (git checkout -b feature/amazing-feature)
- Commit your changes (git commit -m 'Add some amazing feature')
- Push to the branch (git push origin feature/amazing-feature)
- Open a Pull Request

# 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

