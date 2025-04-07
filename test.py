import requests


response = requests.post(

    "http://localhost:5000/patients/appointments",
    json={"patient_id": "565","doctor_id": "52", "start_time" : "2025-4-21 00:00", "end_time" : "2025-04-30 00:00"}
)


print(response.json())