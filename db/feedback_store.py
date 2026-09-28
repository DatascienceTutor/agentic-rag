import sqlite3

DB_PATH = 'agent_feedback.db'

def init_feedback_db():
    """Initializes the SQLite database for storing agent feedback."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            response TEXT,
            rating INTEGER,
            notes TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def log_feedback(query: str, response: str, rating: int, notes: str):
    """
    Logs user feedback for an agent's response.
    
    Args:
        query (str): The original query from the user.
        response (str): The agent's response.
        rating (int): The rating given by the user.
        notes (str): Additional notes or corrections provided by the user.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO feedback_logs (query, response, rating, notes)
        VALUES (?, ?, ?, ?)
    ''', (query, response, rating, notes))
    conn.commit()
    conn.close()

def get_learned_corrections(limit: int = 5):
    """
    Retrieves the most recent feedback entries as learned corrections.
    
    Args:
        limit (int): The maximum number of corrections to retrieve.
        
    Returns:
        list: A list of dictionaries containing feedback details.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT query, response, rating, notes 
        FROM feedback_logs 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (limit,))
    records = cursor.fetchall()
    conn.close()
    
    corrections = []
    for record in records:
        corrections.append({
            'query': record[0],
            'response': record[1],
            'rating': record[2],
            'notes': record[3]
        })
    return corrections

if __name__ == "__main__":
    init_feedback_db()
