import uuid
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Date, Boolean, DECIMAL, JSON, ARRAY, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, TEXT, TIMESTAMP
from datetime import datetime

password = "u3KrUSJDaEgJqZ89"

DATABASE_URL = f"postgresql://postgres.tgsstxvgndqcwwiraxdb:{password}@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"

Base = declarative_base()

engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine)
session = Session()

class User_Goals(Base):
    __tablename__ = "users"
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(50))
    email = Column(String(50))
