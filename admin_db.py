import sqlite3
import bcrypt
import streamlit as st
from datetime import datetime

class AdminDatabase:
    def __init__(self):
        self.db_path = "admin_users.db"
        self.init_database()
    
    def init_database(self):
        """Initialize admin database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Admin users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        ''')
        
        # Default admin if not exists
        cursor.execute("SELECT * FROM admins WHERE username = ?", ("admin",))
        if not cursor.fetchone():
            # Default password: Admin@123
            password_hash = bcrypt.hashpw("Admin@123".encode(), bcrypt.gensalt())
            cursor.execute('''
            INSERT INTO admins (username, password_hash, full_name, email, role)
            VALUES (?, ?, ?, ?, ?)
            ''', ("admin", password_hash.decode(), "System Administrator", "admin@irmc-insureai.com", "superadmin"))
        
        conn.commit()
        conn.close()
    
    def create_admin(self, username: str, password: str, full_name: str, email: str, role: str = "admin") -> bool:
        """Create new admin user"""
        try:
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO admins (username, password_hash, full_name, email, role)
            VALUES (?, ?, ?, ?, ?)
            ''', (username, password_hash.decode(), full_name, email, role))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"Error creating admin: {e}")
            return False
    
    def authenticate_admin(self, username: str, password: str) -> dict:
        """Authenticate admin user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT id, username, password_hash, full_name, email, role
            FROM admins WHERE username = ?
            ''', (username,))
            
            result = cursor.fetchone()
            
            if result and bcrypt.checkpw(password.encode(), result[2].encode()):
                # Update last login
                cursor.execute('''
                UPDATE admins SET last_login = ? WHERE username = ?
                ''', (datetime.now(), username))
                conn.commit()
                
                admin_data = {
                    "id": result[0],
                    "username": result[1],
                    "full_name": result[3],
                    "email": result[4],
                    "role": result[5],
                    "is_admin": True
                }
                conn.close()
                return admin_data
            
            conn.close()
            return None
        except Exception as e:
            print(f"Admin auth error: {e}")
            return None
    
    def get_all_admins(self):
        """Get all admin users"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, full_name, email, role, last_login FROM admins")
            admins = cursor.fetchall()
            conn.close()
            return admins
        except Exception as e:
            print(f"Error getting admins: {e}")
            return []

# Global admin database instance
admin_db = AdminDatabase()
