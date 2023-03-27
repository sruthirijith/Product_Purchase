from typing import Any
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, UploadFile, Form
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import date

from config.base import settings
from core.database.connection import get_db, engine, Base
from core.api.users import schema, crud, models
from core.jwt import auth_handler
from core.jwt.auth_bearer import JWTBearer
# from core.api.users import user_api

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Product purchase")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(user_api.router)

# @app.get("/")
# async def home():
#     return {"Happy shopping"}
#1
@app.post("/register", status_code=201)
async def create_user(user: schema.UsersBase, db: Session = Depends(get_db)):
    if user.role_id in [1,2]:
        db_user: Any = crud.get_user_by_email(db=db, email=user.email)
        if db_user:
            raise HTTPException(
                    status_code=200,
                    detail={
                        "status": "Error",
                        "status_code": 200,
                        "data": None,
                        "error": {
                            "status_code": 200,
                            "status": "Error",
                            "message": "Email already registered"
                        }
                    }
                )
        
        reg_phone:Any= crud.get_user_by_phonenumber(db=db,phone_number=user.phone_number)
        if reg_phone:
            raise HTTPException(
                status_code=200,
                detail={
                    "status": "Error",
                    "status_code": 200,
                    "data": None,
                    "error": {
                        "status_code": 200,
                        "status": "Error",
                        "message": "Phone number already registered"
                    }
                }
            )
        if (user.role_id ==1):
            role="staff"
        role = "customer"
        created_user = crud.create_user(db=db, user=user)
        response = {
            "detail": {
                "status": "Success",
                "status_code": 201,
                "data": {
                    "status_code": 201,
                    "status": "Success",
                    "message": "User registered Successfully",
                    # "username": created_user.__dict__['full_name'],
                    # "phonenumber": created_user.__dict__['phone_number'],
                    "role":role,
                    "role_id":user.role_id
                    },
                    "error": None
                }
            }
        return response
    else:
        raise HTTPException(
                status_code=500,
                detail={
                    "status": "Error",
                    "status_code": 500,
                    "data": None,
                    "error": {
                        "status_code": 500,
                        "status": "Error",
                        "message": "Only Consumer or Merchant can register"
                    }
                }
        )
#2    
@app.post("/user_email_login")  
async def user_login(user:schema.login, db:Session=Depends(get_db)):
    verify_user= crud.verify_email_password(db=db, email=user.email, password=user.password)
    if verify_user:
        token = auth_handler.encode_token(verify_user.email)
        refresh_token = auth_handler.refresh_token(verify_user.email)
        users_id = verify_user.__dict__['id']
        users_role = verify_user.__dict__['user_role']
        return {
                "detail": {
                        "status": "Success",
                        "status_code": 200,
                        "data": {
                            "status_code": 200,
                            "status": "Success",
                                "message": "User Logged in Successfully",
                                "access_token": token, "token_type": "bearer",
                                "refresh_token": refresh_token, "token_type": "bearer",
                               
                                "email": verify_user.__dict__['email'],
                                "users_id":users_id,
                                "role":users_role,
                               
                            },
                            "error": None
                        }
                    }
    else:
        raise HTTPException(
                    status_code = 401, 
                    detail={
                        "status": "Error",
                        "status_code": 401,
                        "data": None,
                        "error": {
                            "status_code": 401,
                            "status": "Error",
                            "message": "Login failed! Invalid credentials"
                        }
                    }
                )
