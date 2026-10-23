from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from psycopg.errors import ForeignKeyViolation

from app.database import get_connection

app = FastAPI(title="Order API", version="1.0.0")


class OrderRequest(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=50)


class Order(BaseModel):
    id: int
    product_id: int
    quantity: int


@app.get("/health")
def health():
    return {"status": "ok", "service": "order-api"}


@app.get("/orders", response_model=list[Order])
def list_orders():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, product_id, quantity FROM orders ORDER BY id"
            )
            return cur.fetchall()


@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, product_id, quantity
                FROM orders
                WHERE id = %s
                """,
                (order_id,),
            )
            order = cur.fetchone()

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


@app.post("/orders", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(order: OrderRequest):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO orders (product_id, quantity)
                    VALUES (%s, %s)
                    RETURNING id, product_id, quantity
                    """,
                    (order.product_id, order.quantity),
                )
                return cur.fetchone()
    except ForeignKeyViolation as exc:
        raise HTTPException(
            status_code=404, detail="Product not found"
        ) from exc