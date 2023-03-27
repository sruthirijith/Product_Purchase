#import requests
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, Form, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from core.utils import password
from core.api.users import schema, crud
from core.database.connection import get_db, Base, engine
from core.jwt import auth_handler
from core.jwt.auth_bearer import JWTBearer
from core.api.users.crud import (
    create_user,
    get_user_by_email,
    get_user_by_phonenumber,
    validate_phone_number,
    get_user_roles,
    add_new_role,
    md5_encrypt,
    get_user_by_token,
    update_pin,
    update_change_password,
    update_token,
    update_reset_password
)
from core.api.consumer.crud import get_recent_referrals_profile
from core.utils.password import validate_password
from core.utils.twilio_service import twilio_send_otp, twilio_verify_otp

Base.metadata.create_all(bind=engine)
router = APIRouter()


@router.post("/register", status_code=201, tags=["User"])
async def create_user_api(user: schema.UserCreate, db: Session = Depends(get_db)):
    
    if user.role_id in [1,2]:  
        db_user: Any = get_user_by_email(db, email=user.email)
        if db_user:
            check_user_role = get_user_roles(db=db, users_id=db_user.__dict__['id'], role=user.role_id)
            if check_user_role:
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
            else:
                add_new_role = add_new_role(db=db, users_id=db_user.__dict__['id'], role=user.role_id)
                user_data = get_user_by_email(db, email=user.email)
                token = auth_handler.encode_token(user_data.email)
                refresh_token = auth_handler.refresh_token(user_data.email)
                if add_new_role:
                    return {
                        "detail": {
                            "status": "Success",
                            "status_code": 201,
                            "data": {
                                "status_code": 201,
                                "status": "Success",
                                "message": "User registered Successfully",
                                "access_token": token, "token_type": "bearer",
                                "refresh_token": refresh_token, "token_type": "bearer",
                                "id" : user_data.__dict__['id'],
                                "username": user_data.__dict__['full_name'],
                                "phonenumber": user_data.__dict__['phone_number'],
                                "role": add_new_role.__dict__['role_id']
                            },
                            "error": None
                        }
                    }

        reg_phone: Any = get_user_by_phonenumber(db, phone_number=user.phone_number)

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
            
        if reg_phone is None:
        
            if not validate_phone_number(user.phone_number, user.country_code):
                raise HTTPException(
                    status_code=400,
                    detail={
                        "status": "Error",
                        "status_code": 400,
                        "data": None,
                        "error": {
                            "status_code": 400,
                            "status": "Error",
                            "message": "Enter a valid phone number."
                        }
                    }
                )
            elif not validate_password(user.password):
                raise HTTPException(
                    status_code=400,
                    detail={
                        "status": "Error",
                        "status_code": 400,
                        "data": None,
                        "error": {
                            "status_code": 400,
                            "status": "Error",
                            "message": """Password must be at least 8 characters long, contains atleast one lower case character, one 
                            upper case character, one digit and one special case character."""
                        }
                    }
                )
            created_user, role = create_user(db, user)
            token = auth_handler.encode_token(created_user.email)
            refresh_token = auth_handler.refresh_token(created_user.email)
            response = {
                "detail": {
                    "status": "Success",
                    "status_code": 201,
                    "data": {
                        "status_code": 201,
                        "status": "Success",
                        "message": "User registered Successfully",
                        "access_token": token, "token_type": "bearer",
                        "refresh_token": refresh_token, "token_type": "bearer",
                        "id" : created_user.__dict__['id'],
                        "username": created_user.__dict__['full_name'],
                        "phonenumber": created_user.__dict__['phone_number']
                    },
                    "error": None
                }
            }
            return response, role
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
                        "message": "Some error occurred"
                    }
                }
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
                        "message": "Only Consumer or Merchant can register"
                    }
                }
        )



# @router.post("/user_email_login", tags=["User"])  #with form
# def user_email_login(role : int, db:Session=Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):

#     check_user = crud.get_user_by_email(db=db, email=form_data.username)
#     if not check_user or check_user.__dict__['deleted']==True:    
#             print("404")
#             raise HTTPException(
#                 status_code = 404, 
#                 detail={
#                     "status": "Error",
#                     "status_code": 404,
#                     "data": None,
#                     "error": {
#                         "status_code": 404,
#                         "status": "Error",
#                         "message": "Email not found!"
#                     }
#                 }
#             )
#     elif check_user.__dict__['blocked']==True:
#             raise HTTPException(
#                 status_code = 401, 
#                 detail={
#                     "status": "Error",
#                     "status_code": 401,
#                     "data": None,
#                     "error": {
#                         "status_code": 401,
#                         "status": "Error",
#                         "message": "User is blocked!"
#                     }
#                 }
#             )
#     else:
#         verify_user_role = crud.get_user_roles(db=db, users_id=check_user.__dict__['id'], role=role)
#         if not verify_user_role:
#             raise HTTPException(
#                 status_code = 404,
#                 detail={
#                     "status": "Error",
#                     "status_code": 404,
#                     "data": None,
#                     "error": {
#                         "status_code": 404,
#                         "status": "Error",
#                         "message": "Entered user role not found!"
#                     }
#                 }
#             )   
#         else:    
#             verify_password = crud.verify_email_password(db=db, email=form_data.username, password=form_data.password)

