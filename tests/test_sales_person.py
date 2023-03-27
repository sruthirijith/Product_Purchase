from fastapi.testclient import TestClient
from tests.crud import truncation

from main import app

client = TestClient(app)


################USER REGISTER##############
#1
def test_register_user():
    truncate = truncation(table='users')
    if truncate == True:
        response = client.post(
            "/register",
            json={
                "full_name": "Test Merchant",
                "email": "test@example.com",
                "password": "Abcdefgh@123",
                "phone_number": "+911234567891",
                "country_code": "",
                "referred_by": "",
                "role_id": 4
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
                "username": "Test Merchant",
                "phonenumber": "+911234567891",
                "role":4,
                "id" :1
        }
        return True


###############REGISTER MERCHANT PROFILE########################
#2
def test_register_merchant_profile():
    response = client.post(
        "/create_merchant_profile/",
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "merchant_account_number": "1234567",
            "authorized_person": "test",
            "dob": "2023-01-31",
            "gender": 1,
            "profile_image": "image",
            "users_id": 1,
            "sales_person_id": 101
        }
    )
    assert response.status_code == 200
    assert response.json() == {
            "status_code" : 200,
            "status" : "Success",
            "message" : "Merchant added successfully",
            "merchant_id" : 1
    }


#3
def test_register_merchant_profile_without_user():
    response = client.post(
        "/create_merchant_profile/",
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "merchant_account_number": "1234567",
            "authorized_person": "test",
            "dob": "2023-01-31",
            "gender": 1,
            "profile_image": "image",
            "users_id": 2,
            "sales_person_id": 101
        }
    )
    truncate = truncation(table='users')
    if truncate :
        assert response.status_code == 404
        assert response.json() == {
                'detail' : {
                    "status_code" : 404,
                    "status" : "Error",
                    "message" : "User not exist"
                }
        }


#4
def test_register_merchant_duplicate():
    test_register_user()
    response = client.post(
        "/create_merchant_profile/",
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "merchant_account_number": "1234567",
            "authorized_person": "test",
            "dob": "2023-01-31",
            "gender": 1,
            "profile_image": "image",
            "users_id": 1,
            "sales_person_id": 101
        }
    )
    response = client.post(
        "/create_merchant_profile/",
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "merchant_account_number": "1234567",
            "authorized_person": "test",
            "dob": "2023-01-31",
            "gender": 1,
            "profile_image": "image",
            "users_id": 1,
            "sales_person_id": 101
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        'detail' : {
            "status_code" : 200,
            "status" : "Error",
            "message" : "Merchant already exist",
            "merchant_id" : 1
        }
    }
    

# ####################DISPLAY MERCHANT PROFILE######################
#5
def test_display_merchant_profile():
    test_register_user()
    test_register_merchant_profile()
    response = client.post(
        '/display_merchant_profile',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "sales_person_id" : 101
        }
    )
    assert response.status_code == 200
    assert response.json() ==  [
        {
        "users_id": 1,
        "full_name": "Test Merchant",
        "email": "test@example.com",
        "phone_number": "+911234567891",
        "id": 1,
        "merchant_account_number": "1234567",
        "merchant_name": None,
        "authorized_person": "test",
        "kyc_doc_type": None,
        "kyc_doc": None,
        "channel_partner_id": None,
        "dob": "2023-01-31",
        "gender": 1,
        "profile_image": "image"
    }
    ]


#6
def test_display_merchant_profile_without_data():
    test_register_user()
    test_register_merchant_profile()
    response = client.post(
        '/display_merchant_profile',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "sales_person_id" : ''
        }
    )
    assert response.status_code == 400
    assert response.json() == {
        'detail' : {
                "status_code" : 400,
                "status" : "Error",
                "message" : "Sales person id not given"
            }
    }


# #####################UPDATE MERCHANT PROFILE#######################
#7
def test_update_merchant_profile_all_vaues():
    test_register_user()
    test_register_merchant_profile()
    response = client.put(
        '/update_merchant_profile',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "merchant_account_number": "0987654",
            "authorized_person": "test",
            "dob": "2023-02-01",
            "gender": 1,
            "profile_image": "string",
            "merchant_id": 1
        }
    )
    assert response.status_code == 200
    assert response.json() == {
            "status_code" : 200,
            "status" : "Success",
            "message" : "Sucessfully updated",
            "merchant_id" : 1
    }

