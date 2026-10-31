from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from decimal import Decimal
from app.models.catalog import Product, ProductVariant, Plan, PlanItem
from app.schemas.catalog import (
    ProductCreate, ProductUpdate, ProductVariantCreate,
    PlanCreate, PlanUpdate, PlanItemCreate
)

class CatalogService:
    # --- Products & Variants ---
    @staticmethod
    def get_product(db: Session, product_id: int) -> Product:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {product_id} not found")
        return product

    @staticmethod
    def list_products(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        category: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Product]:
        query = db.query(Product)
        if is_active is not None:
            query = query.filter(Product.is_active == is_active)
        if category:
            query = query.filter(Product.category == category)
        return query.order_by(Product.name.asc()).offset(skip).limit(limit).all()

    @staticmethod
    def create_product(db: Session, data: ProductCreate) -> Product:
        existing = db.query(Product).filter(Product.sku == data.sku).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Product SKU '{data.sku}' already exists")
        
        product = Product(
            sku=data.sku,
            name=data.name,
            description=data.description,
            category=data.category,
            is_active=data.is_active
        )
        db.add(product)
        db.flush()

        if data.variants:
            for v_data in data.variants:
                existing_v = db.query(ProductVariant).filter(ProductVariant.sku == v_data.sku).first()
                if existing_v:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Variant SKU '{v_data.sku}' already exists")
                variant = ProductVariant(
                    product_id=product.id,
                    sku=v_data.sku,
                    name=v_data.name,
                    attributes=v_data.attributes,
                    unit_price=v_data.unit_price,
                    currency=v_data.currency,
                    is_active=v_data.is_active
                )
                db.add(variant)

        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def add_variant(db: Session, product_id: int, data: ProductVariantCreate) -> ProductVariant:
        product = CatalogService.get_product(db, product_id)
        existing_v = db.query(ProductVariant).filter(ProductVariant.sku == data.sku).first()
        if existing_v:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Variant SKU '{data.sku}' already exists")

        variant = ProductVariant(
            product_id=product.id,
            sku=data.sku,
            name=data.name,
            attributes=data.attributes,
            unit_price=data.unit_price,
            currency=data.currency,
            is_active=data.is_active
        )
        db.add(variant)
        db.commit()
        db.refresh(variant)
        return variant

    # --- Plans & Plan Items ---
    @staticmethod
    def get_plan(db: Session, plan_id: int) -> Plan:
        plan = db.query(Plan).filter(Plan.id == plan_id).first()
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plan {plan_id} not found")
        return plan

    @staticmethod
    def list_plans(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        billing_interval: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Plan]:
        query = db.query(Plan)
        if is_active is not None:
            query = query.filter(Plan.is_active == is_active)
        if billing_interval:
            query = query.filter(Plan.billing_interval == billing_interval)
        return query.order_by(Plan.name.asc()).offset(skip).limit(limit).all()

    @staticmethod
    def create_plan(db: Session, data: PlanCreate) -> Plan:
        existing = db.query(Plan).filter(Plan.code == data.code).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Plan code '{data.code}' already exists")

        plan = Plan(
            code=data.code,
            name=data.name,
            description=data.description,
            billing_interval=data.billing_interval,
            interval_count=data.interval_count,
            base_price=data.base_price,
            currency=data.currency,
            trial_days=data.trial_days,
            is_active=data.is_active
        )
        db.add(plan)
        db.flush()

        if data.items:
            for item_data in data.items:
                product = CatalogService.get_product(db, item_data.product_id)
                if item_data.variant_id:
                    variant = db.query(ProductVariant).filter(
                        ProductVariant.id == item_data.variant_id,
                        ProductVariant.product_id == product.id
                    ).first()
                    if not variant:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Variant {item_data.variant_id} does not belong to Product {product.id}"
                        )
                plan_item = PlanItem(
                    plan_id=plan.id,
                    product_id=product.id,
                    variant_id=item_data.variant_id,
                    quantity=item_data.quantity,
                    unit_price=item_data.unit_price
                )
                db.add(plan_item)

        db.commit()
        db.refresh(plan)
        return plan

    @staticmethod
    def update_product(db: Session, product_id: int, data: ProductUpdate) -> Product:
        product = CatalogService.get_product(db, product_id)
        if data.name is not None:
            product.name = data.name
        if data.description is not None:
            product.description = data.description
        if data.category is not None:
            product.category = data.category
        if data.is_active is not None:
            product.is_active = data.is_active
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def delete_product(db: Session, product_id: int) -> dict:
        product = CatalogService.get_product(db, product_id)
        db.delete(product)
        db.commit()
        return {"success": True, "message": f"Product {product_id} deleted"}

    @staticmethod
    def delete_variant(db: Session, variant_id: int) -> dict:
        variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
        if not variant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Variant {variant_id} not found")
        db.delete(variant)
        db.commit()
        return {"success": True, "message": f"Variant {variant_id} deleted"}

    @staticmethod
    def update_plan(db: Session, plan_id: int, data: PlanUpdate) -> Plan:
        plan = CatalogService.get_plan(db, plan_id)
        if data.name is not None:
            plan.name = data.name
        if data.description is not None:
            plan.description = data.description
        if data.base_price is not None:
            plan.base_price = data.base_price
        if data.is_active is not None:
            plan.is_active = data.is_active
        db.commit()
        db.refresh(plan)
        return plan

    @staticmethod
    def delete_plan(db: Session, plan_id: int) -> dict:
        plan = CatalogService.get_plan(db, plan_id)
        db.delete(plan)
        db.commit()
        return {"success": True, "message": f"Plan {plan_id} deleted"}

