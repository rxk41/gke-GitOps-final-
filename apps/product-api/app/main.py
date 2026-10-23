from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from app.database import get_connection

app = FastAPI(title="Product API", version="2.0.0")

# Demo data only. Replace with a repository/database layer in the persistence exercise.
# SAMPLE_PRODUCTS = [
#     {"id": 1, "name": "Notebook", "price": 4.50},
#     {"id": 2, "name": "Pen", "price": 2.25},
# ]


class Product(BaseModel):
    id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=110)
    price: float = Field(ge=0, allow_inf_nan=False)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness endpoint; does not expose environment variables or secrets."""
    return {"status": "ok", "service": "product-api"}

@app.get("/products", response_model=list[Product])
def list_products():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, price FROM products ORDER BY id"
            )
            return cur.fetchall()


@app.get("/products/under-price", response_model=list[Product])
def get_products_under_price(max_price: float = Query(ge=0)):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, price
                FROM products
                WHERE price <= %s
                ORDER BY id
                """,
                (max_price,),
            )
            return cur.fetchall()


@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, price FROM products WHERE id = %s",
                (product_id,),
            )
            product = cur.fetchone()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product