#8
def test_update_merchant_profile_some_values():
    test_register_user()
    test_register_merchant_profile()
    response = client.put(
        '/update_merchant_profile',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "merchant_account_number": "0987654",
            "authorized_person": "test123",
            "merchant_id": 1
        }
    )
    assert response.status_code == 200
    assert response.json() == {
            "status_code" : 200,
            "status" : "Success",
            "message" : "Sucessfully updated",
            "merchant_id" : 1
    }

#9
def test_update_merchant_profile_merchant_not_exist():
    test_register_user()
    test_register_merchant_profile()
    response = client.put(
        '/update_merchant_profile',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "merchant_account_number": "0987654",
            "authorized_person": "test123",
            "merchant_id" : 2
        }
    )
    assert response.status_code == 404
    assert response.json() == {
            'detail' : {
                "status_code" : 404,
                "status" : "Error",
                "message" : "Merchant not registered"
            }
    }


#10
def test_update_merchant_profile_no_data():
    test_register_user()
    test_register_merchant_profile()
    response = client.put(
        '/update_merchant_profile',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "merchant_id" : 1
        }
    )
    assert response.status_code == 400
    assert response.json() == {
            'detail' : {
                "status_code" : 400,
                "status" : "Error",
                "message" : "No data to update"
            }
    }


# ##########################CREATE MERCHANT BUSINESS############################
#11
def test_create_merchant_business():
    test_register_user()
    test_register_merchant_profile()
    response = client.post(
        '/create_merchant_business/',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "registered_business_name": "google",
            "registered_business_number": "9087654321",
            "website": "google.com",
            "business_description": "google",
            "business_category": 1,
            "dba": "string",
            "address": "usa",
            "operating_address": "string",
            "postal_code": "986322",
            "operating_postal_code": "string",
            "merchant_id": 1
        }
    )
    assert response.status_code == 200
    assert response.json() == {
            "status_code": 200,
            "status": "Success",
            "message": "Merchant profile created Successfully",
            "merchant_id" : 1
    }


#12
def test_create_merchant_business_for_invalid_merchat_id():
    test_register_user()
    test_register_merchant_profile()
    response = client.post(
        '/create_merchant_business/',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "registered_business_name": "google",
            "registered_business_number": "9087654321",
            "website": "google.com",
            "business_description": "google",
            "business_category": 1,
            "dba": "string",
            "address": "usa",
            "operating_address": "string",
            "postal_code": "986322",
            "operating_postal_code": "string",
            "merchant_id": 2
        }
    )
    assert response.status_code == 404
    assert response.json() == {
        'detail' : {
                "status_code" : 404,
                "status" : "Error",
                "message" : "Merchant not exist"
            }
    }


#13
def test_create_merchant_business_profile_check_duplication():
    test_register_user()
    test_register_merchant_profile()
    response = client.post(
        '/create_merchant_business/',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "registered_business_name": "google",
            "registered_business_number": "9087654321",
            "website": "google.com",
            "business_description": "google",
            "business_category": 1,
            "dba": "string",
            "address": "usa",
            "operating_address": "string",
            "postal_code": "986322",
            "operating_postal_code": "string",
            "merchant_id": 1
        }
    )
    response = client.post(
        '/create_merchant_business/',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "registered_business_name": "google",
            "registered_business_number": "9087654321",
            "website": "google.com",
            "business_description": "google",
            "business_category": 1,
            "dba": "string",
            "address": "usa",
            "operating_address": "string",
            "postal_code": "986322",
            "operating_postal_code": "string",
            "merchant_id": 1
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        'detail' : {
                "status_code" : 200,
                "status" : "Error",
                "message" : "Merchant business info already exist",
                "merchant_id" : 1
            }
    }


####################DISPLAY MERCHANT BUSINESS INFO########################
#14
def test_display_merchant_business_info():
    test_create_merchant_business()
    response = client.post(
        '/display_merchant_business_profile/',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "sales_person_id" : 101
        }
    )
    assert response.status_code == 200
    assert response.json() == [
        {
        "id": 1,
        "merchant_id": 1,
        "registered_business_name": "google",
        "registered_business_number": "9087654321",
        "website": "google.com",
        "business_description": "google",
        "business_category": 1,
        "address": "usa",
        "postal_code": "986322"
        }
    ]


