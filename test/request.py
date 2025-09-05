import requests
import json

IP = "192.168.151.133"

# Base URL of the API (请根据实际情况修改，比如 http://localhost:5000)
BASE_URL = "http://192.168.151.133:5000"

# Endpoint
ENDPOINT = "/api/v1/orders"
url = BASE_URL + ENDPOINT

# Request body
payload = {   
    "customer_id": "CUST-123",   
    "requested_resources": {  "cpu_cores": 2,     
                              "memory_gb": 8,    
                              "storage_tb": 2},  
     "duration_months": 12 } 

# Headers
headers = {
    "Content-Type": "application/json"
}  

def test_create_order():
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        print("Status Code:", response.status_code)
        try:
            print("Response JSON:", response.json())
        except ValueError:
            print("Response Text:", response.text)
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)

if __name__ == "__main__":
    test_create_order()