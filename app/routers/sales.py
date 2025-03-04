from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas,services
from app.models import Company,Product,Stock
from app.database import get_db
from app.auth import get_current_user
from app.services import get_products_by_company
from datetime import date

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
def make_sale(request: schemas.Sale, user=Depends(get_current_user), db: Session = Depends(get_db)):
     # Fetch the user who is making the sale
    user = db.query(models.User).filter(models.User.id == user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Fetch the product that is being sold
    product = db.query(Product).filter(Product.id == request.pid).first()
    products_by_company = get_products_by_company(user,db)

    if product.id not in products_by_company:
        raise HTTPException(status_code=404, detail="Product not found under this company")

    stock = db.query(models.Stock).filter(models.Stock.product_id==request.pid).filter(models.Stock.company_id==user.company_id).first()
    print("Testing stock",stock)
    if not stock:
        raise HTTPException(status_code=404,detail='No stock added yet')

    # Check if there is enough stock for the sale
    if stock.stock_count < request.quantity :
        raise HTTPException(status_code=400, detail="Not enough stock available")
    
    #update stock with revised count
    new_stock_count = stock.stock_count - request.quantity
    stock.stock_count = new_stock_count
    db.commit()

    new_sale = models.Sale(company_id = user.company_id, pid=request.pid, quantity=request.quantity)
    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)

    return {"message": "Sale made successfully", "sale_id": new_sale.id}


@router.get("/", status_code=status.HTTP_200_OK)
def fetch_sales(user=Depends(get_current_user), db: Session = Depends(get_db)):
    # Fetch all sales data and join with the Product table to access selling_price
    sales = db.query(models.Sale).filter(models.Sale.company_id==user.company_id).all()

    sales_data = []
    for sale in sales:
        # amount = sale.quantity * sale.product.selling_price 
        formatted_created_at = sale.created_at.strftime("%H:%M: -> %d- %B -%Y")
        sales_data.append({
            "company_id": sale.company_id,
            "id": sale.id,
            "pid": sale.pid,  
            "quantity": sale.quantity,
            "created_at": formatted_created_at,
            "price":sale.product.selling_price
        })
    return {"sales_data": sales_data}




# @router.put("/{sale_id}", status_code=status.HTTP_202_ACCEPTED)
# def update_sale(sale_id: int, request: schemas.Sale, user=Depends(get_current_user), db: Session = Depends(get_db)):
#     # Fetch the sale to be updated
#     sale = db.query(models.Sale).filter(models.Sale.id == sale_id).first()
#     if not sale:
#         raise HTTPException(status_code=404, detail="Sale not found")

#     # Fetch the product associated with the sale
#     product = db.query(models.Product).filter(models.Product.id == sale.pid).first()
#     if not product:
#         raise HTTPException(status_code=404, detail="Product not found")


#     quantity_difference = request.quantity - sale.quantity
#     sale.quantity = request.quantity
#     product.stock_quantity -= quantity_difference  # Update stock quantity based on the new sale quantity

#     db.commit()

#     return {"message": "Sale updated successfully"}


@router.get('/metrics',status_code=status.HTTP_200_OK)
def get_sales_data(user=Depends(get_current_user),db:Session=Depends(get_db)):
    sales_per_month = services.get_sale_time_data(user,db)
    counts = services.get_sale_counts(user,db)
    return {"sales_metrics":sales_per_month,"counts":counts}