#3    
@app.post('/add_pin', dependencies=[Depends(JWTBearer())])
def add_pin(data: schema.add_pin, token = Depends(JWTBearer()), db : Session=Depends(get_db)):
    email = auth_handler.decode_token(token=token)
    userdata = crud.get_user_by_email(db=db, email=email['sub'])
    # user_email = userdata.__dict__['email']
    users_id= userdata.__dict__['id']
    # print(users_id)
    if userdata:
        if ((len(data.pin) and len(data.reenter_pin))==4) and data.pin.isnumeric():
            # if userdata.__dict__['pin'] is None:         
            if (data.pin == data.reenter_pin):
                confirm_pin = crud.add_pin(db = db, pin = data.pin, users_id=users_id)
                if confirm_pin:
                    return {
                            "detail": {
                                "status": "Success",
                                "status_code": 200,
                                "data": {
                                    "status_code": 200,
                                    "status": "Success",
                                    "message": "Pin added Successfully",
                                    "users_id":users_id,
                                },
                                "error": None
                            }
                        } 
                else:
                    raise HTTPException(
                            status_code = 409,
                            detail = {
                                "status": "Error",
                                "status_code" : 409,
                                "data": None,
                                "error" : {
                                    "status_code" : 409,
                                    "status":"Error",
                                    "message" : "Error while adding pin",
                                }
                            },
                        )
                         
            else:
                raise HTTPException(
                        status_code = 409,
                        detail = {
                            "status": "Error",
                            "status_code" : 409,
                            "data": None,
                            "error" : {
                                "status_code" : 409,
                                "status":"Error",
                                "message" : "Two pin must be same",
                            }
                        },
                    )
           
        else:
            raise HTTPException(
                status_code = 411,
                detail = {
                    "status": "Error",
                    "status_code" : 411,
                    "data": None,
                    "error" : {
                        "status_code" : 411,
                        "status":"Error",
                        "message" : "Length of pin must be equal to 4 and numeric",
                    }
                },
            )  
    else:
        raise HTTPException(
            status_code = 404,
            detail = {
                "status": "Error",
                "status_code" : 404,
                "data": None,
                "error" : {
                    "status_code" : 404,
                    "status":"Error",
                    "message" : "No user found",
                }
            },
        )      
# 4
@app.post('/add_wallet', dependencies=[Depends(JWTBearer())])
def add_money(data: schema.add_wallet, token = Depends(JWTBearer()), db : Session=Depends(get_db)):
    email = auth_handler.decode_token(token=token)
    userdata = crud.get_user_by_email(db=db, email=email['sub'])
    users_id= userdata.__dict__['id']
    if userdata:
        check_user_id = crud.verify_pin_by_id(db=db,  users_id=users_id)
        if check_user_id:
            get_pin = check_user_id.__dict__['pin']
            if get_pin == data.pin :
                wallet_by_date = date.today()
                update_balance = crud.update_wallet(db=db,users_id=users_id,add_amount=data.amount,
                                                    date=wallet_by_date)
                if update_balance:
                    return {
                            "detail": {
                                "status": "Success",
                                "status_code": 200,
                                "data": {
                                    "status_code": 200,
                                    "status": "Success",
                                    "message": "money added Successfully",
                                    "users_id":users_id,
                                },
                                "error": None
                            }
                        }
                else:
                     raise HTTPException(
                            status_code = 409,
                            detail = {
                                "status": "Error",
                                "status_code" : 409,
                                "data": None,
                                "error" : {
                                    "status_code" : 409,
                                    "status":"Error",
                                    "message" : "Error while adding money",
                                }
                            },
                        )
            else:
                raise HTTPException(
                status_code = 404,
                detail = {
                "status": "Error",
                "status_code" : 404,
                "data": None,
                "error" : {
                    "status_code" : 404,
                    "status":"Error",
                    "message" : "pin entered is incorrect",
                }
            },
        ) 
    else:
        raise HTTPException(
            status_code = 404,
            detail = {
                "status": "Error",
                "status_code" : 404,
                "data": None,
                "error" : {
                    "status_code" : 404,
                    "status":"Error",
                    "message" : "no user found",
                }
            },
        )  
#5 to add product details by staff
@app.post("/produtc_details_by_staff")
async def add_products(data:schema.add_product, token = Depends(JWTBearer()), db : Session=Depends(get_db)):
    email = auth_handler.decode_token(token=token)
    userdata = crud.get_user_by_email(db=db, email=email['sub'])
    users_role= userdata.__dict__['user_role']
    # print(users_role)
    if userdata:
        if users_role == "1":
            product_details=crud.add_product(db=db, user=data)
            print(product_details.product_name)
            if product_details:
                return{
                    "detail": {
                    "status": "Success",
                    "status_code": 201,
                    "data": {
                        "status_code": 201,
                        "status": "Success",
                        "message": "Product details added Successfully",
                        "product_name": product_details.__dict__['product_name'],
                        "product_price"  : product_details.__dict__['product_price'],
                        "product_stock"  : product_details.__dict__['product_stock'],
                         "user_id"        :users_role,
                    },
                    "error": None
                }
            }
                
   
            else:
                raise HTTPException(
                            status_code = 409,
                            detail = {
                                "status": "Error",
                                "status_code" : 409,
                                "data": None,
                                "error" : {
                                    "status_code" : 409,
                                    "status":"Error",
                                    "message" : "Error while adding product",
                                }
                            },
                        )
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "Error",
                    "status_code": 500,
                    "data": None,
                    "error": {
                        "status_code": 500,
                        "status": "Error",
                        "message": "Not a company staff",
                        "users_id":users_role
                    }
                }
        )
    else:
        raise HTTPException(
            status_code = 404,
            detail = {
                "status": "Error",
                "status_code" : 404,
                "data": None,
                "error" : {
                    "status_code" : 404,
                    "status":"Error",
                    "message" : "no user found",
                }
            },
        )    