#             if not verify_password:
#                 raise HTTPException(
#                     status_code = 401, 
#                     detail={
#                         "status": "Error",
#                         "status_code": 401,
#                         "data": None,
#                         "error": {
#                             "status_code": 401,
#                             "status": "Error",
#                             "message": "Login failed! Invalid credentials"
#                         }
#                     }
#                 )
#             else:
#                 userinfo = crud.verify_email_password(db=db, email=form_data.username, password=form_data.password)
#                 if userinfo:
#                     token = auth_handler.encode_token(form_data.username)
#                     refresh_token = auth_handler.refresh_token(form_data.username)
#                     return {
#                         "detail": {
#                             "status": "Success",
#                             "status_code": 200,
#                             "data": {
#                                 "status_code": 200,
#                                 "status": "Success",
#                                 "message": "User Logged in Successfully",
#                                 "access_token": token, "token_type": "bearer",
#                                 "refresh_token": refresh_token, "token_type": "bearer",
#                                 "id":userinfo.__dict__['id'],
#                                 "full_name": userinfo.__dict__['full_name'],
#                                 "email": userinfo.__dict__['email'],
#                                 "phone_number": userinfo.__dict__['phone_number'],
#                             },
#                             "error": None
#                         }
#                     }


# @router.post("/user_email_login_without_form", tags=["User"])  #without form
# def user_email_login_without_form(role : int,userdata : schema.LoginSchemaEmailPass, db:Session=Depends(get_db)):

#     check_user = crud.get_user_by_email(db=db, email=userdata.email)
#     if not check_user or check_user.__dict__['deleted']==True:    
#             print("404")
#             raise HTTPException(
#                 status_code = 404, 
#                 detail={
#                     "status": "Error",
#                     "status_code": 404,
#                     "data": None,
#                     "error": {
#                         "status_code": 404,
#                         "status": "Error",
#                         "message": "Email not found!"
#                     }
#                 }
#             )
#     elif check_user.__dict__['blocked']==True:
#             raise HTTPException(
#                 status_code = 401, 
#                 detail={
#                     "status": "Error",
#                     "status_code": 401,
#                     "data": None,
#                     "error": {
#                         "status_code": 401,
#                         "status": "Error",
#                         "message": "User is blocked!"
#                     }
#                 }
#             )
#     else:
#         verify_user_role = crud.get_user_roles(db=db, users_id=check_user.__dict__['id'], role=role)
#         if not verify_user_role:
#             raise HTTPException(
#                 status_code = 404,
#                 detail={
#                     "status": "Error",
#                     "status_code": 404,
#                     "data": None,
#                     "error": {
#                         "status_code": 404,
#                         "status": "Error",
#                         "message": "Entered user role not found!"
#                     }
#                 }
#             )   
#         else:    
#             verify_password = crud.verify_email_password(db=db, email=userdata.email, password=userdata.password)

#             if not verify_password:
#                 raise HTTPException(
#                     status_code = 401, 
#                     detail={
#                         "status": "Error",
#                         "status_code": 401,
#                         "data": None,
#                         "error": {
#                             "status_code": 401,
#                             "status": "Error",
#                             "message": "Login failed! Invalid credentials"
#                         }
#                     }
#                 )
#             else:
#                 userinfo = crud.verify_email_password(db=db, email=userdata.email, password=userdata.password)
#                 if userinfo:
#                     token = auth_handler.encode_token(userdata.email)
#                     refresh_token = auth_handler.refresh_token(userdata.email)
#                     return {
#                         "detail": {
#                             "status": "Success",
#                             "status_code": 200,
#                             "data": {
#                                 "status_code": 200,
#                                 "status": "Success",
#                                 "message": "User Logged in Successfully",
#                                 "access_token": token, "token_type": "bearer",
#                                 "refresh_token": refresh_token, "token_type": "bearer",
#                                 "id":userinfo.__dict__['id'],
#                                 "full_name": userinfo.__dict__['full_name'],
#                                 "email": userinfo.__dict__['email'],
#                                 "phone_number": userinfo.__dict__['phone_number'],
#                             },
#                             "error": None
#                         }
#                     }


