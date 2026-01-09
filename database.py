import sqlite3
from datetime import datetime
import bcrypt
from typing import Optional, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserDatabase:
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            full_name TEXT,
            policy_number TEXT,
            role TEXT DEFAULT 'policyholder',
            google_id TEXT UNIQUE,
            is_verified INTEGER DEFAULT 0,
            mfa_enabled INTEGER DEFAULT 0,
            failed_login_attempts INTEGER DEFAULT 0,
            last_login TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Claims table (minimal for now)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            claim_type TEXT,
            claim_status TEXT DEFAULT 'pending',
            amount REAL,
            submitted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Create default admin user if not exists
        cursor.execute("SELECT * FROM users WHERE email = ?", ("admin@secureclaim.ai",))
        if not cursor.fetchone():
            admin_hash = bcrypt.hashpw("Admin@123".encode(), bcrypt.gensalt())
            cursor.execute('''
            INSERT INTO users (email, password_hash, full_name, role, is_verified)
            VALUES (?, ?, ?, ?, ?)
            ''', ("admin@secureclaim.ai", admin_hash.decode(), "System Administrator", "admin", 1))
            logger.info("Default admin user created")
        
        conn.commit()
        conn.close()
    
    def create_user(self, email: str, password: str, full_name: str, 
                   policy_number: Optional[str] = None, role: str = "policyholder") -> bool:
        """Create a new user with email/password"""
        try:
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO users (email, password_hash, full_name, policy_number, role, is_verified)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (email, password_hash.decode(), full_name, policy_number, role, 0))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            logger.error(f"User with email {email} already exists")
            return False
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False
    
    def create_google_user(self, email: str, google_id: str, full_name: str, 
                          role: str = "policyholder") -> bool:
        """Create/update user from Google OAuth"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user exists by email
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            existing = cursor.fetchone()
            
            if existing:
                # Update Google ID if not set
                cursor.execute('''
                UPDATE users SET google_id = ?, is_verified = 1, updated_at = CURRENT_TIMESTAMP
                WHERE email = ?
                ''', (google_id, email))
            else:
                # Create new user
                cursor.execute('''
                INSERT INTO users (email, google_id, full_name, role, is_verified)
                VALUES (?, ?, ?, ?, ?)
                ''', (email, google_id, full_name, role, 1))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error creating Google user: {e}")
            return False
    
    def verify_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Verify email/password login"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT id, email, password_hash, full_name, role, policy_number, 
                   is_verified, failed_login_attempts, mfa_enabled
            FROM users 
            WHERE email = ? AND password_hash IS NOT NULL
            ''', (email,))
            
            user = cursor.fetchone()
            if not user:
                return None
            
            # Check if account is locked
            if user[7] >= 5:  # failed_login_attempts
                logger.warning(f"Account locked for {email}")
                return None
            
            # Verify password
            if bcrypt.checkpw(password.encode(), user[2].encode()):
                # Reset failed attempts on successful login
                cursor.execute('''
                UPDATE users 
                SET failed_login_attempts = 0, last_login = CURRENT_TIMESTAMP
                WHERE email = ?
                ''', (email,))
                
                user_data = {
                    "id": user[0],
                    "email": user[1],
                    "full_name": user[3],
                    "role": user[4],
                    "policy_number": user[5],
                    "is_verified": bool(user[6]),
                    "mfa_enabled": bool(user[8]),
                    "auth_method": "email"
                }
                conn.commit()
                conn.close()
                return user_data
            else:
                # Increment failed attempts
                cursor.execute('''
                UPDATE users 
                SET failed_login_attempts = failed_login_attempts + 1
                WHERE email = ?
                ''', (email,))
                conn.commit()
                conn.close()
                return None
                
        except Exception as e:
            logger.error(f"Error verifying user: {e}")
            return None
    
    def get_user_by_google_id(self, google_id: str) -> Optional[Dict[str, Any]]:
        """Get user by Google ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT id, email, full_name, role, policy_number, is_verified
            FROM users 
            WHERE google_id = ?
            ''', (google_id,))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return {
                    "id": user[0],
                    "email": user[1],
                    "full_name": user[2],
                    "role": user[3],
                    "policy_number": user[4],
                    "is_verified": bool(user[5]),
                    "auth_method": "google"
                }
            return None
        except Exception as e:
            logger.error(f"Error getting Google user: {e}")
            return None
    
    def update_user_last_login(self, user_id: int):
        """Update user's last login timestamp"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
            UPDATE users SET last_login = CURRENT_TIMESTAMP
            WHERE id = ?
            ''', (user_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error updating last login: {e}")

# Global database instance
db = UserDatabase()
