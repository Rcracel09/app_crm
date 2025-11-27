"""
CRM App Backend - FastAPI
Serves React frontend + API endpoints
Connects to database_crm PostgreSQL
"""
import os
import psycopg2
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CRM App API")

# CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration from environment
DB_HOST = os.getenv('DB_HOST', 'database-crm')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'demo_db')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres123')

logger.info(f"Database config: {DB_HOST}:{DB_PORT}/{DB_NAME}")


def get_db_connection():
    """Create database connection"""
    try:
        return psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise


# API Endpoints
@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "app": "crm-app"}


@app.get("/api/ready")
def readiness_check():
    """Readiness check - verifies database connection"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")


@app.get("/api/customers")
def get_customers() -> Dict[str, Any]:
    """Get all customers"""
    try:
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
                'created_at': row[7].isoformat() if row[7] else None
            })
        
        cursor.close()
        conn.close()
        
        logger.info(f"Retrieved {len(customers)} customers")
        return {"total": len(customers), "customers": customers}
    
    except Exception as e:
        logger.error(f"Error fetching customers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/interactions")
def get_interactions() -> Dict[str, Any]:
    """Get all interactions with customer names"""
    try:
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
            JOIN customers c ON i.custom_id = c.id
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
                'created_at': row[6].isoformat() if row[6] else None
            })
        
        cursor.close()
        conn.close()
        
        logger.info(f"Retrieved {len(interactions)} interactions")
        return {"total": len(interactions), "interactions": interactions}
    
    except Exception as e:
        logger.error(f"Error fetching interactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
def get_stats() -> Dict[str, Any]:
    """Get database statistics"""
    try:
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
    
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Serve React static files (after build)
# This will be mounted only if /app/static exists (production)
try:
    app.mount("/assets", StaticFiles(directory="/app/static/assets"), name="assets")
    
    @app.get("/{full_path:path}")
    def serve_react(full_path: str):
        """Serve React app for all other routes"""
        return FileResponse("/app/static/index.html")
    
    logger.info("Serving React static files from /app/static")
except RuntimeError:
    logger.warning("Static directory not found - API only mode")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=False)