# @router.get("/user_email_login/user_info", dependencies=[Depends(JWTBearer())], tags=["Global"])
# async def read_users_me(token = Depends(JWTBearer()), db : Session=Depends(get_db)):
#     payload = auth_handler.decode_token(token)
#     userdata = crud.get_user_by_email(db=db, email=payload['sub'])
#     if userdata:
#         response_msg = {
#             "detail": {
#                 "status": "Success",
#                 "status_code": 200,
#                 "data": {
#                     "status_code": 200,
#                     "status": "Success",
#                     "message": "User Logged in Successfully",
#                     "id":userdata.__dict__['id'],
#                     "full_name": userdata.__dict__['full_name'],
#                     "email": userdata.__dict__['email'],
#                     "phone_number": userdata.__dict__['phone_number'],
#                 },
#                 "error": None
#             }
#         }

#         return response_msg
#     else:
#         raise HTTPException(
#             status_code=404,
#             detail={
#                 "status": "Error",
#                 "status_code": 404,
#                 "data": None,
#                 "error": {
#                     "status_code": 404,
#                     "status": "Error",
#                     "message": "No user found"
#                 }
#             }
#         )


# @router.post("/user_phone_login", tags=["User"])
# def user_phone_login(role : int ,user_data : schema.PhoneNumberLoginSchema, response : Response, db : Session=Depends(get_db)):
    
#     check_phone = crud.get_user_by_phonenumber(db=db, phone_number=user_data.phone_number)

#     if not check_phone or check_phone.__dict__['deleted']==True:   
#             print("404")
#             raise HTTPException(
#                 status_code = 404,
#                 detail={
#                     "status": "Error",
#                     "status_code": 404,
#                     "data": None,
#                     "error": {
#                         "status_code": 404,
#                         "status": "Error",
#                         "message": "phone_number not found!"
#                     }
#                 }
#             )
        
#     elif check_phone.__dict__['blocked']==True:
#         raise HTTPException(
#             status_code = 401,
#             detail={
#                 "status": "Error",
#                 "status_code": 401,
#                 "data": None,
#                 "error": {
#                     "status_code": 401,
#                     "status": "Error",
#                     "message": "User is blocked!"
#                 }
#             }
#         )

#     else:
#         verify_user_role = crud.get_user_roles(db=db, users_id=check_phone.__dict__['id'], role=role)
#         if not verify_user_role:
#             raise HTTPException(
#                 status_code = 404,
#                 detail={
#                     "status": "Error",
#                     "status_code": 404,
#                     "data": None,
#                     "error": {
#                         "status_code": 404,
#                         "status": "Error",
#                         "message": "Entered user role not found!"
#                     }
#                 }
#             )
#         else: 
#             send_otp = twilio_send_otp(user_data.phone_number)

#             if send_otp.status == "pending":
                
#                 response_msg = {
#                     "detail": {
#                         "status": "Success",
#                         "status_code": 200,
#                         "data": {
#                             "status_code": 200,
#                             "status": "Success",
#                             "message": "OTP send",
#                             "phonenumber": check_phone.__dict__['phone_number'],
#                         },
#                         "error": None
#                     }
#                 }
#                 return response_msg

#             else:
#                 raise HTTPException(
#                     status_code=409,
#                     detail={
#                         "status": "Error",
#                         "status_code": 409,
#                         "data": None,
#                         "error": {
#                             "status_code": 409,
#                             "status": send_otp.status,
#                             "message": f"Could not send otp to {user_data.phone_number}"
#                         }
#                     }
#                 )


# @router.post("/user_phone_login/verify_otp", tags=["User"])
# def verify_otp(data : schema.Otp, response : Response, db : Session=Depends(get_db)):

#     otp = data.otp
#     # key = data.key
#     phone_number = data.phone_number

#     verifying_send_otp = twilio_verify_otp(phone_number, otp)
    
#     userinfo = crud.get_user_by_phonenumber(db = db, phone_number=phone_number)
    
#     if verifying_send_otp.status == "approved" and phone_number==userinfo.phone_number:
#         token = auth_handler.encode_token(userinfo.__dict__['email'])
#         refresh_token = auth_handler.refresh_token(userinfo.__dict__['email'])
#         return {
#             "detail": {
#                 "status": "Success",
#                 "status_code": 200,
#                 "data": {
#                     "status_code": 200,
#                     "status": "Success",
#                     "message": "OTP Verified Successfully",
#                     "access_token": token, #"token_type": "bearer",
#                     "refresh_token": refresh_token,#, "token_type": "bearer"
#                     "id":userinfo.__dict__['id'],
#                     "full_name": userinfo.__dict__['full_name'],
#                     "email": userinfo.__dict__['email'],
#                     "phone_number": userinfo.__dict__['phone_number'],
#                 },
#             "error": None
#             }
#         }
#     else:
#         raise HTTPException(
#             status_code = 401,
#             detail={
#                 "status": "Error",
#                 "status_code": 401,
#                 "data": None,
#                 "error": {
#                     "status_code": 401,
#                     "status": "Error",
#                     "message": "OTP is not valid"
#                 }
#             }
#         )


