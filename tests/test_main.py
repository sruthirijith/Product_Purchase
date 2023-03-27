from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

####################GLOBAL#################################
#1
def test_get_countries():
    response = client.get("/country")
    assert response.status_code == 200
    print(response.json())
    assert response.json() == {
       "country": [
    {
      "name": "India",
      "flag": None,
      "country_code": "+91",
      "currency_symbol": "₹"
    }
  ]
    }

def test_get_id_proofs():
    response = client.get("/get_id_proof_or_address_proof")
    assert response.status_code == 200
    print(response.json())
    assert response.json() == {
        "id_proofs": [
        {
        "id": 1,
        "id_type": "AADHAAR"
        },
        {
        "id": 2,
        "id_type": "PAN"
        },
        {
        "id": 3,
        "id_type": "VOTERS ID"
        }
    ]
    }