#15
def test_display_merchant_business_info_without_data():
    test_create_merchant_business()
    response = client.post(
        '/display_merchant_profile',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "sales_person_id" : ''
        }
    )
    assert response.status_code == 400
    assert response.json() == {
        'detail' : {
                "status_code" : 400,
                "status" : "Error",
                "message" : "Sales person id not given"
            }
    }


########################UPDATE MERCHANT BUSINESS INFO############################
#16
def test_update_merchant_business_profile_all_values():
    test_create_merchant_business()
    response = client.put(
        '/update_merchant_business_profile/',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "registered_business_name": "w3school",
            "registered_business_number": "9087654321",
            "website": "w3school.com",
            "business_description": "learning",
            "business_category": 1,
            "dba": "w3school.learning",
            "address": "ind",
            "operating_address": "ker",
            "postal_code": "897654",
            "operating_postal_code": "897612",
            "merchant_id": 1
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "status_code": 200,
        "status": "Success",
        "message": "Successfully updated merchant business profile",
        "merchant_id" : 1
    }


#17
def test_update_merchant_business_profile_some_values():
    test_create_merchant_business()
    response = client.put(
        '/update_merchant_business_profile/',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "registered_business_name": "w3school",
            "website": "w3school.com",
            "business_description": "learning",
            "merchant_id": 1
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "status_code": 200,
        "status": "Success",
        "message": "Successfully updated merchant business profile",
        "merchant_id" : 1
    }


#18
def test_update_merchant_business_profile_merchant_id_not_exist():
    test_create_merchant_business()
    response = client.put(
        '/update_merchant_business_profile/',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "registered_business_name": "w3school",
            "website": "w3school.com",
            "business_description": "learning",
            "merchant_id": 2
        }
    )
    assert response.status_code == 404
    assert response.json() == {
        'detail' : {
                "status_code" : 404,
                "status" : "Error",
                "message" : "Merchant not exist"
            }
    }


#19
def test_update_merchant_business_profile_does_not_exist():
    test_create_merchant_business()
    truncation(table = 'merchant_business_info')
    response = client.put(
        '/update_merchant_business_profile/',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "registered_business_name": "w3school",
            "website": "w3school.com",
            "business_description": "learning",
            "merchant_id": 1
        }
    )   
    assert response.status_code == 404
    assert response.json() == {
        'detail' : {
                "status_code" : 404,
                "status" : "Error",
                "message" : "Merchant profile not exist"
            }
    }

######################CREATE MERCHANT TAX INFORMATIOM###########################
#20
def test_create_merchant_tax_information_sucess():
    test_register_user()
    test_register_merchant_profile()
    response = client.post(
        '/create_merchant_tax_info/',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "name_on_pan": "PAN",
            "pan_number": "ASD123",
            "gstin_doc": "string",
            "pan_doc": "string",
            "tan_doc": "string",
            "id_proof": "Licence",
            "id_proof_type": 1,
            "id_proof_doc": "string",
            "address_proof": "aadhaar",
            "address_proof_type": 1,
            "address_proof_doc": "string",
            "merchant_id": 1
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "status_code": 200,
        "status" : "success",
        "message" : "Merchant_Tax_Info added successfully",
        "merchant_id" : 1
    }

#21
def test_create_merchant_tax_info_invalid_merchant_id():
    test_register_user()
    test_register_merchant_profile()
    response = client.post(
        '/create_merchant_tax_info/',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "name_on_pan": "PAN",
            "pan_number": "ASD123",
            "gstin_doc": "string",
            "pan_doc": "string",
            "tan_doc": "string",
            "id_proof": "Licence",
            "id_proof_type": 1,
            "id_proof_doc": "string",
            "address_proof": "aadhaar",
            "address_proof_type": 1,
            "address_proof_doc": "string",
            "merchant_id": 2
        }
    )
    assert response.status_code == 404
    assert response.json() == {
        'detail' : {
                "status_code" : 404,
                "status" : "Error",
                "message" : "Merchant not exist"
            }
    }


