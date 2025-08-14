from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, condecimal
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Numeric, Text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import logging
import os

# ---- Logging ----
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s - %(message)s"
)
logger = logging.getLogger("product_catalog")

# ---- Database Setup ----
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./app.db")

# SQLite needs check_same_thread=False for use with FastAPI default threadpool
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ProductModel(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    category = Column(String(100), nullable=False, index=True)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---- Schemas ----
class ProductIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=5000)
    price: condecimal(max_digits=10, decimal_places=2) = Field(..., ge=0)
    category: str = Field(..., min_length=1, max_length=100)

class Product(ProductIn):
    id: int

    class Config:
        from_attributes = True

# ---- App ----
app = FastAPI(title="Product Catalog Service", version="1.0.0")

# CORS (optional; handy if frontends test it)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

# CRUD Endpoints
@app.get("/products", response_model=List[Product])
def list_products(db: Session = Depends(get_db)):
    products = db.query(ProductModel).all()
    return products

@app.post("/products", response_model=Product, status_code=201)
def create_product(payload: ProductIn, db: Session = Depends(get_db)):
    product = ProductModel(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    logger.info("Created product id=%s name=%s", product.id, product.name)
    return product

@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, payload: ProductIn, db: Session = Depends(get_db)):
    product = db.get(ProductModel, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in payload.model_dump().items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    logger.info("Updated product id=%s", product.id)
    return product

@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(ProductModel, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    logger.info("Deleted product id=%s", product.id)
    return None

@app.get("/products/search", response_model=List[Product])
def search_products(
    query: str = Query(..., description="Search by name or category (case-insensitive)"),
    db: Session = Depends(get_db)
):
    # Simple LIKE search across name and category
    like = f"%{query.lower()}%"
    results = db.query(ProductModel).filter(
        (ProductModel.name.ilike(like)) | (ProductModel.category.ilike(like))
    ).all()
    logger.info("Search query='%s' results=%d", query, len(results))
    return results
