from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
load_dotenv()



# Database URL from environment
DATABASE_URL = os.getenv("db_url") or os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fallback to local sqlite or a standard default if no DB URL is provided
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/Justice_nest"
    print("WARNING: 'db_url' or 'DATABASE_URL' not found in .env. Using fallback.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()
