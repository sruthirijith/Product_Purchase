from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship

from core.database.connection import Base
from sqlalchemy.orm import declarative_mixin
from core.utils.time import utc_time
from datetime import date


@declarative_mixin
class TimeStamp:
    created_at = Column(DateTime, default=utc_time(), nullable=False)
    updated_at = Column(DateTime, default=utc_time(), nullable=False)

#T1
class Users(TimeStamp,Base):

    __tablename__ = "users"
    id            = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    full_name     = Column(String(100), nullable=False)
    email         = Column(String(100), nullable=False, unique=True)
    password      = Column(String(200), nullable=False)
    phone_number  = Column(String(20), nullable=False, unique=True)
    user_role     = Column(String(20), nullable=False)


# class Roles(Base):
    
#     __tablename__ = "roles"
#     id = Column(Integer, primary_key=True)
#     role = Column(String(50), nullable=False)

#T2
class Pin(TimeStamp,Base):

    __tablename__= "pin"
    id           = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    users_id     = Column(Integer, ForeignKey('users.id'), nullable=False, primary_key=True)
    pin          = Column(Integer, nullable=False)
    users        = relationship("Users")
    __table_args__ = (
        UniqueConstraint("users_id", "pin", name="unique_user_pin"),
    )

#T3
class wallet(Base):

    __tablename__="wallet"
    id           = Column(Integer, primary_key=True, autoincrement=True)
    users_id     = Column(Integer, ForeignKey('users.id'), nullable=False, primary_key=True)
    amount       =Column(Integer, nullable=False)
    balance      = Column(Integer, nullable=False)
    date          =Column(String(50), nullable=False)

#T4

class product_details(TimeStamp,Base):

    __tablename__ ="product_details"
    id            = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    product_name  = Column(String(50),nullable=False)
    product_price = Column(Integer,nullable=False)
    product_stock = Column(Integer,nullable=False)
    

#T5

class purchase_info(Base):

    __tablename__ ="purchase_info"
    id            = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    users_id      =Column(Integer, ForeignKey('users.id'),nullable=False, primary_key=True)
    full_name     =Column(String(50), nullable=False)
    product_name  =Column(String(50), nullable=False)
    quantity      =Column(Integer,nullable=False)
    date          =Column(String(50), nullable=False)
    total_price   =Column(Integer, nullable=False)

#T6
class token(TimeStamp,Base):

    __tablename__ ="token"
    id            = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    users_id      =Column(Integer, ForeignKey('users.id'),nullable=False, primary_key=True)
    token         = Column(Integer ,nullable=False)

#T7
class membership_purchased(TimeStamp,Base):

    __tablename__  ="membership_purchased"
    id            = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    users_id      = Column(Integer, ForeignKey('users.id'),nullable=False, primary_key=True)
    plan          =Column(String(50),nullable=False)

#T8
class membership_plan(Base):

    __tablename__= "membership_plans"
    id            = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    plan          = Column(String(50),nullable=False)
    period        = Column(String(50),nullable=False)
    amount        = Column(Integer,nullable=False)

# T9
class transaction_log(Base):

    __tablename__="users_transaction"
    id            = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    users_id      = Column(Integer, ForeignKey('users.id'),nullable=False, primary_key=True)
    date          =Column(String(50), nullable=False)
    amount        = Column(Integer,nullable=False)
    balance       = Column(Integer, nullable=False)
    status        = Column(String(50),nullable=False)

   
    

    