# 6
@app.post('/product_purchase', dependencies=[Depends(JWTBearer())])
def buy_product(data: schema.product_purchase, token = Depends(JWTBearer()), db : Session=Depends(get_db)):
    email = auth_handler.decode_token(token=token)
    userdata = crud.get_user_by_email(db=db, email=email['sub'])
    users_id = userdata.__dict__['id']
    if userdata:
        user_product= crud.verify_product(db=db,product_name=data.product_name)
        if user_product:
            check_stock=crud.verify_stock(db=db,quantity=data.quantity)
            if not check_stock:
                raise HTTPException(
                    status_code = 404,
                    detail = {
                    "status": "Error",
                    "status_code" : 404,
                    "data": None,
                    "error" : {
                    "status_code" : 404,
                    "status":"Error",   
                    "message" : "out of stock, enter lesser quantity",
                }
            },
        )   
            product_price = user_product.__dict__['product_price']
            total_price = product_price * data.quantity
            get_user = db.query(models.wallet).filter(models.wallet.users_id==users_id).first()
            balance = get_user.__dict__['balance']
            balance= crud.check_balance(db=db,total_price=total_price, users_id=users_id)
            if not balance:
                raise HTTPException(
                    status_code = 404,
                    detail = {
                    "status": "Error",
                    "status_code" : 404,
                    "data": None,
                    "error" : {
                    "status_code" : 404,
                    "status":"Error",
                    "message" : "insufficient balance , please add money to the wallet",
                }
            },
        ) 
            else:
                add_token=crud.update_token(db=db,users_id=users_id,total_price=total_price)
                product_name  =user_product.__dict__['product_name']
                fullname      = userdata.__dict__['full_name']
                quantity      = data.quantity
                purchase_date          = date.today()
                purchase_details = crud.purchase_info(db=db,quantity=quantity, users_id=users_id, 
                                                full_name=fullname, product_name=product_name, 
                                                date= purchase_date, total_price= total_price)
                
                if purchase_details:
                    return {
                        "detail": {
                            "status ": "Success",
                                "status_code": 200,
                                 "data": {
                                    "status_code": 200,
                                    "status": "Success",
                                    "message": "purchased successfully",
                                    # "product_name":product_name,
                                    # "quantity":quantity,
                                    # "token":add_token.__dict__['token']
                                },
                                "error": None
                            }
                        }
        else:
            raise HTTPException(
                status_code = 404,
                detail = {
                "status": "Error",
                "status_code" : 404,
                "data": None,
                "error" : {
                    "status_code" : 404,
                    "status":"Error",
                    "message" : "product not found",
                }
            },
        )       
    else:
        raise HTTPException(
            status_code = 404,
            detail = {
                "status": "Error",
                "status_code" : 404,
                "data": None,
                "error" : {
                    "status_code" : 404,
                    "status":"Error",
                    "message" : "no user found",
                }
            },
        )
