import json
from fastapi.testclient import TestClient

from main import app
from tests.crud import truncation, update_blocked, update_deleted


client = TestClient(app)

#######################REGISTER##############################
#1
def test_register_user_consumer():
    truncate = truncation(table='users')
    if truncate == True:
        response = client.post(
            "/register",
            json={
                "full_name": "Test Consumer",
                "email": "test@example.com",
                "password": "Abcdefgh@123",
                "phone_number": "+911234567891",
                "country_code": "",
                "referred_by": "",
                "role_id": 5
                }
        )
        assert response.status_code == 201
        token = response.json()["access_token"]
        refresh_token = response.json()["refresh_token"]
        assert response.json() == {
                "access_token" : token,
                "token_type" : "bearer",
                "refresh_token" : refresh_token,
                "status_code": 201,
                "status": "Success",
                "message": "User registred Successfully",
                "username": "Test Consumer",
                "phonenumber": "+911234567891",
                "role":5,
                "id" :1
        }
        return True

#2
def test_register_duplicate_email_user_consumer():
    register = test_register_user_consumer()
    if register == True:

        response = client.post(
            "/register",
            json={
                "full_name": "Test Consumer",
                "email": "test@example.com",
                "password": "Abcdefgh@123",
                "phone_number": "+911234567891",
                "country_code": "",
                "referred_by": "",
                "role_id": 5

                }
        )
        assert response.status_code == 200
        assert response.json() == {
                "detail": {
                    "status_code" : 200,
                    "status": "Error",
                    "message": "Email already registered"
                }
                }

#3         
def test_register_duplicate_phone_user_consumer():
    register = test_register_user_consumer()
    if register == True:
        response = client.post(
            "/register",
            json={
                "full_name": "Test1 Consumer",
                "email": "test1@example.com",
                "password": "Abcdefgh@123",
                "phone_number": "+911234567891",
                "country_code": "",
                "referred_by": "",
                "role_id": 5
                }
        )
        assert response.status_code == 200
        assert response.json() == {
                "detail": {
                    "status_code" : 200,
                    "status": "Error",
                    "message": "Phone number already registered"
                }
                }
#4
def test_register_invalid_phone_user_consumer():
    truncate = truncation(table='users')
    if truncate == True:
        response = client.post(
            "/register/",
            json={
                "full_name": "Test1 Consumer",
                "email": "test1@example.com",
                "password": "Abcdefgh@123",
                "phone_number": "+910234567890",
                "country_code": "",
                "referred_by": "",
                "role_id": 5
                }
        )
        assert response.status_code == 400
        assert response.json() == {
                "detail": {
                    "status_code" : 400,
                    "status": "Error",
                    "message": "Enter a valid phone number."
                }
                }
#5
def test_register_user_consumer_with_role_fails():
    truncate =  truncation(table='users')
    if truncate == True:
        response = client.post(
            "/register",
            json={
                "full_name": "Test Consumer",
                "email": "test@example.com",
                "password": "Abcdefgh@123",
                "phone_number": "+911234567891",
                "country_code": "",
                "referred_by": "",
                "role_id": 1
                }
        )
        assert response.status_code == 500
        assert response.json() == {
              "detail":{
                  "status_code": 500,
                  "status": "Error",
                  "message": "Only Consumer or Merchant can register"
        }
        }
#6
def test_register_user_consumer_password_validation_fails():
    truncate =  truncation(table='users')
    if truncate == True:
        response = client.post(
            "/register",
            json={
                "full_name": "Test Consumer",
                "email": "test@example.com",
                "password": "abcdefgh",
                "phone_number": "+911234567891",
                "country_code": "",
                "referred_by": "",
                "role_id": 5
                }
        )
        assert response.status_code == 400
        assert response.json() == {
              "detail":{
                  "status_code": 400,
                  "status": "Error",
                  "message": """Password must be at least 8 characters long, contains atleast one lower case character, one 
                            upper case character, one digit and one special case character."""
        }
        }

########################LOGIN###############################
#1
def test_login_consumer_token_success():
    register =test_register_user_consumer()
    if register:
        the_data = {"username": "test@example.com", "password" : "Abcdefgh@123"}

        response = client.post(
            "/user_email_login",
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            params={"role":5},
            data=the_data
        )
        assert response.status_code == 200
        assert response.json() != { 
                "detail" : {
                "status_code":401,
                "status":"Error", 
                "message" : "Email not found!"
                }
                }

