from fastapi.testclient import TestClient
from app.main import app, Base, engine, SessionLocal, ProductModel

client = TestClient(app)

def setup_module(module):
    # fresh DB for tests
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_create_and_search_product():
    new_product = {
        "name": "Acoustic Guitar",
        "description": "A 6-string acoustic guitar",
        "price": "199.99",
        "category": "Instruments"
    }
    r = client.post("/products", json=new_product)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["id"] >= 1
    assert data["name"] == "Acoustic Guitar"

    # search by name
    r2 = client.get("/products/search", params={"query": "guitar"})
    assert r2.status_code == 200
    results = r2.json()
    assert len(results) == 1
    assert results[0]["category"] == "Instruments"
