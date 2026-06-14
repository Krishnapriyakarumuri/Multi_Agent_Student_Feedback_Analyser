# database/auth.py - Authentication & User Management
import hashlib
from sqlalchemy.orm import sessionmaker
from config import config
from database.init_sql_models import User, Base
from sqlalchemy import create_engine

class AuthManager:
    """Manage user authentication and user database"""
    
    def __init__(self):
        self.engine = create_engine(config.DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self._create_default_users()
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _create_default_users(self):
        """Create default admin and viewer users if they don't exist"""
        session = self.Session()
        try:
            # Check if users exist
            admin_exists = session.query(User).filter_by(username="admin").first()
            viewer_exists = session.query(User).filter_by(username="viewer").first()
            
            if not admin_exists:
                admin_user = User(
                    username="admin",
                    password_hash=self._hash_password("admin123"),
                    role="admin"
                )
                session.add(admin_user)
                print("✅ Default admin user created (admin/admin123)")
            
            if not viewer_exists:
                viewer_user = User(
                    username="viewer",
                    password_hash=self._hash_password("viewer123"),
                    role="viewer"
                )
                session.add(viewer_user)
                print("✅ Default viewer user created (viewer/viewer123)")
            
            session.commit()
        except Exception as e:
            print(f"⚠️ Error creating default users: {e}")
        finally:
            session.close()
    
    def verify_user(self, username: str, password: str) -> dict:
        """
        Verify user credentials.
        
        Returns:
            dict with keys: user_id, username, role (on success)
            None (on failure)
        """
        session = self.Session()
        try:
            user = session.query(User).filter_by(username=username).first()
            
            if not user:
                return None
            
            password_hash = self._hash_password(password)
            if user.password_hash == password_hash:
                return {
                    "user_id": user.id,
                    "username": user.username,
                    "role": user.role
                }
            return None
        finally:
            session.close()
    
    def get_user(self, user_id: str) -> dict:
        """Get user details by ID"""
        session = self.Session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                return {
                    "user_id": user.id,
                    "username": user.username,
                    "role": user.role
                }
            return None
        finally:
            session.close()
    
    def create_user(self, username: str, password: str, role: str = "viewer") -> dict:
        """Create a new user"""
        session = self.Session()
        try:
            # Check if user exists
            existing = session.query(User).filter_by(username=username).first()
            if existing:
                return None  # User already exists
            
            user = User(
                username=username,
                password_hash=self._hash_password(password),
                role=role
            )
            session.add(user)
            session.commit()
            
            return {
                "user_id": user.id,
                "username": user.username,
                "role": user.role
            }
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
        finally:
            session.close()

# Global instance
auth_manager = AuthManager()