# @router.get("/user_phone_login/verify_otp/token", dependencies=[Depends(JWTBearer())], tags=["Global"])
# def phone_login(token = Depends(JWTBearer()), db : Session=Depends(get_db)):
#     email = auth_handler.decode_token(token=token)
#     userdata = crud.get_user_by_email(db=db, email=email['sub'])

#     if userdata:
#         response_msg = {
#             "detail": {
#                 "status": "Success",
#                 "status_code": 200,
#                 "data": {
#                     "status_code": 200,
#                     "status": "Success",
#                     "message": "User login Successfully",
#                     "id":userdata.__dict__['id'],
#                     "full_name": userdata.__dict__['full_name'],
#                     "email": userdata.__dict__['email'],
#                     "phone_number": userdata.__dict__['phone_number'],
#                 },
#                 "error": None
#             }
#         }
#         return response_msg

#     else:
#         raise HTTPException(
#             status_code=404,
#             detail={
#                 "status": "Error",
#                 "status_code": 404,
#                 "data": None,
#                 "error": {
#                     "status_code": 404,
#                     "status": "Error",
#                     "message": "No user found"
#                 }
#             }
#         )


# @router.get('/refresh_token', dependencies=[Depends(JWTBearer())], tags=["User"])
# def refresh(refresh_token = Depends(JWTBearer()), db : Session=Depends(get_db)):
#     new_access_token = auth_handler.refresh_access_token(refresh_token=refresh_token)
#     email=auth_handler.decode_token(token=new_access_token['access_token'])
#     user_data= get_user_by_email(db=db, email=email['sub'])
#     if user_data:
#         return {
#             "detail": {
#             "status": "Success",
#             "status_code": 201,
#                 "data": {
#                 "status_code": 201,
#                 "status": "Success",
#                 "message": "refresh token",
#                 "token" : new_access_token
#                 },
#             "error": None
#         }
#             }
#     else:
#         raise HTTPException(
#             status_code=404,
#             detail={
#                 "status": "Error",
#                 "status_code": 404,
#                 "data": None,
#                 "error": {
#                     "status_code": 404,
#                     "status": "Error",
#                     "message": "No user found"
#                 }
#             }
#         )


# @router.post('/user_forgot_password', status_code=201, tags=["User"])
# async def forgot_password(email : schema.LoginSchema_email, db : Session = Depends(get_db)):
#     user = get_user_by_email(db, email.email)
#     if user :
#         encrpt_key = md5_encrypt()
#         token_update = update_token(db = db, email = email.email, token = encrpt_key)
#         if token_update:
#             response_msg = {
#                 "detail": {
#                     "status": "Success",
#                     "status_code": 200,
#                     "data": {
#                         "status_code": 200,
#                         "status": "Success",
#                         "message": "",
#                         "status":"Sucess",
#                         "email": email.email,
#                         "key":encrpt_key,

#                     },
#                     "error": None
#                 }
#             }
#             return response_msg
#         else :
#             raise HTTPException(
#                 status_code=400,
#                 detail={
#                     "status": "Error",
#                     "status_code": 400,
#                     "data": None,
#                     "error": {
#                         "status_code": 400,
#                         "status": "Error",
#                         "message": "Token not updated"
#                     }
#                 }
#             )
#     else :
#         raise HTTPException(
#             status_code=404,
#             detail={
#                 "status": "Error",
#                 "status_code": 404,
#                 "data": None,
#                 "error": {
#                     "status_code": 404,
#                     "status": "Error",
#                     "message": "Email not registered"
#                 }
#             }
#         )


# @router.post("/user_reset_password", tags=["User"])
# async def reset_password(user : schema.reset_password, db:Session = Depends(get_db)):
#     user_data = get_user_by_token(db,user.token)
#     if user_data :
#         if user_data.token_expired == False :
#             if not password.validate_password(user.password):
#                 raise HTTPException(
#                     status_code=400,
#                     detail={
#                         "status": "Error",
#                         "status_code": 400,
#                         "data": None,
#                         "error": {
#                             "status_code": 400,
#                             "status": "Error",
#                             "message": """Password must be at least 8 characters long, contains atleast one lower case character, one 
#                             upper case character, one digit and one special case character."""
#                         }
#                     }
#                 )
#             user_password = password.get_hashed_password(user.password)
#             password_reset = update_reset_password(db = db, token = user.token, password = user_password)
#             if password_reset :
#                 return {
#                     "detail": {
#                     "status": "Success",
#                     "status_code": 201,
#                     "data": {
#                         "status_code": 201,
#                         "status": "Success",
#                         "message": "Password reset successfully"
#                         },
#                     "error": None
#                     }
#                 }
#             else :
#                 raise HTTPException(
#                     status_code=400,
#                     detail = {
#                         "status": "Error",
#                         "status_code": 400,
#                         "data": None,
#                         "error": {
#                             "status_code": 400,
#                             "status": "Error",
#                             "message": "Password not updated"
#                         }
#                     }
#                 )
#         else :
#             raise HTTPException(
#                 status_code=400,
#                 detail = {
#                     "status": "Error",
#                     "status_code": 400,
#                     "data": None,
#                     "error": {
#                         "status_code": 400,
#                         "status": "Error",
#                         "message": "Token expired"
#                     }
#                 }
#             )
#     else :
#         raise HTTPException(
#             status_code = 404,
#             detail = {
#                 "status": "Error",
#                 "status_code": 404,
#                 "data": None,
#                 "error": {
#                     "status_code": 404,
#                     "status": "Error",
#                     "message": "Invalid user"
#                 }
#             }
#         )


