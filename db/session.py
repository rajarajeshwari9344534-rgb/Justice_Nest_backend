from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
load_dotenv()



engine=create_engine(os.getenv("db_url"))
SessionLocal= sessionmaker(autoflush=False,autocommit=False,bind=engine)


Base=declarative_base()