#2
def test_login_consumer__token_fail():
    register =test_register_user_consumer()
    if register:
        the_data = {"username": "test12@example.com", "password" : "Abcdefgh@123"}

        response = client.post(
            "/user_email_login",
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            params={"role":5},
            data=the_data
        )
        assert response.status_code == 404
        assert response.json() == { 
                "detail" : {
                "status_code":404,
                "status":'Error', 
                "message" : "Email not found!"
                }
                }

#3
def test_login_consumer_token_wrong_cred():
    register =test_register_user_consumer()
    if register:
        the_data = {"username": "test@example.com", "password" : "abcd"}

        response = client.post(
            "/user_email_login",
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            params={"role":5},
            data=the_data
        )
        assert response.status_code == 401
        assert response.json() == { 
                "detail" : {
                "status_code":401,
                "status":'Error', 
                "message" : "Login failed! Invalid credentials"
                }
                }
            
#4
def test_login_consumer_success():
    register =test_register_user_consumer()
    if register:
        the_data = {"username": "test@example.com", "password" : "Abcdefgh@123"}

        response = client.post(
            "/user_email_login",
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            params={"role":5},
            data=the_data
        )
        token = response.json()["access_token"]
        headers={"Authorization" : f"Bearer {token}"}
        response = client.get(
            "/user_email_login/user_info",
            headers=headers
        )
        assert response.status_code == 200
        assert response.json() == { 
                "status_code": 200,
                "status": "Success",
                "message": "User login Successfully",
                "id" : 1,
                "full_name" : "Test Consumer",
                "email": "test@example.com",
                "phone_number" : "+911234567891"
                }
#5
def test_login_blocked_consumer_fails():
    register =test_register_user_consumer()
    update = update_blocked(table='users', id=1)
    if register and update:
        the_data = {"username": "test@example.com", "password" : "Abcdefgh@123"}

        response = client.post(
            "/user_email_login",
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            params={"role":5},
            data=the_data
        )
        assert response.status_code == 401
        assert response.json() == { 
                "detail" : {
                "status_code":401,
                "status":'Error', 
                "message" : "User is blocked!"
                }
                }
#6
def test_login_deleted_consumer_fails():
    register =test_register_user_consumer()
    update = update_deleted(table='users', id=1)
    if register and update:
        the_data = {"username": "test@example.com", "password" : "Abcdefgh@123"}

        response = client.post(
            "/user_email_login",
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            params={"role":5},
            data=the_data
        )
        assert response.status_code == 404
        assert response.json() == { 
                "detail" : {
                "status_code":404,
                "status":'Error', 
                "message" : "Email not found!"
                }
                }
#7
def test_login_consumer_role_fails():
    register =test_register_user_consumer()
    if register:
        the_data = {"username": "test@example.com", "password" : "Abcdefgh@123"}

        response = client.post(
            "/user_email_login",
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            params={"role":1},
            data=the_data
        )
        assert response.status_code == 404
        assert response.json() == { 
                "detail" : {
                "status_code":404,
                "status":'Error', 
                "message" : "Entered user role not found!"
                }
                }
#8
def test_login_consumer_fails():
    register =test_register_user_consumer()
    if register:
        the_data = {"username": "test@example.com", "password" : "Abcdefgh@123"}

        response = client.post(
            "/user_email_login",
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            params={"role":5},
            data=the_data
        )
        token = response.json()["access_token"]
        truncate = truncation(table='users')
        if truncate:
            headers={"Authorization" : f"Bearer {token}"}
            response = client.get(
                "/user_email_login/user_info",
                headers=headers
            )
            assert response.status_code == 404
            assert response.json() == {
                "detail": {
                    "status_code" : 404,
                    "status" : "Error",
                    "message" : "No user found"
                    }
                    }
#9
# def test_login_consumer_phone_send_otp_success():
#     register =test_register_user_consumer()
#     if register:
#         the_data = {"phone_number" : "+911234567891"}