#22
def test_create_merchant_tax_info_duplicate():
    test_register_user()
    test_register_merchant_profile()
    response = client.post(
        '/create_merchant_tax_info/',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "name_on_pan": "PAN",
            "pan_number": "ASD123",
            "gstin_doc": "string",
            "pan_doc": "string",
            "tan_doc": "string",
            "id_proof": "Licence",
            "id_proof_type": 1,
            "id_proof_doc": "string",
            "address_proof": "aadhaar",
            "address_proof_type": 1,
            "address_proof_doc": "string",
            "merchant_id": 1
        }
    )
    response = client.post(
        '/create_merchant_tax_info/',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "name_on_pan": "PAN",
            "pan_number": "ASD123",
            "gstin_doc": "string",
            "pan_doc": "string",
            "tan_doc": "string",
            "id_proof": "Licence",
            "id_proof_type": 1,
            "id_proof_doc": "string",
            "address_proof": "aadhaar",
            "address_proof_type": 1,
            "address_proof_doc": "string",
            "merchant_id": 1
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        'detail' : {
                "status_code" : 200,
                "status" : "Error",
                "message" : "Merchant tax information already exist",
                "merchant_id" : 1
            }
    }


###################DISPLAY MERCHAT TAX INFORMATION##########################
#23
def test_display_merchant_tax_info():
    test_create_merchant_tax_information_sucess()
    response = client.post(
        '/display_merchant_tax_info/',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "sales_person_id" : "101"
        }
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "merchant_id": 1,
            "name_on_pan": "PAN",
            "pan_number": "ASD123",
            "pan_doc": "string",
            "gstin_doc": "string",
            "tan_doc": "string",
            "id_proof": "Licence",
            "id_proof_type": 1,
            "id_proof_doc": "string",
            "address_proof": "aadhaar",
            "address_proof_type": 1,
            "address_proof_doc": "string"
        }
    ]


#24
def test_display_merchant_tax_info_without_data():
    test_create_merchant_tax_information_sucess()
    response = client.post(
        '/display_merchant_profile',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "sales_person_id" : ''
        }
    )
    assert response.status_code == 400
    assert response.json() == {
        'detail' : {
                "status_code" : 400,
                "status" : "Error",
                "message" : "Sales person id not given"
            }
    }


######################UPDATE MERCHANT TAX INFORMATION########################
#25
def test_update_merchant_tax_info_all_values():
    test_create_merchant_tax_information_sucess()
    response = client.put(
        '/update_merchant_tax_info',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
                "name_on_pan": "pan",
                "pan_number": "123456",
                "gstin_doc": "gstindoc",
                "pan_doc": "pandoc",
                "tan_doc": "tandoc",
                "id_proof": "licence",
                "id_proof_type": 1,
                "id_proof_doc": "idproofdoc",
                "address_proof": "addresproof",
                "address_proof_type": 1,
                "address_proof_doc": "adresproofdoc",
                "merchant_id": 1
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "status_code": 200,
        "status" : "success",
        "message" : "Merchant tax info updated successfully",
        "merchant_id" : 1
    }


#26
def test_update_merchant_tax_info_some_values():
    test_create_merchant_tax_information_sucess()
    response = client.put(
        '/update_merchant_tax_info',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
                "name_on_pan": "pan",
                "pan_number": "123456",
                "merchant_id": 1
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "status_code": 200,
        "status" : "success",
        "message" : "Merchant tax info updated successfully",
        "merchant_id" : 1
    }


#27
def test_update_merchant_tax_info_invalid_merchant():
    test_create_merchant_tax_information_sucess()
    response = client.put(
        '/update_merchant_tax_info',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
                "name_on_pan": "pan",
                "pan_number": "123456",
                "merchant_id": 2
        }
    )
    assert response.status_code == 404
    assert response.json() == {
        'detail' : {
                "status_code" : 404,
                "status" : "Error",
                "message" : "Merchant not exist"
            }
    }


#28
def test_update_merchant_tax_info_does_not_exist():
    test_create_merchant_tax_information_sucess()
    truncation(table = "merchant_tax_information")
    response = client.put(
        '/update_merchant_tax_info',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
                "name_on_pan": "pan",
                "pan_number": "123456",
                "merchant_id": 1
        }
    )
    assert response.status_code == 404
    assert response.json() == {
        'detail' : {
                "status_code" : 404,
                "status" : "Error",
                "message" : "Merchant tax information not exist"
            }
    }


###############CREATE MERCHANT BANK DETAILS######################
#29
def test_create_merchant_bank_details_sucess():
    test_register_user()
    test_register_merchant_profile()
    response = client.post(
        '/create_merchant_bank_details/',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
                "current_account_name": "tester",
                "account_number": "5467382910",
                "ifsc_number": "4567",
                "branch_name": "ind",
                "bank_name": "sib",
                "merchant_id": 1
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "status_code": 200,
        "status": "Success",
        "message": "Bank details created Successfully",
        "merchant_id" : 1
    }


