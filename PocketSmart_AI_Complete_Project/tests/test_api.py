import os
os.environ["DATABASE_URL"] = "sqlite:///./test_pocketsmart.db"
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r=client.get('/api/health'); assert r.status_code==200; assert r.json()['status']=='ok'

def test_register_login_and_home():
    email='test@example.com'
    client.post('/register',json={'name':'Test User','email':email,'password':'password123'})
    r=client.post('/login',json={'email':email,'password':'password123'})
    assert r.status_code==200
    token=r.json()['access_token']
    h=client.post('/generate-home',headers={'Authorization':f'Bearer {token}'},json={'budget':50000,'style':'Modern','priorities':'value','rooms':[{'room':'Living Room','category':'lighting','item':'LED light','quantity':2}]})
    assert h.status_code==200
    assert h.json()['planner']=='home'