#         response = client.post(
#             "/user_phone_login",
#             headers={'Content-Type': 'application/x-www-form-urlencoded'},
#             params={"role":5},
#             data=the_data
#         )
#         assert response.status_code == 200
#         assert response.json() == {
#                 "status_code":200,
#                 "status":"Success", 
#                 "message" : "OTP send",
#                 "phonenumber" : "+911234567891"
#                 }

#10
def test_login_consumer_phone_not_found():
    register =test_register_user_consumer()
    if register ==True:
        the_data = {"phone_number" : "+911234567892"}

        response = client.post(
            "/user_phone_login",
            headers={'Content-Type': 'application/json','Accept': 'application/json'},
            params={"role" : 5},
            data=json.dumps(the_data)
        )
        assert response.status_code == 404
        assert response.json() == { 
                "detail" : {
                "status_code": 404,
                "status":'Error', 
                "message" : "phone_number not found!"
                }
                }
#11
def test_login_consumer_phone_deleted():
    register =test_register_user_consumer()
    update = update_deleted(table='users',id=1)
    if register and update ==True:
        the_data = {"phone_number" : "+911234567891"}

        response = client.post(
            "/user_phone_login",
            headers={'Content-Type': 'application/json','Accept': 'application/json'},
            params={"role" : 5},
            data=json.dumps(the_data)
        )
        assert response.status_code == 404
        assert response.json() == { 
                "detail" : {
                "status_code": 404,
                "status":'Error', 
                "message" : "phone_number not found!"
                }
                }
#12
def test_login_consumer_phone_blocked():
    register =test_register_user_consumer()
    update = update_blocked(table='users',id=1)
    if register and update ==True:
        the_data = {"phone_number" : "+911234567891"}

        response = client.post(
            "/user_phone_login",
            headers={'Content-Type': 'application/json','Accept': 'application/json'},
            params={"role" : 5},
            data=json.dumps(the_data)
        )
        assert response.status_code == 401
        assert response.json() == { 
                "detail" : {
                "status_code": 401,
                "status":'Error', 
                "message" : "User is blocked!"
                }
                }
#13
def test_login_consumer_phone_role_fails():
    register =test_register_user_consumer()
    if register == True:
        the_data = {"phone_number" : "+911234567891"}

        response = client.post(
            "/user_phone_login",
            headers={'Content-Type': 'application/json','Accept': 'application/json'},
            params={"role" : 1},
            data=json.dumps(the_data)
        )
        assert response.status_code == 404
        assert response.json() == { 
                "detail" : {
                "status_code": 404,
                "status":'Error', 
                "message" : "Entered user role not found!"
                }
                }
#14
# def test_login_consumer_phone_send_otp_fails():
#     register =test_register_user_consumer()
#     if register == True:
#         the_data = {"phone_number" : "+911234567891"}

#         response = client.post(
#             "/user_phone_login",
#             headers={'Content-Type': 'application/json','Accept': 'application/json'},
#             params={"role" : 5},
#             data=json.dumps(the_data)
#         )
#         assert response.status_code == 409
#         Status = response.json()["Status"]
#         assert response.json() == { 
#                 "detail" : {
#                 "status": Status,
#                 "message" : "Could not send otp to +911234567891"
#                 }
#                 }

#15
# def test_user_consumer_verify_otp_success():
#     register =test_register_user_consumer()
#     if register == True:
#         the_data = {"otp" : "", "phone_number" : "+911234567891","key" : ""}

#         response = client.post(
#             "/user_phone_login/verify_otp",
#             headers={'Content-Type': 'application/json','Accept': 'application/json'},
#             params={"role" : 5},
#             data=json.dumps(the_data)
#         )
#         assert response.status_code == 200
#         access_token = response.json()['access_token']
#         refresh_token = response.json()['refresh_token']
#         assert response.json() ==  {
#                 "access_token": access_token,
#                 "refresh_token": refresh_token, 
#                 "id" : 1,
#                 "full_name" : "Test Consumer",
#                 "email" : "test@example.com",
#                 "phone_number" : "+911234567891" 
#                 }

#16
# def test_user_consumer_verify_otp_fails():
#     register =test_register_user_consumer()
#     if register == True:
#         otp = ''
#         the_data = {"otp" : otp, "phone_number" : "+911234567891","key" : None}

