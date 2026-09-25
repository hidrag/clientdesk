# ClientDesk

ClientDesk is a beginner-friendly **Customer Database Management System** built with **Python, MySQL, and Streamlit**.

The project is designed as a practical learning project to combine Python programming, SQL, database connectivity, validation, CRUD operations, authentication, and Streamlit application development into one complete application.

---

## 📌 Project Overview

ClientDesk allows users to:

- Create an account
- Log in securely
- Store customer information
- Search customer records
- Add new customers
- Update customer information
- Delete customer records
- Validate user input before storing data
- Prevent duplicate usernames and email addresses

The project is being developed incrementally, with each feature implemented and tested before moving to the next stage.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Streamlit | Web interface |
| MySQL 8 | Database |
| mysql-connector-python | Python → MySQL connection |
| python-dotenv | Environment variable management |
| PyCharm | Development IDE |
| MySQL Workbench | Database management |
| Git / GitHub | Version control |

---

## 🏗️ Architecture

```text
User
  ↓
Streamlit Interface
  ↓
Input Validation
  ↓
Python Database Functions
  ↓
MySQL Database
```

The project intentionally avoids unnecessary frameworks and advanced architecture in V1.

No Django, Flask, FastAPI, SQLAlchemy, JWT, Redis, or Docker are required for V1.

---

## 📂 Project Structure

```text
ClientDesk/
│
├── .venv/
├── .env
├── .env.example
├── .gitignore
├── app.py
├── database.py
├── validation.py
├── requirements.txt
├── README.md
│
└── sql/
    └── schema.sql
```

### File Responsibilities

**`app.py`**  
Contains the Streamlit user interface and application flow.

**`database.py`**  
Contains functions responsible for communicating with MySQL, including connections, inserts, selects, duplicate checks, updates, and deletes.

**`validation.py`**  
Contains input validation functions for names, addresses, phone numbers, usernames, emails, and passwords.

**`.env`**  
Contains local database credentials. This file must **never be committed to GitHub**.

**`.env.example`**  
Contains the structure of required environment variables without exposing real credentials.

**`sql/schema.sql`**  
Contains database and table creation SQL.

---

# 🗄️ Database

## Database

```text
clientdesk
```

## Table

```text
cust_details
```

### Current Schema

```sql
CREATE TABLE cust_details (
    cust_id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(150) NOT NULL,
    address VARCHAR(500) NOT NULL,
    phone_number VARCHAR(10) NOT NULL,
    user_id VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);
```

### Columns

| Column | Type | Description |
|---|---|---|
| `cust_id` | INT | Primary key |
| `full_name` | VARCHAR(150) | Customer name |
| `address` | VARCHAR(500) | Customer address |
| `phone_number` | VARCHAR(10) | 10-digit phone number |
| `user_id` | VARCHAR(100) | Unique username |
| `email` | VARCHAR(255) | Unique email |
| `password` | VARCHAR(255) | Hashed password |

---

# 🔐 Validation Rules

ClientDesk performs validation before data reaches the database.

### Full Name

- Required
- Minimum 2 characters
- Maximum 150 characters
- Leading/trailing whitespace removed

### Address

- Required
- Maximum 500 characters
- Leading/trailing whitespace removed

### Phone Number

- Required
- Exactly 10 digits
- Digits only
- No `+91`
- No spaces
- No hyphens
- No letters

Examples:

```text
9876543210     ✓
+919876543210  ✗
98765 43210    ✗
98765-43210    ✗
987654321      ✗
98765432101    ✗
```

### Username

- Required
- Minimum 4 characters
- Maximum 100 characters
- No spaces
- Must be unique

### Email

- Required
- Converted to lowercase
- Basic email format validation
- Maximum 255 characters
- Must be unique

### Password

- Required
- Minimum 8 characters
- Maximum 128 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number

### Confirm Password

Must match the original password.

---

# 🔑 Authentication

ClientDesk uses the customer table for the initial V1 authentication system.

The first registered customer becomes the first application user.

Passwords should **never be stored as plaintext**.

Registration flow:

```text
Registration Form
       ↓
Input Validation
       ↓
Username / Email Duplicate Check
       ↓
Password Hashing
       ↓
Database Insert
       ↓
Registration Successful
```

---

# ⚙️ Local Setup

## 1. Clone the Repository

```bash
git clone <repository-url>
cd ClientDesk
```

## 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Main dependencies:

```text
streamlit
mysql-connector-python
python-dotenv
```

## 4. Configure MySQL

Create the database:

