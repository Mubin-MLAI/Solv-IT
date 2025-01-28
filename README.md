

## Description
This Django application offers a solution for managing business operations with an emphasis on user experience and modern web technologies. It integrates Bootstrap for front-end design and employs Ajax for dynamic sales creation. The application features models for user profiles, vendors, customers, and transactions, including billing, invoicing, and inventory management.

## Prerequisites
- **Python installed**: Ensure Python is installed on your system. You can download it from the official [Python website](https://www.python.org/).
- **Understand Python and Django**: Basic understanding of Python programming and familiarity with Django web framework.

## Installation

Follow these steps to install the necessary dependencies and set up the application:

### Clone the Repository

```bash
git clone https://github.com/munuhee/sales-and-inventory-management.git
cd sales-and-inventory-management
```

### With Docker

1. **Build the Docker Image**

    ```bash
    docker build -t sales-and-inventory-management:1.0 .
    ```

2. **Run the Docker Container**

    ```bash
    docker run -d -p 8000:8000 sales-and-inventory-management:1.0
    ```

### Without Docker

#### On Linux

1. **Set Up the Virtual Environment**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

3. **Apply Migrations and Run the Server**

    ```bash
    python manage.py migrate
    python manage.py runserver
    ```

#### On Windows

1. **Set Up the Virtual Environment**

    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

2. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

3. **Apply Migrations and Run the Server**

    ```bash
    python manage.py migrate
    python manage.py runserver
    ```