#7
@app.post("/purchase_membership", dependencies=[Depends(JWTBearer())])
async def membership(data:schema.membership, token = Depends(JWTBearer()), db : Session=Depends(get_db)):
    email = auth_handler.decode_token(token=token)
    userdata = crud.get_user_by_email(db=db, email=email['sub'])
    users_id = userdata.__dict__['id']     
    if userdata:
        find_plan = crud.find_plan(db=db,plan=data.plan)
        if find_plan:
            plan_rate =find_plan.__dict__['amount']
            user_balance= crud.get_by_user_id(db=db,users_id=users_id)
            balance = user_balance.__dict__['balance']
            if balance > plan_rate :
                verify_pin = crud.verify_pin_by_id(db=db,users_id=users_id)
                get_pin = verify_pin.__dict__['pin']
                if get_pin == data.pin :
                    add_membership = crud.add_membership(db=db,users_id=users_id,plan=data.plan)
                    if add_membership:
                        return {
                        "detail": {
                            "status ": "Success",
                                "status_code": 200,
                                "data": {
                                    "status_code": 200,
                                    "status": "Success",
                                    "message": "membership purchased successfully",
                                    #  "plan":find_plan.__dict__['plan'],
                                    
                                },
                                "error": None
                            }
                        }
                    else:
                        raise HTTPException(
                            status_code = 409,
                            detail = {
                                "status": "Error",
                                "status_code" : 409,
                                "data": None,
                                "error" : {
                                    "status_code" : 409,
                                    "status":"Error",
                                    "message" : "Error while purchasing membership",
                                }
                            },
                        )
                else:
                    raise HTTPException(
                    status_code = 401, 
                    detail={
                        "status": "Error",
                        "status_code": 401,
                        "data": None,
                        "error": {
                            "status_code": 401,
                            "status": "Error",
                            "message": " Invalid PIN, please re-enter"
                        }
                    }
                )
            else:
                raise HTTPException(
                    status_code = 404,
                    detail = {
                    "status": "Error",
                    "status_code" : 404,
                    "data": None,
                    "error" : {
                    "status_code" : 404,
                    "status":"Error",
                    "message" : "insufficient balance , please add money to the wallet",
                }
            },
        )     
        else:
            raise HTTPException(
                    status_code = 401, 
                    detail={
                        "status": "Error",
                        "status_code": 401,
                        "data": None,
                        "error": {
                            "status_code": 401,
                            "status": "Error",
                            "message": " Invalid plan, please enter a valid plan"
                        }
                    }
                )
    else:
        raise HTTPException(
            status_code = 404,
            detail = {
                "status": "Error",
                "status_code" : 404,
                "data": None,
                "error" : {
                    "status_code" : 404,
                    "status":"Error",
                    "message" : "no user found",
                }
            },
        )    
#8
@app.put('/product_update', dependencies=[Depends(JWTBearer())])
def product_update(data: schema.add_product, token = Depends(JWTBearer()), db : Session=Depends(get_db)):
    email = auth_handler.decode_token(token=token)
    userdata = crud.get_user_by_email(db=db, email=email['sub'])
    # users_id = userdata.__dict__['id']
    users_role= userdata.__dict__['user_role']
    if userdata:
        if users_role == 1:
            user_product= crud.verify_product(db=db,product_name=data.product_name)
            if user_product:
                update_product = crud.update_product_details(db=db,data=add_products)
                if update_product:
                    return {
                        "detail": {
                            "status ": "Success",
                                "status_code": 200,
                                "data": {
                                    "status_code": 200,
                                    "status": "Success",
                                    "message": "product details updated successfully",
                                    #  "plan":find_plan.__dict__['plan'],
                                    
                                },
                                "error": None
                            }
                        }
                else:
                    raise HTTPException(
                            status_code = 409,
                            detail = {
                                "status": "Error",
                                "status_code" : 409,
                                "data": None,
                                "error" : {
                                    "status_code" : 409,
                                    "status":"Error",
                                    "message" : "Error while purchasing membership",
                                }
                            },
                        )
           
            else:
                raise HTTPException(
                status_code = 404,
                detail = {
                "status": "Error",
                "status_code" : 404,
                "data": None,
                "error" : {
                    "status_code" : 404,
                    "status":"Error",
                    "message" : "product not found",
                }
            },
        )
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "Error",
                    "status_code": 500,
                    "data": None,
                    "error": {
                        "status_code": 500,
                        "status": "Error",
                        "message": "Not a company staff",
                        "users_id":users_role
                    }
                }
        )  
    else:
        raise HTTPException(
            status_code = 404,
            detail = {
                "status": "Error",
                "status_code" : 404,
                "data": None,
                "error" : {
                    "status_code" : 404,
                    "status":"Error",
                    "message" : "no user found",
                }
            },
        )             

