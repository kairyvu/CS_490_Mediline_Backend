import requests


response = requests.put(

    "http://localhost:5000/patients/565",
    json={"patient_id": "565","first_name": "david", "last_name" : "david", "email" : "david@gmail.com", "phone" : "1231231234"}
)


print(response.json())