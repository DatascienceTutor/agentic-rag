import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'company_records.db')

def init_db():
    """Initializes the SQLite database and seeds it with employee records."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create employees table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            employee_code TEXT PRIMARY KEY,
            full_name TEXT,
            email TEXT,
            department TEXT,
            joining_date TEXT,
            relieving_date TEXT,
            status TEXT
        )
    ''')
    
    # Seed data
    employees_data = [
        ('EMP101', 'Alice Smith', 'alice@example.com', 'Engineering', '2020-01-15', None, 'Active'),
        ('EMP102', 'Bob Jones', 'bob@example.com', 'HR', '2019-03-10', '2023-05-20', 'Relieved'),
        ('EMP103', 'Charlie Brown', 'charlie@example.com', 'Marketing', '2021-07-22', None, 'Active'),
        ('HR201', 'Diana Prince', 'diana@example.com', 'HR', '2018-05-11', None, 'Active'),
        ('HR202', 'Clark Kent', 'clark@example.com', 'HR', '2022-09-01', None, 'Active')
    ]
    
    # Insert seed data if not exists
    cursor.executemany('''
        INSERT OR IGNORE INTO employees (employee_code, full_name, email, department, joining_date, relieving_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', employees_data)
    
    conn.commit()
    conn.close()

def get_employee_record_secure(authenticated_emp_code: str):
    """
    Securely fetches the record for a given employee code.
    
    Args:
        authenticated_emp_code (str): The employee code of the authenticated user.
        
    Returns:
        dict: A dictionary containing the employee's details, or None if not found.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM employees WHERE employee_code = ?', (authenticated_emp_code,))
    record = cursor.fetchone()
    conn.close()
    
    if record:
        return {
            'employee_code': record[0],
            'full_name': record[1],
            'email': record[2],
            'department': record[3],
            'joining_date': record[4],
            'relieving_date': record[5],
            'status': record[6]
        }
    return None

if __name__ == "__main__":
    init_db()
