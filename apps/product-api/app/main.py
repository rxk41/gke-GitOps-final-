from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Product API", version="1.0.0")

# Demo data only. Replace with a repository/database layer in the persistence exercise.
SAMPLE_PRODUCTS = [
    {"id": 1, "name": "Notebook", "price": 4.50},
    {"id": 2, "name": "Pen", "price": 1.25},
]


class Product(BaseModel):
    id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=120)
    price: float = Field(ge=0, allow_inf_nan=False)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness endpoint; does not expose environment variables or secrets."""
    return {"status": "ok", "service": "product-api"}


@app.get("/products", response_model=list[Product])
def list_products() -> list[dict]:
    return SAMPLE_PRODUCTS


@app.get("/products/under-price", response_model=list[Product])
def get_products_under_price(max_price: float = Query(ge=0)) -> list[dict]:
    """Return every product whose price is less than or equal to max_price."""
    return [product for product in SAMPLE_PRODUCTS if product["price"] <= max_price]


@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int) -> dict:
    for product in SAMPLE_PRODUCTS:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")


@app.get("/products/under-price", response_model=list[Product])
def get_products_under_price(max_price: float = Query(ge=0)) -> list[dict]:
    """Return every product whose price is less than or equal to max_price."""
    return [product for product in SAMPLE_PRODUCTS if product["price"] <= max_price]
