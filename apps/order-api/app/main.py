from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="Order API", version="1.0.0")

# Demo-only in-memory store: orders reset when the process restarts and are not shared
# between replicas. PostgreSQL integration is a separate application-development step.
ORDERS: list[dict] = []
NEXT_ORDER_ID = 1


class OrderRequest(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=100)


class Order(BaseModel):
    id: int
    product_id: int
    quantity: int


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "order-api"}


@app.get("/orders", response_model=list[Order])
def list_orders() -> list[dict]:
    return ORDERS


@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: int) -> dict:
    for order in ORDERS:
        if order["id"] == order_id:
            return order
    raise HTTPException(status_code=404, detail="Order not found")


@app.post("/orders", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(order: OrderRequest) -> dict:
    global NEXT_ORDER_ID
    created = {"id": NEXT_ORDER_ID, **order.model_dump()}
    ORDERS.append(created)
    NEXT_ORDER_ID += 1
    return created
