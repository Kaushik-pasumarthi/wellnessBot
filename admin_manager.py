"""
Admin Management System for Wellness Bot
Handles admin authentication, dashboard, and management features
"""
import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class AdminManager:
    def __init__(self, db_path='admin.db', users_db_path='users.db'):
        self.db_path = db_path
        self.users_db_path = users_db_path
        self.init_admin_db()
        self.create_default_admin()
    
    def init_admin_db(self):
        """Initialize admin database with all required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Admin users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'admin',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT,
                feedback_type TEXT NOT NULL, -- 'bug', 'feature', 'general', 'rating'
                subject TEXT,
                message TEXT NOT NULL,
                rating INTEGER, -- 1-5 scale
                status TEXT DEFAULT 'new', -- 'new', 'reviewed', 'resolved', 'archived'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                admin_response TEXT,
                admin_id INTEGER,
                FOREIGN KEY (admin_id) REFERENCES admin_users (id)
            )
        ''')
        
        # Health tips table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_tips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT, -- 'general', 'diet', 'exercise', 'mental_health', etc.
                tags TEXT, -- JSON array of tags
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                FOREIGN KEY (created_by) REFERENCES admin_users (id)
            )
        ''')
        
        # Query analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT,
                query TEXT NOT NULL,
                intent TEXT,
                intent_confidence REAL,
                detected_symptoms TEXT, -- JSON array
                response_type TEXT, -- 'medical', 'general', 'fallback'
                session_id TEXT,
                response_time REAL, -- in seconds
                user_rating INTEGER, -- 1-5 if user rates the response
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # System metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_type TEXT, -- 'counter', 'gauge', 'histogram'
                tags TEXT, -- JSON object with additional metadata
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Admin database initialized successfully")
    
    def create_default_admin(self):
        """Create default admin user if none exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM admin_users")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            # Create default admin
            default_password = "admin123"  # Change this in production!
            password_hash = self.hash_password(default_password)
            
            cursor.execute('''
                INSERT INTO admin_users (username, password_hash, email, role)
                VALUES (?, ?, ?, ?)
            ''', ('admin', password_hash, 'admin@wellnessbot.com', 'superadmin'))
            
            conn.commit()
            print("✅ Default admin user created (username: admin, password: admin123)")
        
        conn.close()
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate_admin(self, username, password):
        """Authenticate admin user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        cursor.execute('''
            SELECT id, username, email, role, is_active 
            FROM admin_users 
            WHERE username = ? AND password_hash = ? AND is_active = 1
        ''', (username, password_hash))
        
        admin = cursor.fetchone()
        
        if admin:
            # Update last login
            cursor.execute('''
                UPDATE admin_users SET last_login = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (admin[0],))
            conn.commit()
            
            return {
                'id': admin[0],
                'username': admin[1],
                'email': admin[2],
                'role': admin[3],
                'is_active': admin[4]
            }
        
        conn.close()
        return None
    
    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        stats = {}
        
        # User statistics from users.db
        try:
            conn = sqlite3.connect(self.users_db_path)
            cursor = conn.cursor()
            
            # Total users
            cursor.execute("SELECT COUNT(*) FROM users")
            stats['total_users'] = cursor.fetchone()[0]
            
            # Users registered today
            cursor.execute("""
                SELECT COUNT(*) FROM users 
                WHERE DATE(created_at) = DATE('now')
            """)
            stats['users_today'] = cursor.fetchone()[0]
            
            # Users registered this week
            cursor.execute("""
                SELECT COUNT(*) FROM users 
                WHERE created_at >= datetime('now', '-7 days')
            """)
            stats['users_this_week'] = cursor.fetchone()[0]
            
            # Total conversations
            cursor.execute("SELECT COUNT(*) FROM conversations")
            stats['total_conversations'] = cursor.fetchone()[0]
            
            conn.close()
        except Exception as e:
            print(f"Error getting user stats: {e}")
            stats.update({
                'total_users': 0,
                'users_today': 0,
                'users_this_week': 0,
                'total_conversations': 0
            })
        
        # Admin database statistics
        admin_conn = sqlite3.connect(self.db_path)
        cursor = admin_conn.cursor()
        
        # Total feedback
        cursor.execute("SELECT COUNT(*) FROM feedback")
        stats['total_feedback'] = cursor.fetchone()[0]
        
        # Unresolved feedback
        cursor.execute("SELECT COUNT(*) FROM feedback WHERE status IN ('new', 'reviewed')")
        stats['pending_feedback'] = cursor.fetchone()[0]
        
        # Total health tips
        cursor.execute("SELECT COUNT(*) FROM health_tips WHERE is_active = 1")
        stats['active_health_tips'] = cursor.fetchone()[0]
        
        # Total queries today
        cursor.execute("""
            SELECT COUNT(*) FROM query_analytics 
            WHERE DATE(created_at) = DATE('now')
        """)
        stats['queries_today'] = cursor.fetchone()[0]
        
        admin_conn.close()
        
        return stats
    
    def log_query_analytics(self, user_email, query, intent, intent_confidence, 
                          detected_symptoms, response_type, session_id, response_time):
        """Log query analytics for admin dashboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO query_analytics 
            (user_email, query, intent, intent_confidence, detected_symptoms, 
             response_type, session_id, response_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_email, query, intent, intent_confidence, 
              json.dumps(detected_symptoms) if detected_symptoms else None,
              response_type, session_id, response_time))
        
        conn.commit()
        conn.close()
    
    def add_feedback(self, user_email, feedback_type, subject, message, rating):
        """Add user feedback"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO feedback (user_email, feedback_type, subject, message, rating)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_email, feedback_type, subject, message, rating))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return feedback_id
    
    def get_all_feedback(self, status=None):
        """Get all feedback with optional status filter"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
                SELECT * FROM feedback WHERE status = ? 
                ORDER BY created_at DESC
            ''', (status,))
        else:
            cursor.execute('SELECT * FROM feedback ORDER BY created_at DESC')
        
        feedback = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        columns = ['id', 'user_email', 'feedback_type', 'subject', 'message', 
                  'rating', 'status', 'created_at', 'admin_response', 'admin_id']
        return [dict(zip(columns, row)) for row in feedback]
    
    def update_feedback_status(self, feedback_id, status, admin_response=None, admin_id=None):
        """Update feedback status and admin response"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE feedback 
            SET status = ?, admin_response = ?, admin_id = ?
            WHERE id = ?
        ''', (status, admin_response, admin_id, feedback_id))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    def get_user_data(self):
        """Get all user data from users.db"""
        try:
            conn = sqlite3.connect(self.users_db_path)
            
            # Get users
            users_df = pd.read_sql_query("SELECT * FROM users", conn)
            
            # Get conversations
            conversations_df = pd.read_sql_query("""
                SELECT * FROM conversations 
                ORDER BY timestamp DESC LIMIT 1000
            """, conn)
            
            conn.close()
            
            return {
                'users': users_df,
                'conversations': conversations_df
            }
        except Exception as e:
            print(f"Error getting user data: {e}")
            return {'users': pd.DataFrame(), 'conversations': pd.DataFrame()}
    
    def get_query_analytics_data(self, days=30):
        """Get query analytics data for visualization"""
        conn = sqlite3.connect(self.db_path)
        
        query = f"""
            SELECT * FROM query_analytics 
            WHERE created_at >= datetime('now', '-{days} days')
            ORDER BY created_at DESC
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df

# Initialize admin manager
admin_manager = AdminManager()

if __name__ == "__main__":
    print("🏥 Admin Management System Initialized")
    print("✅ Default admin created: username='admin', password='admin123'")
    print("🔧 Database tables created successfully")