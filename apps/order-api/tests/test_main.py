import pytest
from fastapi.testclient import TestClient
from app.main import app, ORDERS
import app.main as order_module

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_orders():
    ORDERS.clear()
    order_module.NEXT_ORDER_ID = 1
    yield
    ORDERS.clear()
    order_module.NEXT_ORDER_ID = 1


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_and_read_order():
    response = client.post("/orders", json={"product_id": 1, "quantity": 2})
    assert response.status_code == 201
    assert response.json() == {"id": 1, "product_id": 1, "quantity": 2}
    assert client.get("/orders/1").status_code == 200


def test_quantity_must_be_positive():
    response = client.post("/orders", json={"product_id": 1, "quantity": 0})
    assert response.status_code == 422


def test_product_id_must_be_positive():
    response = client.post("/orders", json={"product_id": 0, "quantity": 1})
    assert response.status_code == 422


def test_missing_order_is_404():
    assert client.get("/orders/99").status_code == 404
