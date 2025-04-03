# Dublin Bikes Login System

This is a Flask-based authentication system for the Dublin Bikes web application. It includes user registration, login, dashboard, and password reset functionality.

## Project Structure

```
dublin-bikes-login/
│
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── static/             # Static files (images, CSS, JS)
│   ├── dublin-bike-logo.png
│   └── bike-logo.png
└── templates/          # HTML templates
    ├── log_in.html
    ├── create_account.html
    ├── dashboard.html
    └── reset_password.html
```

## Setup Instructions

1. Create a Python virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `static` directory for your images:
   ```
   mkdir static
   ```

5. Copy your logo images to the static directory:
   - dublin-bike-logo.png
   - bike-logo.png

6. Initialize the database:
   - Run the Flask application
   - Visit `/initialize_db` endpoint in your browser

7. Start the application:
   ```
   python app.py
   ```

8. Access the application at http://localhost:5000

## Features

- User registration with password strength validation
- Secure login with password hashing
- User dashboard with profile management
- Password reset functionality
- Responsive design for all screen sizes

## Technology Stack

- Backend: Flask (Python)
- Database: MySQL
- Frontend: HTML, CSS, JavaScript
- Security: bcrypt for password hashing, Flask session management

## Database Schema

The application uses a MySQL database with the following user table structure:

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fullname VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    terms_accepted TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL,
    last_login DATETIME,
    status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',
    verification_token VARCHAR(255),
    is_verified TINYINT(1) DEFAULT 0,
    reset_token VARCHAR(255),
    reset_token_expiry DATETIME
)
```