# @router.post("/user_change_pin", tags=["User"])
# async def change_pin(pin : schema.Change_pin, token = Depends(JWTBearer()), db : Session = Depends(get_db)):
#     token = auth_handler.decode_token(token=token)
#     user = crud.get_user_by_email_with_pin(db, token['sub'])
#     if not user :
#         raise HTTPException (
#             status_code = 404,
#             detail = {
#                 "status": "Error",
#                 "status_code": 404,
#                 "data": None,
#                 "error": {
#                     "status_code": 404,
#                     "status": "Error",
#                     "message": "Invalid user"
#                 }
#             }
#         )
#     if user.pin is not None :
#         if len(pin.new_pin)== 4 and pin.new_pin.isnumeric(): 
#             if user.pin ==  pin.old_pin:
#                 if pin.new_pin == pin.reenter_pin :
#                     pin_change = update_pin(db = db, email = token['sub'], pin = pin.new_pin)
#                     if pin_change :
#                         response_msg = {
#                             "detail": {
#                             "status": "Success",
#                             "status_code": 201,
#                             "data": {
#                                 "status_code": 201,
#                                 "status": "Success",
#                                 "message": "Pin changed"
#                             },
#                             "error": None
#                         }
#                         }
#                         return response_msg
#                     else :
#                         raise HTTPException (
#                             status_code = 400,
#                             detail = {
#                             "status": "Error",
#                             "status_code": 400,
#                             "data": None,
#                             "error": {
#                                 "status_code": 400,
#                                 "status": "Error",
#                                 "message": "Pin not changed"
#                                 }
#                             }
#                         )
#                 else :
#                     raise HTTPException (
#                         status_code = 409,
#                         detail = {
#                             "status": "Error",
#                             "status_code": 409,
#                             "data": None,
#                             "error": {
#                                 "status_code": 409,
#                                 "status": "Error",
#                                 "message": "New pin and Reenter pin must be same"
#                             }
#                         }
#                     )
#             else :
#                 raise HTTPException (
#                     status_code = 400,
#                     detail = {   
#                     "status": "Error",
#                     "status_code": 400,
#                     "data": None,
#                     "error": {
#                         "status_code": 400,
#                         "status": "Error",
#                         "message": "Wrong pin"
#                         }
#                     }
  
#                 )
#         else :
#             raise HTTPException (
#                 status_code = 400,
#                 detail = {
#                 "status": "Error",
#                 "status_code": 400,
#                 "data": None,
#                 "error": {
#                     "status_code": 400,
#                     "status": "Error",
#                     "message": "Pin number must be 4 character and numeric"
#                     }
#             }
#         )
#     else :
#         raise HTTPException (
#             status_code = 404,
#             detail = {
#             "status": "Error",
#             "status_code": 404,
#             "data": None,
#             "error": {
#                 "status_code": 404,
#                 "status": "Error",
#                 "message": "Pin not added"
#                 }
#             }
#         )
    

# @router.post("/user_change_password", tags=["User"])
# async def change_password(user_password : schema.Change_password,token = Depends(JWTBearer()), db : Session = Depends(get_db)):
#     token = auth_handler.decode_token(token=token)
#     user = crud.get_user_by_email_with_password(db, token['sub'])
#     if user :
#         if password.verify_password(user_password.old_password, user.password):
#             if user_password.new_password == user_password.reenter_password :
#                 if not password.validate_password(user_password.new_password):
#                     raise HTTPException(
#                         status_code=400,
#                         detail={
#                         "status": "Error",
#                         "status_code": 400,
#                         "data": None,
#                         "error": {
#                             "status_code": 400,
#                             "status": "Error",
#                             "message": """Password must be at least 8 characters long, contains atleast one lower case character, one 
#                                                         upper case character, one digit and one special case character."""
#                         }
#                     }
#                     )
#                 new_password = password.get_hashed_password(user_password.new_password)
#                 password_change = update_change_password(db = db, email = token['sub'], password = new_password)
#                 if password_change :
#                     response_msg = {  
#                     "detail": {
#                     "status": "Success",
#                     "status_code": 201,
#                     "data": {
#                         "status_code": 201,
#                         "status": "Success",
#                         "message": "Password changed"
#                         },
#                     "error": None
#                 }
#                     }
#                     return response_msg
#                 else :
#                     raise HTTPException (
#                         status_code = 400,
#                         detail = {
#                         "status": "Error",
#                         "status_code": 400,
#                         "data": None,
#                         "error": {
#                             "status_code": 400,
#                             "status": "Error",
#                             "message": "Password not changed"
#                             }
#                         }
#                     )
#             else :
#                 raise HTTPException (
#                     status_code = 409,
#                     detail = {    
#                         "status": "Error",
#                         "status_code": 409,
#                         "data": None,
#                         "error": {
#                             "status_code": 409,
#                             "status": "Error",
#                             "message": "New password and Reenter password must be same"
#                             }
#                     }
#                 )
#         else :
#             raise HTTPException (
#                 status_code = 400,
#                 detail = {
#                 "status": "Error",
#                 "status_code": 400,
#                 "data": None,
#                 "error": {
#                     "status_code": 400,
#                     "status": "Error",
#                     "message": "Wrong password"
#                     }
#                 }
#             )
#     else :
#         raise HTTPException (
#             status_code = 404,
#                     detail = {
#                     "status": "Error",
#                     "status_code": 404,
#                     "data": None,
#                     "error": {
#                         "status_code": 404,
#                         "status": "Error",
#                         "message": "Invalid User"
#                     }
#                 }
#         )


