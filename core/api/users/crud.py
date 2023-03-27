from bson.objectid import ObjectId
from fastapi.security import OAuth2PasswordBearer
from hashids import Hashids
from sqlalchemy import and_
from sqlalchemy.orm import Session, load_only
from passlib.context import CryptContext
from datetime import date

from config.base import settings
from core.api.users import models, schema
# from core.api.consumer.models import FollowedSocialMedia
from core.database.connection import get_db
from core.utils import password, time


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user_email_login")
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
secret = settings.JWT_SECRET_KEY
ALGORITHM = settings.ALGORITHM




def create_user(db: Session, user:schema.UsersBase ):
    db_user = models.Users(
        full_name    =user.full_name,
        email        =user.email,
        password     =user.password,
        phone_number =user.phone_number,
        user_role    =user.role_id
    )
    db.add(db_user)
    db.commit()
    db_wallet = models.wallet(
        users_id  = db_user.id,
        balance   =0,
        amount    =0,
        date = date.today()
    )
    db.add(db_wallet)
    db.commit()
    db_token = models.token(
        users_id = db_user.id,
        token = 1
        )
    db.add(db_token)
    db.commit()
    return db_user, db_wallet, db_token


def add_product(db:Session, user:dict):
    db_product= models.product_details(
        product_name  = user.product_name,
        product_price = user.product_price,
        product_stock = user.product_stock,
        
    )
    db.add(db_product)
    db.commit()
    return db_product

def find_plan(db:Session,plan: str):
    db_plan = db.query(models.membership_plan).filter(models.membership_plan.plan==plan).first()
    return db_plan
    
def get_user_by_email(db: Session, email: str):
    return db.query(models.Users).options(load_only(
            "id", "full_name", "email", "phone_number","user_role"
        )).filter(models.Users.email == email).first()


def get_user_by_phonenumber(db: Session, phone_number: str):
    return db.query(models.Users).options(load_only(
            "id", "full_name", "email", "phone_number"
        )).filter(models.Users.phone_number == phone_number).first()


def verify_email_password(db:Session , email:str ,password:str):
    userinfo = db.query(models.Users).filter(models.Users.email==email, models.Users.password==password).first()
    if userinfo:
        return userinfo

def add_pin(db:Session,pin:str, users_id: str):
    db_pin=models.Pin(
            pin=pin,
            users_id=users_id
        )
    db.add(db_pin)
    db.commit()
    return(db_pin)
    

def get_user_role_one(db:Session, user_role: int):
    return db.query(models.Users).filter(models.Users.user_role == user_role).first    

def get_by_user_id(db:Session, users_id: int):    
    return db.query(models.wallet).filter(models.wallet.users_id==users_id).first()    

def verify_pin_by_id(db : Session, users_id:int):
    return db.query(models.Pin).filter(models.Pin.users_id == users_id).first()
    
def update_wallet(db: Session, users_id: int, add_amount:int, date: str):
    fetch_id = db.query(models.wallet).filter(models.wallet.users_id==users_id).first()
    fetch_balance = fetch_id.__dict__['balance']
    wallet_by_date = date.today()
    final_amount = fetch_balance + add_amount
    db_wallet=db.query(models.wallet).filter(models.wallet.users_id==users_id).update(
        {"balance":final_amount,"date":wallet_by_date,"amount":add_amount})
    db.commit()
    if db_wallet:
        db_transaction = models.transaction_log(
                        users_id      = users_id,
                        date          = wallet_by_date,
                        amount        = add_amount,
                        balance       = final_amount,
                        status        = "credited"
        )
        db.add(db_transaction)
        db.commit() 
        return db_wallet, db_transaction

def update_token(db:Session,users_id:int,total_price:int):
    fetch_id = db.query(models.token).filter(models.token.users_id==users_id).first()
    fetch_token = fetch_id.__dict__['token']
    if total_price > 600:
        new_token = fetch_token +5
        db.query(models.token).filter(models.token.users_id==users_id).update({"token":new_token})
        db.commit()
        return True
    
def update_product_details(db:Session,product:schema.add_product):
    db.query(models.product_details).filter(models.product_details.product_name==product.product_name).update(
        {"product_price":product.product_price,"product_stock":product.product_stock}
    )
    db.commit()
    return True
    

def purchase_info(db: Session,quantity:int, users_id:int, full_name: str, 
                  product_name: str, date: str, total_price: int):
    fetch_wallet = get_by_user_id(db=db, users_id=users_id)
    balance = fetch_wallet.__dict__['balance']
    balance_after_debit = balance-total_price
    db_product= models.purchase_info(
                users_id      =users_id,
                full_name     =full_name,
                product_name  =product_name,
                quantity      =quantity,
                date          =date,
                total_price   =total_price
    )
    db.add(db_product)
    db.commit()
    if purchase_info:
        db_transaction = models.transaction_log(
                  users_id      = users_id,
                  date          =date,
                  amount        =total_price,
                  balance       = balance_after_debit,
                  status        = "debited"
        )
        db.add(db_transaction)
        db.commit()
        if db_transaction:
            new_wallet= db.query(models.wallet).filter(models.wallet.users_id==users_id).update({"balance":balance_after_debit})
            db.commit()
            return db_product, db_transaction, new_wallet

def add_membership(db:Session,users_id: int,plan: str):
    db_membership = models.membership_purchased(
        users_id = users_id,
        plan = plan,
        created_at=time.utc_time(),
        updated_at=time.utc_time(),
    )
    db.add(db_membership)
    db.commit()
    return db_membership

def check_balance(db: Session, total_price: int, users_id:int):
   get_user = db.query(models.wallet).filter(models.wallet.users_id==users_id).first()
   balance = get_user.__dict__['balance']
   if balance > total_price :
       return True
       
  
    
def verify_product(db:Session, product_name: str):
    return db.query(models.product_details).filter(models.product_details.product_name==product_name).first()
    
def verify_stock(db : Session, quantity : str):
    return db.query(models.product_details).filter(models.product_details.product_stock >= quantity).first()    

def delete_product(db:Session, product_name:str):
    db.query(models.product_details).filter(models.product_details.product_name ==product_name).first()
    db.delete()
    db.commit()
    return True