#9
@app.delete('/product_delete', dependencies=[Depends(JWTBearer())])
def delete_product(product_name:str , token = Depends(JWTBearer()), db : Session=Depends(get_db)):
    email = auth_handler.decode_token(token=token)
    userdata = crud.get_user_by_email(db=db, email=email['sub'])
    # users_id = userdata.__dict__['id']
    users_role= userdata.__dict__['user_role']
    # print(users_role)
    if userdata:
        if users_role == 1:
            user_product= crud.verify_product(db=db,product_name=product_name)
            if user_product:
                product_to_delete= crud.delete_product(db=db, product_name=product_name)
                if product_to_delete:
                    return {
                        "detail": {
                            "status ": "Success",
                                "status_code": 200,
                                "data": {
                                    "status_code": 200,
                                    "status": "Success",
                                    "message": "product deleted successfully",
                                    #  "plan":find_plan.__dict__['plan'],
                                    
                                },
                                "error": None
                            }
            
                        }
                else:
                    raise HTTPException(
                            status_code = 409,
                            detail = {
                                "status": "Error",
                                "status_code" : 409,
                                "data": None,
                                "error" : {
                                    "status_code" : 409,
                                    "status":"Error",
                                    "message" : "Error while deleting product",
                                }
                            },
                        )
            else:
                raise HTTPException(
                    status_code = 401, 
                    detail={
                        "status": "Error",
                        "status_code": 401,
                        "data": None,
                        "error": {
                            "status_code": 401,
                            "status": "Error",
                            "message": " no product found"
                        }
                    }
                ) 
        else:
            raise HTTPException(
                status_code = 404,
                detail = {
                "status": "Error",
                "status_code" : 404,
                "data": None,
                "error" : {
                    "status_code" : 404,
                    "status":"Error",
                    "message" : "not a company staff",
                }
            },
        )   
    else:
            raise HTTPException(
                status_code = 404,
                detail = {
                "status": "Error",
                "status_code" : 404,
                "data": None,
                "error" : {
                    "status_code" : 404,
                    "status":"Error",
                    "message" : "user not found",
                }
            },
        )       
        

#10
@app.get("/product_list",  dependencies=[Depends(JWTBearer())])
def list_product(token = Depends(JWTBearer()), db : Session=Depends(get_db)):
    email = auth_handler.decode_token(token=token)
    userdata = crud.get_user_by_email(db=db, email=email['sub'])
    if userdata:
        fetch_products= db.query(models.product_details).all()
        return fetch_products
    else:
        raise HTTPException(
            status_code = 404,
            detail = {
                "status": "Error",
                "status_code" : 404,
                "data": None,
                "error" : {
                    "status_code" : 404,
                    "status":"Error",
                    "message" : "no user found",
                }
            },
        )
    
#11
@app.post("/transaction_log",  dependencies=[Depends(JWTBearer())])
def transaction_details(date: str,token = Depends(JWTBearer()), db : Session=Depends(get_db)):
    email = auth_handler.decode_token(token=token)
    userdata = crud.get_user_by_email(db=db, email=email['sub'])
    users_id = userdata.__dict__['id']
    if userdata:
        verify_pin = crud.verify_pin_by_id(db=db, users_id=users_id)
        if verify_pin:
            fetch_date = db.query(models.transaction_log).filter(models.transaction_log.date==date).all()
            if fetch_date:
                 return fetch_date
            else:
                raise HTTPException(
                status_code = 404,
                detail = {
                "status": "Error",
                "status_code" : 404,
                "data": None,
                "error" : {
                    "status_code" : 404,
                    "status":"Error",
                    "message" : "no transaction found on this date",
                }
            },
        ) 
        else:
                raise HTTPException(
                    status_code = 401, 
                    detail={
                        "status": "Error",
                        "status_code": 401,
                        "data": None,
                        "error": {
                            "status_code": 401,
                            "status": "Error",
                            "message": " Invalid pin, please enter a valid pin"
                        }
                    }
                ) 
    else:
            raise HTTPException(
                status_code = 404,
                detail = {
                "status": "Error",
                "status_code" : 404,
                "data": None,
                "error" : {
                    "status_code" : 404,
                    "status":"Error",
                    "message" : "user not found",
                }
            },
        )        


            


        

             