# @router.post("/user_logout", tags=["User"])
# async def logout(token = Depends(JWTBearer()), db : Session = Depends(get_db)):
#     token = auth_handler.decode_token(token=token)
#     user = get_user_by_email(db, token['sub'])
#     if user :
#         response_msg = {
#             "detail": {
#                 "status": "Success",
#                 "status_code": 200,
#                 "data": {
#                     "status_code": 200,
#                     "status": "Success",
#                     "message": "Successfully logged out",
#                 },
#                 "error": None
#             }
#         }
#         return response_msg
#     else :
#         raise HTTPException(
#             status_code = 404,
#             detail = {
#                 "status": "Error",
#                 "status_code" : 404,
#                 "data": None,
#                 "error" : {
#                     "status_code" : 404,
#                     "status":"Error",
#                     "message" : "Invalid User",
#                 }
#             },
#         )
        

# @router.post("/generate-otp")
# async def generate_otp_api(user: schema.GenerateOtp, db: Session = Depends(get_db)):
    
#     user_data = get_user_by_phonenumber(db=db, phone_number=user.phone_number)
#     if user_data:
#         return HTTPException(
#             status_code = 400,
#             detail = {
#                 "status": "Error",
#                 "status_code" : 400,
#                 "data": None,
#                 "error" : {
#                     "status_code" : 400,
#                     "status":"Error",
#                     "message" : "Phone number already registered.",
#                 }
#             },
#         )
        
#     otp_sent_response = twilio_send_otp(phone_number=user.phone_number, channel=user.channel)
    
#     if otp_sent_response.status == "pending":
#         response = {
#             "detail": {
#                 "status": "Success",
#                 "status_code": 200,
#                 "data": {
#                     "status_code": 200,
#                     "status": "Success",
#                     "message": "OTP send to the number " + str(user.phone_number),
#                 },
#                 "error": None
#             }
#         }
#         return response
#     else:
#         raise HTTPException(
#             status_code = 502,
#             detail = {
#                 "status": "Error",
#                 "status_code" : 502,
#                 "data": None,
#                 "error" : {
#                     "status_code" : 502,
#                     "status":"Error",
#                     "message" : "OTP generation failed.",
#                 }
#             },
#         )


# @router.post("/verify-otp")
# async def verify_otp_api(user: schema.VerifyOtp, db: Session = Depends(get_db)):
    
#     try:
#         otp_verify_response = twilio_verify_otp(phone_number=user.phone_number, code=user.otp)
#     except Exception as e:
#         raise HTTPException(
#             status_code = 408,
#             detail = {
#                 "status": "Error",
#                 "status_code" : 408,
#                 "data": None,
#                 "error" : {
#                     "status_code" : 408,
#                     "status":"Error",
#                     "message" : "OTP verification timed out.",
#                 }
#             },
#         )
    
#     if otp_verify_response.status == "approved":
#         current_user = get_user_by_phonenumber(db, phone_number=user.phone_number)
#         if current_user and current_user.blocked == False and current_user.deleted == False:
#             response = {
#                 "detail": {
#                     "status": "Success",
#                     "status_code": 200,
#                     "data": {
#                         "status_code": 200,
#                         "status": "Success",
#                         "message": "OTP verified successfully",
#                         "user": current_user
#                     },
#                     "error": None
#                 }
#             }
#             return response
#         else:
#             response = {
#                 "detail": {
#                     "status": "Success",
#                     "status_code": 200,
#                     "data": {
#                         "status_code": 200,
#                         "status": "Success",
#                         "message": "OTP verified successfully",
#                         "user": current_user
#                     },
#                     "error": None
#                 }
#             }
#             return response
#     else:
#         raise HTTPException(
#             status_code = 404,
#             detail = {
#                 "status": "Error",
#                 "status_code" : 404,
#                 "data": None,
#                 "error" : {
#                     "status_code" : 404,
#                     "status":"Error",
#                     "message" : "Wrong OTP Code.",
#                 }
#             },
#         )


