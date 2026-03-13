import requests
# 1. Register admin to get token
res = requests.post("http://localhost:8000/api/v1/auth/register", json={
    "name": "Test Admin 5",
    "email": "testadmin5@test.com",
    "password": "password",
    "admin_secret": "supersecretjootrh"
})
token = res.json().get("access_token")

res1 = requests.get("http://localhost:8000/api/v1/admin/download-report?period=all", headers={"Authorization": f"Bearer {token}"})
print("Report status:", res1.status_code)

res2 = requests.get("http://localhost:8000/api/v1/admin/download-mentors", headers={"Authorization": f"Bearer {token}"})
print("Mentors status:", res2.status_code)
