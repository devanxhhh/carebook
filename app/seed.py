import logging
import sys
from app.db.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_admin():
    db = SessionLocal()
    try:
        admin_email = settings.ADMIN_EMAIL
        admin_password = settings.ADMIN_PASSWORD
        
        if not admin_email or not admin_password:
            logger.error("ADMIN_EMAIL and ADMIN_PASSWORD must be set in environment variables.")
            return

        admin_email = admin_email.lower()
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        
        if existing_admin:
            logger.info(f"Admin user {admin_email} already exists. Skipping.")
            return

        hashed_password = get_password_hash(admin_password)
        new_admin = User(
            name="Admin",
            email=admin_email,
            password_hash=hashed_password,
            role=UserRole.ADMIN
        )
        db.add(new_admin)
        db.commit()
        logger.info(f"Successfully seeded admin user: {admin_email}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to seed admin: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Starting admin seeding process...")
    seed_admin()
    logger.info("Seeding process completed.")
