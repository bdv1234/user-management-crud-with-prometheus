from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from typing import List, Optional
from opentelemetry import trace
from app.logging.logging import app_logger
from app.elasticsearch.client import es_client

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("UserService.create_user"):
            db_user = User(**user_data.dict())
            try:
                self.db.add(db_user)
                self.db.commit()
                self.db.refresh(db_user)
                
                # Log user creation
                app_logger.info(
                    "User created",
                    user_id=db_user.id,
                    username=db_user.username,
                    email=db_user.email
                )
                
                # Log to Elasticsearch
                es_client.log_user_action(
                    user_id=db_user.id,
                    action="user_created",
                    details={
                        "username": db_user.username,
                        "email": db_user.email,
                        "full_name": db_user.full_name,
                        "is_active": db_user.is_active
                    }
                )
                
                return db_user
            except IntegrityError:
                self.db.rollback()
                app_logger.error(
                    "User creation failed - duplicate username or email",
                    username=user_data.username,
                    email=user_data.email
                )
                raise ValueError("username or email already exists")

    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get list of users with pagination"""
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user by ID"""
        db_user = self.get_user(user_id)
        if not db_user:
            return None
        
        # Store original values for logging
        original_data = {
            "username": db_user.username,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "is_active": db_user.is_active
        }
        
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)

        try:
            self.db.commit()
            self.db.refresh(db_user)
            
            # Log user update
            app_logger.info(
                "User updated",
                user_id=user_id,
                updated_fields=list(update_data.keys())
            )
            
            # Log to Elasticsearch
            es_client.log_user_action(
                user_id=user_id,
                action="user_updated",
                details={
                    "original_data": original_data,
                    "updated_data": update_data
                }
            )
            
            return db_user
        except IntegrityError:
            self.db.rollback()
            app_logger.error(
                "User update failed - duplicate username or email",
                user_id=user_id,
                update_data=update_data
            )
            raise ValueError("Username or email already exists")
        
    def delete_user(self, user_id: int) -> bool:
        """Delete user by ID"""
        db_user = self.get_user(user_id)
        if not db_user:
            return False
        
        # Store user data for logging before deletion
        user_data = {
            "username": db_user.username,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "is_active": db_user.is_active
        }
        
        self.db.delete(db_user)
        self.db.commit()
        
        # Log user deletion
        app_logger.info(
            "User deleted",
            user_id=user_id,
            username=user_data["username"]
        )
        
        # Log to Elasticsearch
        es_client.log_user_action(
            user_id=user_id,
            action="user_deleted",
            details=user_data
        )
        
        return True
    
    def get_users_count(self) -> int:
        """Get total count of users"""
        return self.db.query(User).count()
