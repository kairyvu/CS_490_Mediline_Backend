import requests

response = requests.put(
    "http://localhost:5000/chat/appointment/301",
    json={
        "user_id": 703,
        "appointment_id": 303,
        "message": "Hello Doctor23, I have a question about my medication."
    }
)

print(response.status_code)
print(response.json())


