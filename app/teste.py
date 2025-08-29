import requests

url = "https://bizlink-production.up.railway.app/users/me"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzU2NDg0MDk2fQ.fhecMpF0qWWdpk8abwY3qbkNm6OdNhVGO04_8FAwifM"
}

response = requests.get(url, headers=headers)

print("Status:", response.status_code)
try:
    print("Resposta JSON:", response.json())
except Exception:
    print("Resposta bruta:", response.text)
