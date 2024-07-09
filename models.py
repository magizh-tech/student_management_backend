from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base




engine=create_engine('sqlite:///db.sqlite3')
Base=declarative_base()

class User(Base):
    __tablename__='users'
    id=Column(Integer, primary_key=True)
    username=Column(String)
    password=Column(String)
    email=Column(String,unique=True)
    date_of_joining=Column(String)
    phone_number=Column(String,unique=True)
    address=Column(String)

Base.metadata.create_all(engine)