#         response = client.post(
#             "/user_phone_login/verify_otp",
#             headers={'Content-Type': 'application/json','Accept': 'application/json'},
#             params={"role" : 5},
#             data=json.dumps(the_data)
#         )
#         assert response.status_code == 401
#         assert response.json() ==  {
#                 "status": '401',
#                 "message": 'OTP is not valid' 
#                 }

#17
# def test_user_consumer_login_token_success():
#     register =test_register_user_consumer()
#     if register == True:
#         the_data = {"phone_number" : "+911234567891"}

#         response = client.post(
#             "/user_phone_login",
#             headers={'Content-Type': 'application/json','Accept': 'application/json'},
#             params={"role" : 5},
#             data=json.dumps(the_data)
#         )
#         otp = ''
#         the_data = {"otp" : otp, "phone_number" : "+911234567891","key" : None}

#         response = client.post(
#             "/user_phone_login/verify_otp",
#             headers={'Content-Type': 'application/json','Accept': 'application/json'},
#             params={"role" : 5},
#             data=json.dumps(the_data)
#         )
#         token = response.json()["access_token"]
#         headers={"Authorization" : f"Bearer {token}"}
#         response = client.get(
#             "/user_phone_login/verify_otp/token",
#             headers=headers
#         )
#         assert response.status_code == 200
#         assert response.json() == {
#                 "status_code": 200,
#                 "status":'Success', 
#                 "Message" : "User login Successfully",
#                 "id" : 1,
#                 "full_name" : "Test Consumer",
#                 "email" : "test@example.com",
#                 "phone_number" : "+911234567891"
#                 }

#18
# def test_user_consumer_login_token_fails():
#     register =test_register_user_consumer()
#     if register == True:
#         the_data = {"phone_number" : "+911234567891"}

#         response = client.post(
#             "/user_phone_login",
#             headers={'Content-Type': 'application/json','Accept': 'application/json'},
#             params={"role" : 5},
#             data=json.dumps(the_data)
#         )

#         otp = ''
#         the_data = {"otp" : otp, "phone_number" : "+911234567891","key" : None}

#         response = client.post(
#             "/user_phone_login/verify_otp",
#             headers={'Content-Type': 'application/json','Accept': 'application/json'},
#             params={"role" : 5},
#             data=json.dumps(the_data)
#         )
#         token = response.json()["access_token"]
#         truncate = truncation('users')
#         if truncate:
#             headers={"Authorization" : f"Bearer {token}"}
#             response = client.get(
#                 "/user_phone_login/verify_otp/token",
#                 headers=headers
#             )
#             assert response.status_code == 409
#             assert response.json() == {
#                 "detail":{
#                     "status":'Error',
#                     "message":'No user found'
#                     }
#                     }            

#19
def test_refresh_email_token_success():
    register =test_register_user_consumer()
    if register:
        the_data = {"username": "test@example.com", "password" : "Abcdefgh@123"}

        response = client.post(
            "/user_email_login",
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            params={"role":5},
            data=the_data
        )
        print("first",response.json())

        refresh_token = response.json()["refresh_token"]

        headers={"Authorization" : f"Bearer {refresh_token}"}
        response = client.get(
            "/refresh_token",
            headers=headers
        )
        access_token = response.json()["access_token"]
        print("second",response.json())
        assert response.status_code == 200
        assert response.json() == { 
                    "access_token" : access_token
                }

#20
def test_refresh_email_token_fails():
    register =test_register_user_consumer()
    if register:
        the_data = {"username": "test@example.com", "password" : "Abcdefgh@123"}

        response = client.post(
            "/user_email_login",
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            params={"role":5},
            data=the_data
        )
        print("first",response.json())

        refresh_token = response.json()["refresh_token"]
        truncate = truncation(table='users')
        if truncate:
            headers={"Authorization" : f"Bearer {refresh_token}"}
            response = client.get(
                "/refresh_token",
                headers=headers
            )
            # access_token = response.json()["access_token"]
            # print("second",access_token)
            # assert False
            assert response.status_code == 404
            assert response.json() == { 
                "detail" : {
                "status_code": 404,
                "status":'Error', 
                "message" : "No user found"
                }
                }