# @router.get("/refer-user", dependencies=[Depends(JWTBearer())], tags=["Global"])
# async def refer_friend_api(token = Depends(JWTBearer()), db : Session=Depends(get_db)):
#     payload = auth_handler.decode_token(token)
#     current_user = get_user_by_email(db=db, email=payload['sub'])
#     response_msg = {
#         "detail": {
#             "status": "Success",
#             "status_code": 200,
#             "data": {
#                 "status_code": 200,
#                 "status": "Success",
#                 "message": "fetched referral code Successfully",
#                 "referral_code": current_user.referral_code,
#             },
#             "error": None
#         }
#     }
#     return response_msg


# @router.get("/recent-referrals", dependencies=[Depends(JWTBearer())], tags=["Global"])
# async def recent_referrals_api(token = Depends(JWTBearer()), db: Session=Depends(get_db)):
#     payload = auth_handler.decode_token(token)
#     current_user = get_user_by_email(db=db, email=payload['sub'])
#     referred_users = get_recent_referrals_profile(db=db, referral_code=current_user.referral_code, user_id=current_user.id)
#     response = {
#         "detail": {
#             "status": "Success",
#             "status_code": 200,
#             "data": {
#                 "status_code": 200,
#                 "status": "Success",
#                 "message": "fetched referred users Successfully",
#                 "referred_users": referred_users,
#             },
#             "error": None
#         }
#     }
#     return response


# @router.post('/add_pin', dependencies=[Depends(JWTBearer())], tags=["User"])
# def add_pin(pin : schema.Add_Pin, token = Depends(JWTBearer()), db : Session=Depends(get_db)):
#     email = auth_handler.decode_token(token=token)
#     userdata = crud.get_user_by_email_with_pin(db=db, email=email['sub'])

#     if userdata:
#         print(userdata.__dict__)
#         if ((len(pin.pin) and len(pin.reenter_pin))==4) and pin.pin.isnumeric():
#             if userdata.__dict__['pin'] is None:         
#                 if pin.pin == pin.reenter_pin:
#                     add_pin = update_pin(db = db, email = userdata.__dict__['email'], pin = pin.pin)
#                     if add_pin:
#                         response_msg = {
#                             "detail": {
#                                 "status": "Success",
#                                 "status_code": 200,
#                                 "data": {
#                                     "status_code": 200,
#                                     "status": "Success",
#                                     "message": "Pin added Successfully",
#                                 },
#                                 "error": None
#                             }
#                         }
#                         return response_msg
#                     else:
#                         raise HTTPException(
#                             status_code = 409,
#                             detail = {
#                                 "status": "Error",
#                                 "status_code" : 409,
#                                 "data": None,
#                                 "error" : {
#                                     "status_code" : 409,
#                                     "status":"Error",
#                                     "message" : "Error while adding pin",
#                                 }
#                             },
#                         )
#                 else:
#                     raise HTTPException(
#                         status_code = 409,
#                         detail = {
#                             "status": "Error",
#                             "status_code" : 409,
#                             "data": None,
#                             "error" : {
#                                 "status_code" : 409,
#                                 "status":"Error",
#                                 "message" : "Two pin must be same",
#                             }
#                         },
#                     )
#             else:
#                 raise HTTPException(
#                     status_code = 409,
#                         detail = {
#                             "status": "Error",
#                             "status_code" : 409,
#                             "data": None,
#                             "error" : {
#                                 "status_code" : 409,
#                                 "status":"Error",
#                                 "message" : "Already pin exists",
#                             }
#                         },
#                 )
#         else:
#             raise HTTPException(
#                 status_code = 411,
#                 detail = {
#                     "status": "Error",
#                     "status_code" : 411,
#                     "data": None,
#                     "error" : {
#                         "status_code" : 411,
#                         "status":"Error",
#                         "message" : "Length of pin must be equal to 4 and numeric",
#                     }
#                 },
#             )
#     else:
#         raise HTTPException(
#             status_code = 404,
#             detail = {
#                 "status": "Error",
#                 "status_code" : 404,
#                 "data": None,
#                 "error" : {
#                     "status_code" : 404,
#                     "status":"Error",
#                     "message" : "No user found",
#                 }
#             },
#         )


# @router.post("/file_upload/", dependencies=[Depends(JWTBearer())], tags=["User"])
# async def file_upload(file_upload : UploadFile, file_collection : str = Form(), source_id : int = Form() \
#                         , token = Depends(JWTBearer()), db : Session=Depends(get_db), mongo_db = Depends(get_mongo_db)):
#     payload = auth_handler.decode_token(token)
#     current_user = get_user_by_email(db=db, email=payload['sub'])
#     if not current_user:
#         raise HTTPException (
#             status_code = 404,
#             detail = {
#                 "status": "Error",
#                 "status_code" : 404,
#                 "data": None,
#                 "error" : {
#                     "status_code" : 404,
#                     "status":"Error",
#                     "message" : "Invalid User",
#                 }
#             },
#         )
    
