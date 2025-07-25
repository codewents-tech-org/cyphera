import os
import logging
import logging.config
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from controllers.tablemodel import ActivityLog
import models.Parameters as P

# ---------------------------------------------------------------------
# Directory and Log File Setup
# ---------------------------------------------------------------------
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILENAME = os.path.join(LOG_DIR, f'tara_{datetime.now().strftime("%Y%m%d")}.log')
ERROR_LOG_FILENAME = os.path.join(LOG_DIR, "error.log")

# ---------------------------------------------------------------------
# Logger Configuration Dictionary
# ---------------------------------------------------------------------
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s | %(levelname)s | %(message)s"
        }
    },
    "handlers": {
        "file_info": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": LOG_FILENAME,
            "formatter": "standard"
        },
        "file_error": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": ERROR_LOG_FILENAME,
            "formatter": "standard"
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard"
        }
    },
    "loggers": {
        "tara": {
            "handlers": ["file_info", "file_error", "console"],
            "level": "INFO",
            "propagate": False
        }
    }
}

# ---------------------------------------------------------------------
# Dynamic DB Session Retrieval (Safe Delayed Init)
# ---------------------------------------------------------------------
def get_logger_engine_and_session():
    """
    Safely create SQLAlchemy engine and session only if URL is set.
    """
    db_url = getattr(P, "SQLALCHEMY_DATABASE_URL", "")
    if not db_url or not db_url.startswith("postgresql://"):
        print("logger_config: SQLALCHEMY_DATABASE_URL not set or invalid. Skipping DB log write.")
        return None, None
    engine = create_engine(db_url, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal


# ---------------------------------------------------------------------
# Activity Logging Function
# ---------------------------------------------------------------------
def log_activity(action_type, module, entity_id, performed_by, description):
    """
    Logs activity to both the database and the log file.
    """
    logger.info("Activity logged: %s on %s by %s", action_type, module, performed_by)

    engine, SessionLocal = get_logger_engine_and_session()
    if not SessionLocal:
        return  # Avoid DB write if DB not initialized

    try:
        session = SessionLocal()
        log_entry = ActivityLog(
            action_type=action_type,
            module=module,
            entity_id=str(entity_id),
            performed_by=performed_by,
            description=description,
            timestamp=datetime.now()
        )
        session.add(log_entry)
        session.commit()
    except Exception as exc:
        logger.error("Failed to write log entry to DB: %s", exc)
    finally:
        if 'session' in locals():
            session.close()


# ---------------------------------------------------------------------
# CRUD Logging Decorator
# ---------------------------------------------------------------------
def log_crud_action(action_type, module_name_getter, entity_id_getter):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                module = module_name_getter(*args, **kwargs) or "-"
                entity_id = entity_id_getter(result, *args, **kwargs) or "-"
                log_activity(
                    action_type, module, entity_id,
                    performed_by="system",
                    description=f"{action_type} via decorator"
                )
                return result
            except Exception as exc:
                logger.error(" CRUD logging failed: %s", exc)
                raise
        return wrapper
    return decorator


# ---------------------------------------------------------------------
# Setup Logging Entry Point
# ---------------------------------------------------------------------
def setup_logging():
    """
    Initializes and returns a structured logger using predefined config.

    Returns:
        logging.Logger: Configured logger instance
    """
    logging.config.dictConfig(LOGGING_CONFIG)
    return logging.getLogger("tara")


# ---------------------------------------------------------------------
# Global logger for import
# ---------------------------------------------------------------------
logger = setup_logging()
