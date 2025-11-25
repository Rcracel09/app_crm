"""
Customer Viewer - Simple web app to visualize customer database
Connects to customer-db and displays data in HTML tables
"""
import os
import psycopg2
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Database configuration from environment
DB_HOST = os.getenv('DB_HOST', 'customer-db')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'demo_db')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres123')


def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def get_customers():
    """Fetch all customers from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, email, phone, address, company, notes, created_at
        FROM customers
        ORDER BY id
    """)
    
    customers = []
    for row in cursor.fetchall():
        customers.append({
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'phone': row[3],
            'address': row[4],
            'company': row[5],
            'notes': row[6],
            'created_at': row[7]
        })
    
    cursor.close()
    conn.close()
    
    return customers


def get_interactions():
    """Fetch all interactions with customer names"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            i.id,
            c.name as customer_name,
            i.interaction_type,
            i.subject,
            i.description,
            i.created_by,
            i.created_at
        FROM interactions i
        JOIN customers c ON i.customer_id = c.id
        ORDER BY i.created_at DESC
    """)
    
    interactions = []
    for row in cursor.fetchall():
        interactions.append({
            'id': row[0],
            'customer_name': row[1],
            'interaction_type': row[2],
            'subject': row[3],
            'description': row[4],
            'created_by': row[5],
            'created_at': row[6]
        })
    
    cursor.close()
    conn.close()
    
    return interactions


def get_stats():
    """Get database statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total customers
    cursor.execute("SELECT COUNT(*) FROM customers")
    total_customers = cursor.fetchone()[0]
    
    # Total interactions
    cursor.execute("SELECT COUNT(*) FROM interactions")
    total_interactions = cursor.fetchone()[0]
    
    # Customers with .pt emails
    cursor.execute("SELECT COUNT(*) FROM customers WHERE email LIKE '%.pt'")
    pt_emails = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    return {
        'total_customers': total_customers,
        'total_interactions': total_interactions,
        'pt_emails': pt_emails
    }


@app.route('/')
def index():
    """Homepage - display customers and interactions"""
    try:
        customers = get_customers()
        interactions = get_interactions()
        stats = get_stats()
        
        return render_template('index.html',
                             customers=customers,
                             interactions=interactions,
                             stats=stats)
    except Exception as e:
        return f"Error connecting to database: {str(e)}", 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'app': 'customer-viewer'})


@app.route('/ready')
def ready():
    """Readiness check - verifies database connection"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return jsonify({'status': 'ready', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'not ready', 'error': str(e)}), 503


@app.route('/api/customers')
def api_customers():
    """API endpoint - return customers as JSON"""
    try:
        customers = get_customers()
        return jsonify({'total': len(customers), 'customers': customers})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/interactions')
def api_interactions():
    """API endpoint - return interactions as JSON"""
    try:
        interactions = get_interactions()
        return jsonify({'total': len(interactions), 'interactions': interactions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)