```sql
CREATE DATABASE clientdesk;
```

Then create the table using:

```text
sql/schema.sql
```

## 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD
DB_NAME=clientdesk
```

Do not commit `.env` to GitHub.

## 6. Run the Application

```bash
streamlit run app.py
```

---

# 🧪 Development Workflow

ClientDesk is being developed incrementally:

```text
Design
  ↓
Write Code
  ↓
Test
  ↓
Fix
  ↓
Understand
  ↓
Commit
  ↓
Next Feature
```

The goal is not simply to generate the entire application at once, but to understand how each component works.

---

# 📋 Current Development Status

## Foundation

- [x] MySQL installed
- [x] MySQL Workbench configured
- [x] Database created
- [x] Table created
- [x] Python virtual environment created
- [x] `mysql-connector-python` installed
- [x] Python → MySQL connection
- [x] `.env` configuration
- [x] `.gitignore`
- [x] Database connection function
- [x] INSERT function
- [x] SELECT function
- [x] Username duplicate check
- [x] Email duplicate check

## Validation

- [x] Full name validation
- [x] Address validation
- [x] Phone validation
- [x] Username validation
- [x] Email validation
- [x] Password validation
- [x] Confirm password validation

## Streamlit

- [x] Streamlit installed
- [x] Basic application created
- [x] Registration interface started
- [ ] Complete registration flow
- [ ] Password hashing
- [ ] Login system
- [ ] Session management

## Customer Management

- [ ] Add customer
- [ ] View customers
- [ ] Search customers
- [ ] Update customer
- [ ] Delete customer

## Deployment

- [ ] GitHub repository
- [ ] Cloud MySQL
- [ ] Streamlit Community Cloud deployment
- [ ] Production environment configuration

---

# 🚀 Planned V1 Features

1. Registration
2. Login
3. Authentication
4. Add customer
5. View customers
6. Search customers
7. Update customer
8. Delete customer
9. Input validation
10. Duplicate detection
11. Password hashing
12. Error handling
13. Streamlit UI

---

# 🔮 Future Improvements

Possible V2 improvements:

- Separate `users` and `customers` tables
- Multiple user accounts
- User roles
- Admin dashboard
- Customer ownership
- Created/updated timestamps
- Better search and filtering
- Pagination
- Advanced authentication
- Password reset
- Audit logs
- Improved UI
- Cloud database
- Production deployment

These features are intentionally outside the initial V1 scope.

---

# 🔒 Security Considerations

The project is primarily an educational application, but basic security practices are being followed.

### Environment Variables

Database credentials are stored in `.env`.

### SQL Injection Protection

Parameterized SQL queries are used:

```python
cursor.execute(
    "SELECT * FROM cust_details WHERE user_id = %s",
    (user_id,)
)
```

SQL strings should never be constructed using user input.

### Password Security

Passwords should be hashed before being stored in MySQL.

Plaintext passwords should not be stored in the database.

### Git Security

The following files should not be committed:

```text
.env
.venv/
__pycache__/
```

---

# 🎯 Learning Objectives

This project is being developed as a practical Python + SQL learning project.

### Python

- Variables
- Data types
- Strings
- Lists
- Tuples
- Sets
- Dictionaries
- Conditions
- Loops
- Functions
- Lambda
- Exception handling
- Modules
- Database connectivity
- Input validation

### SQL

- Database creation
- Table creation
- Primary keys
- Auto increment
- Unique constraints
- INSERT
- SELECT
- UPDATE
- DELETE
- WHERE
- Parameterized queries
- Transactions

### Streamlit

- Page configuration
- Text input
- Text area
- Password fields
- Buttons
- Validation messages
- Success/error messages
- Application state
- Forms

---

# 🌐 Planned Deployment

The planned deployment architecture is:

```text
GitHub
   ↓
Streamlit Community Cloud
   ↓
Python + Streamlit Application
   ↓
Cloud MySQL Database
```

Development will initially use:

```text
Windows 11
   ↓
PyCharm
   ↓
Python
   ↓
Local MySQL
   ↓
MySQL Workbench
```

Cloud deployment will be handled after the local V1 is complete.

---

# 📌 Project Philosophy

ClientDesk is intentionally being built as a simple application.

The objective is to understand the fundamentals of:

```text
Python
+
SQL
+
Databases
+
Web UI
+
Application Logic
```

before introducing more advanced frameworks and architecture.

The project can later evolve into a more production-oriented system.

---

# 📄 License

This project is currently intended as a personal learning and portfolio project.
