from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "product-api"}


def test_list_products():
    response = client.get("/products")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_existing_product():
    response = client.get("/products/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Notebook"


def test_missing_product_is_404():
    response = client.get("/products/999")
    assert response.status_code == 404


def test_filter_products_under_price_inclusive():
    response = client.get("/products/under-price", params={"max_price": 1.25})
    assert response.status_code == 200
    assert [p["name"] for p in response.json()] == ["Pen"]


def test_negative_price_limit_is_rejected():
    response = client.get("/products/under-price", params={"max_price": -1})
    assert response.status_code == 422
