from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas,services
from app.database import get_db
from app.auth import get_current_user
from app.utils import admin_required
from app.services import get_depleting_products

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
def add_stock(stock: schemas.Stock, user=Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if the product exists and belongs to the correct company
    check_product = db.query(models.Product).filter(
        models.Product.id == stock.product_id,
        models.Product.company_id == user.company_id
    ).first()

    if not check_product:
        raise HTTPException(status_code=404, detail=f'Product with product id:{stock.product_id} not found')

    # Add a new record in the StockTracker table for historical record
    new_stock_tracker = models.StockTracker(
        company_id=user.company_id,
        product_id=stock.product_id,
        stock_added=stock.stock_count,
    )
    
    db.add(new_stock_tracker)

    # Check if a stock record exists for this company and product
    existing_stock = db.query(models.Stock).filter_by(
        company_id=user.company_id, product_id=stock.product_id
    ).first()

    if existing_stock:
        # If stock exists, update the stock_count by adding the new stock to the existing one
        existing_stock.stock_count += stock.stock_count
    else:
        # If no stock exists for this product, create a new entry in the Stock table
        new_stock = models.Stock(
            company_id=user.company_id,
            product_id=stock.product_id,
            stock_count=stock.stock_count,
        )
        db.add(new_stock)

    # Commit changes
    db.commit()
    db.refresh(new_stock_tracker)  # Refresh stock_tracker to return its current state

    return {"message": "Stock added successfully"}



@router.get('/',status_code=status.HTTP_200_OK)
def get_stock(user=Depends(get_current_user),db:Session=Depends(get_db)):
    my_stock = services.get_all_stock(user,db)
    if my_stock is None:
         raise HTTPException(status_code=404, detail="Stock not found")
    
    

    return {"my_stock":my_stock}

@router.get('/metrics',status_code=status.HTTP_200_OK)
def get_stock_data(user=Depends(get_current_user),db:Session=Depends(get_db)):
    stock_metrics = services.get_stock_metrics(user,db)
    stock_worth = services.get_stock_worth(user,db)
    return {"stock_metrics":stock_metrics,"stock_worth":stock_worth}
    

