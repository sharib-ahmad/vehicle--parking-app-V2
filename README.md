# 🅿️ Vehicle Parking App V2

A comprehensive full-stack Vehicle Parking Management Application for 4-wheeler parking with role-based access control, real-time availability tracking, and automated background jobs.

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#️-tech-stack)
- [Architecture](#️-architecture)
- [Installation](#-installation)
- [Configuration](#️-configuration)
- [API Documentation](#-api-documentation)
- [Database Schema](#️-database-schema)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

## 🎯 Overview

This application provides an efficient solution for managing parking lots, parking spots, and vehicle reservations with distinct roles for Administrators and Users. It features a modern REST API backend with Flask and a responsive Vue.js frontend.

**Developed by:** Sharib Ahmad (24f2001786)  
**Course:** Modern Application Development II - Sep 2025 Term  
**Collage Email:** 24f2001786@ds.study.iitm.ac.in
**Personal Email:** sharibahmad6716@gmail.com

## ✨ Features

### Core Functionality
- **Multi-user Support** - Role-based access (Admin/User)
- **Parking Lot Management** - Create, update, and manage parking facilities
- **Spot Reservation System** - Real-time booking and availability tracking
- **Vehicle Registration** - Support for multiple vehicle brands, models, and colors
- **Payment Processing** - Integrated dummy payment portal

### Additional Features
- 📊 **Data Visualization** - Chart.js integration for analytics and occupancy trends
- 📱 **Responsive Design** - Mobile-friendly Bootstrap 5 UI
- 🔒 **Secure Authentication** - JWT token-based auth with refresh tokens
- 📄 **PDF Reports** - Monthly activity reports generation
- 📧 **Email Notifications** - Daily reminders and monthly reports via Celery
- 📥 **CSV Export** - Export parking data for analysis
- ✅ **Form Validation** - Both frontend (HTML5/JS) and backend validation
- ⚡ **Redis Caching** - Fast data access for frequently requested information

## 🛠️ Tech Stack

### Backend
- **Flask** - Python web framework
- **Flask-RESTX** - RESTful API with Swagger documentation
- **SQLAlchemy** - ORM for database operations
- **SQLite** - Database system
- **Redis** - Caching and message broker
- **Celery** - Asynchronous task queue
- **Flask-Security** - Authentication and authorization
- **Jinja2** - Template engine

### Frontend
- **Vue.js 3** - Progressive JavaScript framework
- **Vue Router** - Client-side routing
- **Pinia** - State management
- **Bootstrap 5** - CSS framework
- **Chart.js** - Data visualization
- **Vite** - Build tool and dev server

## 🏗️ Architecture

The application follows a modern full-stack architecture:

```
┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│   Vue.js    │ ◄─────► │  Flask API   │ ◄─────► │   SQLite     │
│  Frontend   │  REST   │   Backend    │         │   Database   │
└─────────────┘         └──────────────┘         └──────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │    Redis     │
                        │   Caching    │
                        └──────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │    Celery    │
                        │    Workers   │
                        └──────────────┘
```

## 📦 Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- Redis Server

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/sharib-ahmad/vehicle--parking-app-V2
cd vehicle_parking_app_24f2001786/backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (create `.env` file):
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
SQLALCHEMY_DATABASE_URI=sqlite:///parking.db
REDIS_URL=redis://localhost:6379/0
```

5. Initialize database:
```bash
flask db upgrade
```

6. Run the Flask application:
```bash
python app.py
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd ../frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env.local` file:
```env
VITE_API_BASE_URL=http://localhost:5000
```

4. Run development server:
```bash
npm run dev
```

### Redis and Celery Setup

1. Start Redis server:
```bash
redis-server
```

2. Start Celery worker:
```bash
celery -A app.celery worker --loglevel=info
```

3. Start Celery beat (for scheduled tasks):
```bash
celery -A app.celery beat --loglevel=info
```

## ⚙️ Configuration

### Backend Configuration (`config.py`)
- Database connection settings
- JWT token expiration times
- Redis configuration
- Celery task schedules
- Email settings for notifications

### Frontend Configuration (`vite.config.js`)
- API base URL
- Build optimization settings
- Development server configuration

## 📚 API Documentation

The API is fully documented using Swagger/OpenAPI. Once the backend is running, access the interactive documentation at:

```
http://localhost:5000/swagger
```

### Authentication Endpoints
- `POST /auth/register` - Create new account
- `POST /auth/login` - Login with refresh token
- `POST /auth/logout` - Logout and revoke token
- `POST /auth/refresh` - Refresh access token

### Admin Endpoints (Auth Required)
- `GET /admin/parking-lots` - List all parking lots
- `POST /admin/parking-lots` - Create new parking lot
- `GET /admin/parking-lot/{lot_id}` - Get lot details
- `PUT /admin/parking-lot/{lot_id}` - Update parking lot
- `DELETE /admin/parking-lot/{lot_id}` - Delete parking lot
- `GET /admin/reservation/spot/{spot_id}` - Get spot reservation
- `GET /admin/search/{search_type}` - Search lots/users/vehicles
- `DELETE /admin/spot/{spot_id}` - Delete parking spot
- `GET /admin/summary` - Dashboard summary data

### User Endpoints (Auth Required)
- `GET /users/me` - Get user profile
- `PUT /users/me` - Update user profile
- `GET /users/reservations` - Get user reservations
- `PUT /users/reservations` - Update reservation
- `POST /users/booking_spot` - Book parking spot
- `GET /users/booking/{vehicle_number}` - Get vehicle details
- `POST /users/payments` - Process payment
- `GET /users/search` - Search lots by location
- `GET /users/summary` - User summary statistics
- `POST /users/export-csv` - Export parking data

### Public Endpoints
- `GET /public/brands` - Get vehicle brands
- `GET /public/colors` - Get vehicle colors
- `GET /public/models/{brand_name}` - Get models by brand

## 🗄️ Database Schema

### Key Entities

**User**
- Stores user credentials, profile information, and role
- Supports Admin and User roles

**ParkingLot**
- Contains location, address, pricing, and capacity information
- Links to multiple parking spots

**ParkingSpot**
- Individual parking spaces within a lot
- Tracks status (available/occupied) and revenue

**ReservedParkingSpot**
- Associates users with parking spots
- Contains reservation timestamps and cost details

**Vehicle**
- Stores vehicle information (brand, model, color, registration)
- Links to user through reservations

**Payment**
- Tracks payment transactions
- Links to reservations with status and timestamps

**TokenBlocklist**
- Manages revoked JWT tokens for security

Refer to the ER diagram in the project report for detailed relationships.

## 💻 Usage

### Admin Workflow
1. Login with admin credentials
2. Create and manage parking lots
3. Add parking spots to lots
4. View occupancy and revenue analytics
5. Search and manage user reservations
6. Generate reports and export data

### User Workflow
1. Register and login
2. Search for available parking lots by location
3. View available spots and pricing
4. Book a parking spot for your vehicle
5. Complete payment through payment portal
6. View and manage your reservations
7. Receive email notifications for bookings

## 📁 Project Structure

```
vehicle_parking_app_24f2001786/
├── backend/
│   ├── app.py                      # Main Flask application
│   ├── config.py                   # Configuration settings
│   ├── security.py                 # Security utilities
│   ├── requirements.txt            # Python dependencies
│   ├── models/                     # Database models
│   │   ├── user.py
│   │   ├── parkingLot.py
│   │   ├── parkingSpot.py
│   │   ├── reservedParkingSpot.py
│   │   ├── vehicle.py
│   │   ├── payments.py
│   │   ├── userProfile.py
│   │   └── token.py
│   └── routes/                     # API endpoints
│       ├── auth.py
│       ├── admin.py
│       ├── user.py
│       └── public.py
└── frontend/
    ├── src/
    │   ├── components/             # Vue components
    │   │   ├── admin/
    │   │   ├── user/
    │   │   ├── auth/
    │   │   └── common/
    │   ├── router/                 # Vue Router configuration
    │   ├── stores/                 # Pinia state management
    │   ├── services/               # API service layer
    │   ├── utils/                  # Utility functions
    │   ├── App.vue                 # Root component
    │   └── main.js                 # Application entry point
    ├── public/                     # Static assets
    ├── package.json                # Node dependencies
    └── vite.config.js              # Vite configuration
```

## 🤝 Contributing

This is an academic project. For any questions or suggestions, please contact:
- **Email:** 24f2001786@ds.study.iitm.ac.in

## 📝 License

This project is developed as part of the Modern Application Development II course at IIT Madras.

## 🙏 Acknowledgments

- IIT Madras for course curriculum and guidance
- AI assistance used for documentation, debugging, and optimization
- Open-source community for the frameworks and libraries used

---

**Note:** Core functionality, business logic, database design, and API implementation were developed independently. AI assistance was limited to documentation enhancement, debugging support, UI/UX suggestions, and code optimization recommendations.