#     file_name = file_collection + "_" + str(source_id)
#     file_content = await file_upload.read()
#     content_type = file_upload.content_type
#     result = crud.save_file(mongo_db, file_collection, file_name, file_content, content_type)
#     if not result:
#         raise HTTPException (
#             status_code = 500,
#             detail = {
#                 "status": "Error",
#                 "status_code" : 500,
#                 "data": None,
#                 "error" : {
#                     "status_code" : 500,
#                     "status":"Error",
#                     "message" : "File upload failed",
#                 }
#             },
#         )
        
#     return {
#         "detail": {
#             "status": "Success",
#             "status_code": 200,
#             "data": {
#                 "status_code": 200,
#                 "status": "Success",
#                 "message": "File uploaded Successfully",
#                 "file_id": str(result)
#             },
#             "error": None
#         }
#     }


# @router.get("/file_download/{file_collection}/{file_id}", dependencies=[Depends(JWTBearer())], tags=["User"])
# async def file_download(file_collection : str , file_id : str, token = Depends(JWTBearer()), db : Session=Depends(get_db), mongo_db = Depends(get_mongo_db)):
#     payload = auth_handler.decode_token(token)
#     current_user = get_user_by_email(db=db, email=payload['sub'])
#     if not current_user:
#         raise HTTPException (
#             status_code = 404,
#             detail = {
#                 "status": "Error",
#                 "status_code" : 404,
#                 "data": None,
#                 "error" : {
#                     "status_code" : 404,
#                     "status":"Error",
#                     "message" : "Invalid User",
#                 }
#             },
#         )

#     exists = crud.check_if_file_exists(mongo_db, file_collection, file_id)
#     if not exists:
#         raise HTTPException (
#             status_code = 404,
#             detail = {
#                 "status": "Error",
#                 "status_code" : 404,
#                 "data": None,
#                 "error" : {
#                     "status_code" : 404,
#                     "status":"Error",
#                     "message" : "File doesn't exist",
#                 }
#             },
#         )
        
#     result = crud.retrieve_file(mongo_db, file_collection, file_id)
#     if not result:
#         raise HTTPException (
#             status_code = 500,
#             detail = {
#                 "status": "Error",
#                 "status_code" : 500,
#                 "data": None,
#                 "error" : {
#                     "status_code" : 500,
#                     "status":"Error",
#                     "message" : "File download failed",
#                 }
#             },
#         )
        
#     # return {
#     #     "detail": {
#     #         "status": "Success",
#     #         "status_code": 200,
#     #         "data": {
#     #             "status_code": 200,
#     #             "status": "Success",
#     #             "message": "File downloaded Successfully",
#     #             "content": result
#     #         },
#     #         "error": None
#     #     }
#     # }
#     return Response(status_code=200, content=result)


# @router.delete("/file_delete/{file_collection}/{file_id}", dependencies=[Depends(JWTBearer())], tags=["User"])
# async def file_delete(file_collection : str, file_id : str, token = Depends(JWTBearer()), db : Session=Depends(get_db), mongo_db = Depends(get_mongo_db)):
#     payload = auth_handler.decode_token(token)
#     current_user = get_user_by_email(db=db, email=payload['sub'])
#     if not current_user:
#         raise HTTPException (
#             status_code = 404,
#             detail = {
#                 "status": "Error",
#                 "status_code" : 404,
#                 "data": None,
#                 "error" : {
#                     "status_code" : 404,
#                     "status":"Error",
#                     "message" : "Invalid User",
#                 }
#             },
#         )
    
#     exists = crud.check_if_file_exists(mongo_db, file_collection, file_id)
#     if not exists:
#         raise HTTPException (
#             status_code = 404,
#             detail = {
#                 "status": "Error",
#                 "status_code" : 404,
#                 "data": None,
#                 "error" : {
#                     "status_code" : 404,
#                     "status":"Error",
#                     "message" : "File doesn't exist",
#                 }
#             },
#         )
#     result = crud.delete_file(mongo_db, file_collection, file_id)
#     if not result:
#         raise HTTPException (
#             status_code = 500,
#             detail = {
#                 "status": "Error",
#                 "status_code" : 500,
#                 "data": None,
#                 "error" : {
#                     "status_code" : 500,
#                     "status":"Error",
#                     "message" : "File deletion failed",
#                 }
#             },
#         )
#     return {
#         "detail": {
#             "status": "Success",
#             "status_code": 200,
#             "data": {
#                 "status_code": 200,
#                 "status": "Success",
#                 "message": "File deleted Successfully",
#             },
#             "error": None
#         }
#     }

