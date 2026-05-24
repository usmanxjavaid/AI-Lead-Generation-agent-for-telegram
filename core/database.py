import sqlite3
import os
import csv
try:
    from core.logger import logger 
except ImportError:
    from logger import logger  
from datetime import datetime

DB_FILE = "Database.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    # this makes rows behave like dictionaries
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create all tables when bot starts"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            name TEXT,
            email TEXT,
            phone TEXT,
            service TEXT,
            requirement TEXT,
            status TEXT DEFAULT 'new',
            created_at TEXT            
            )
            ''')
    
    conn.commit()
    conn.close()
    logger.info('Database initialized')

def save_lead(telegram_id: int, name: str, email: str,
              phone: str, service: str, requirement: str):
    """Saves a new lead to database"""

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT OR REPLACE INTO leads 
            (telegram_id, name, email, phone, service, requirement, status, created_at)
            VALUES(?, ?, ?, ?, ?, ?, 'new', ?)   
        ''', (telegram_id, name, email, phone, service, 
            requirement, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        conn.commit()
        logger.info(f"New lead saved: {name} ({email})")
        return True
    
    except Exception as e:
        logger.error(f"Failed to save lead: {e}")
        return False
    
    finally:
        conn.close()

def get_all_leads():
    """Returns all leads for admin"""
    conn =get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM leads ORDER BY created_at DESC')
    leads = cursor.fetchall()
    conn.close()
    return leads

def get_lead_by_telegram_id(telegram_id: int):
    """Returns a specific lead"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM leads WHERE telegram_id = ?',
                (telegram_id,))
    lead = cursor.fetchone()
    conn.close()
    return lead

def update_lead_status(telegram_id: int, status: str):
    """Updates lead status.
       status options: new, contacted, converted
       """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            UPDATE leads SET status = ? WHERE telegram_id = ?
        ''', (status, telegram_id))
        conn.commit()
        logger.info(f"Lead {telegram_id} status updated to: {status}")
        return True
    except Exception as e:
        logger.error(f"Failed to update status: {e}")
        return False
    finally:
        conn.close()

def get_stats():
    """Returns lead statistics for admin panel"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM leads')
    total = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM leads WHERE status = "new"')
    new = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM leads WHERE status = "contacted"')
    contacted = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM leads WHERE status = "converted"')
    converted = cursor.fetchone()[0]

    conn.close()
    return total, new, contacted, converted

def export_leads_csv():
    """
    Exports all leads to a CSV file.
    Admin can download this and open in excel
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM leads ORDER BY created_at DESC')
    leads = cursor.fetchall()
    conn.close()

    # create exports folder if not exists
    os.makedirs("lead_exports", exist_ok=True)

    filename = f"lead_exports/leads_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Header row
        writer.writerow(['ID', 'Telegram ID', 'Name', 'Email',
                         'Phone', 'Service', 'Requirement', 'Status', 'Created At'])
        # Data rows
        for lead in leads:
            writer.writerow(list(lead))

    logger.info(f"Leads exported to {filename}")
    return filename

