import hashlib
import secrets
import mysql.connector
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, session
from config import Config

class AuthManager:
    def __init__(self):
        self.db_config = Config.DB_CONFIG
        
    def init_auth_tables(self):
        """Initialize authentication tables"""
        try:
            conn = mysql.connector.connect(
                host=self.db_config['host'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            cursor = conn.cursor()
            
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS flashcards_db")
            cursor.execute("USE flashcards_db")
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR(36) PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    salt VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL
                )
            """)
            
            # Create user_sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id VARCHAR(36) PRIMARY KEY,
                    user_id VARCHAR(36) NOT NULL,
                    session_token VARCHAR(255) UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # Update flashcards table to include user_id
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS flashcards (
                    id VARCHAR(36) PRIMARY KEY,
                    user_id VARCHAR(36) NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    subject VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # Update study_sessions table to include user_id
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS study_sessions (
                    id VARCHAR(36) PRIMARY KEY,
                    user_id VARCHAR(36) NOT NULL,
                    session_name VARCHAR(200),
                    flashcard_ids JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ Authentication tables created successfully!")
            return True
            
        except mysql.connector.Error as e:
            print(f"❌ Database setup error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def hash_password(self, password, salt=None):
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return salt, password_hash.hex()
    
    def verify_password(self, password, stored_hash, stored_salt):
        """Verify password against stored hash"""
        _, computed_hash = self.hash_password(password, stored_salt)
        return computed_hash == stored_hash
    
    def register_user(self, username, email, password):
        """Register a new user"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Check if username or email already exists
            cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
            if cursor.fetchone():
                return False, "Username or email already exists"
            
            # Create new user
            user_id = secrets.token_urlsafe(32)
            salt, password_hash = self.hash_password(password)
            
            cursor.execute("""
                INSERT INTO users (id, username, email, password_hash, salt)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, username, email, password_hash, salt))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True, user_id
            
        except mysql.connector.Error as e:
            print(f"Database error during registration: {e}")
            return False, "Database error"
        except Exception as e:
            print(f"Unexpected error during registration: {e}")
            return False, "Registration failed"
    
    def login_user(self, username, password):
        """Authenticate user and create session"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
            
            # Get user by username
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            
            if not user:
                return False, "Invalid username or password"
            
            # Verify password
            if not self.verify_password(password, user['password_hash'], user['salt']):
                return False, "Invalid username or password"
            
            # Create session
            session_token = secrets.token_urlsafe(32)
            session_id = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(days=7)
            
            cursor.execute("""
                INSERT INTO user_sessions (id, user_id, session_token, expires_at)
                VALUES (%s, %s, %s, %s)
            """, (session_id, user['id'], session_token, expires_at))
            
            # Update last login
            cursor.execute("UPDATE users SET last_login = NOW() WHERE id = %s", (user['id'],))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True, {
                'user_id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'session_token': session_token
            }
            
        except mysql.connector.Error as e:
            print(f"Database error during login: {e}")
            return False, "Database error"
        except Exception as e:
            print(f"Unexpected error during login: {e}")
            return False, "Login failed"
    
    def verify_session(self, session_token):
        """Verify session token and return user info"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
            
            # Get session and user info
            cursor.execute("""
                SELECT us.*, u.username, u.email 
                FROM user_sessions us
                JOIN users u ON us.user_id = u.id
                WHERE us.session_token = %s AND us.expires_at > NOW()
            """, (session_token,))
            
            session_data = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if not session_data:
                return None
            
            return {
                'user_id': session_data['user_id'],
                'username': session_data['username'],
                'email': session_data['email']
            }
            
        except mysql.connector.Error as e:
            print(f"Database error during session verification: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error during session verification: {e}")
            return None
    
    def logout_user(self, session_token):
        """Logout user by removing session"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM user_sessions WHERE session_token = %s", (session_token,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
            
        except mysql.connector.Error as e:
            print(f"Database error during logout: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error during logout: {e}")
            return False

# Global auth manager instance
auth_manager = AuthManager()

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not session_token:
            return jsonify({'error': 'Authentication required'}), 401
        
        user = auth_manager.verify_session(session_token)
        if not user:
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        # Add user info to request context
        request.user = user
        return f(*args, **kwargs)
    
    return decorated_function