#30
def test_create_merchant_bank_detail_invalid_merchant():
    test_register_user()
    test_register_merchant_profile()
    response = client.post(
        '/create_merchant_bank_details/',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
                "current_account_name": "tester",
                "account_number": "5467382910",
                "ifsc_number": "4567",
                "branch_name": "ind",
                "bank_name": "sib",
                "merchant_id": 2
        }
    )
    assert response.status_code == 404
    assert response.json() == {
        'detail' : {
                "status_code" : 404,
                "status" : "Error",
                "message" : "Merchant not exist"
            }
    }


#31
def test_create_merchant_bank_detail_duplicate():
    test_register_user()
    test_register_merchant_profile()
    response = client.post(
        '/create_merchant_bank_details/',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
                "current_account_name": "tester",
                "account_number": "5467382910",
                "ifsc_number": "4567",
                "branch_name": "ind",
                "bank_name": "sib",
                "merchant_id": 1
        }
    )
    response = client.post(
        '/create_merchant_bank_details/',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
                "current_account_name": "tester",
                "account_number": "5467382910",
                "ifsc_number": "4567",
                "branch_name": "ind",
                "bank_name": "sib",
                "merchant_id": 1
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        'detail' : {
                "status_code" : 200,
                "status" : "Error",
                "message" : "Bank details already exist",
                "merchant_id" : 1
            }
    }


################DISPLAY MERCHANT BANK DETAILS###########################
#32
def test_display_merchant_bank_detsil():
    test_create_merchant_bank_details_sucess()
    response = client.post(
        '/display_merchant_bank_details/',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "sales_person_id" : 101
        }
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "merchant_id": 1,
            "current_account_name": "tester",
            "account_number": "5467382910",
            "ifsc_number": "4567",
            "branch_name": "ind",
            "bank_name": "sib"
        }
    ]


#33
def test_display_merchant_bank_detail_without_data():
    test_create_merchant_bank_details_sucess()
    response = client.post(
        '/display_merchant_bank_details',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "sales_person_id" : ''
        }
    )
    assert response.status_code == 400
    assert response.json() == {
        'detail' : {
                "status_code" : 400,
                "status" : "Error",
                "message" : "Sales person id not given"
            }
    }


#######################UPDATE MERCHANT BANK DETAIL######################
#34
def test_update_merchant_bank_detail_all_data():
    test_create_merchant_bank_details_sucess()
    response = client.put(
        '/update_merchant_bank_details',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "current_account_name": "test",
            "account_number": "123456",
            "ifsc_number": "7890",
            "branch_name": "uk",
            "bank_name": "asd",
            "merchant_id": 1
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "status_code": 200,
        "status": "Success",
        "message": "Bank details Successfully updated",
        "merchant_id" : 1
    }


#35
def test_update_merchant_bank_detail_some_data():
    test_create_merchant_bank_details_sucess()
    response = client.put(
        '/update_merchant_bank_details',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "current_account_name": "test",
            "account_number": "123456",
            "merchant_id": 1
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "status_code": 200,
        "status": "Success",
        "message": "Bank details Successfully updated",
        "merchant_id" : 1
    }


#36
def test_update_merchant_bank_detail_invalid_merchant():
    test_create_merchant_bank_details_sucess()
    response = client.put(
        '/update_merchant_bank_details',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "current_account_name": "test",
            "account_number": "123456",
            "merchant_id": 2
        }
    )
    assert response.status_code == 404
    assert response.json() == {
        'detail' : {
                "status_code" : 404,
                "status" : "Error",
                "message" : "Merchant not exist"
            }
    }


#37
def test_update_merchant_bank_detail_does_not_exist():
    test_create_merchant_bank_details_sucess()
    truncation(table = "merchant_bank_details")
    response = client.put(
        '/update_merchant_bank_details',
        headers = {'access_token' : 'dbc5bd406ce539152186b5a952bd301dff4806bc07128ae21f657d848f3fe792'},

        json = {
            "current_account_name": "test",
            "account_number": "123456",
            "merchant_id": 1
        }
    )
    assert response.status_code == 404
    assert response.json() == {
        'detail' : {
                "status_code" : 404,
                "status" : "Error",
                "message" : "Bank details not exist"
            }
    }