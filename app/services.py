from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date,datetime
from app.models import Sale,Product,User,Company,Stock,StockTracker
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import get_current_user
from fastapi import HTTPException



def sales_per_day(user:get_current_user,db:Session):
    try:
        sales_per_day= db.query(func.date(Sale.created_at).label("dates"),
                        func.sum(Sale.quantity * Product.selling_price).label("sales")).join(Product,Product.id==Sale.pid).join(Company,Company.id==Sale.company_id
                        ).filter(user.company_id==Company.id).group_by('dates')
        sale_today = sales_per_day.filter(func.date(Sale.created_at)==date.today()).all()
        all_sales_per_day = sales_per_day.group_by('dates').all()
        if sales_per_day:
            sales_data_today =[{"date":str(dates),"sales":sales} for dates,sales in sale_today]
            sales_data_all =[{"date":str(dates),"sales":sales} for dates,sales in all_sales_per_day]
            return {"sales_today":sales_data_today if sales_data_today else 0,"all_sale_data":sales_data_all}
        raise HTTPException(status_code=404,detail='Sales per day no found')
    except Exception as error:
        raise HTTPException(status_code=500,detail={"Error fetching sales per day":error})



def get_sale_time_data(user, db: Session):
    # Fetch sales data grouped by month
    sale_per_timedelta =  db.query(
            func.date( Sale.created_at).label('dates'),
            func.sum(Sale.quantity * Product.selling_price).label('total_sales')
        ).join(Product, Sale.pid == Product.id).filter(Sale.company_id == user.company_id).group_by(func.date(Sale.created_at)).all()
  
    formatted_sale_per_timedelta = [{"date":dates,"sales":sale} for dates, sale in sale_per_timedelta] if sale_per_timedelta else 0

    today = date.today()
    current_month = today.month
    current_year = today.year

    sales_today = next((item['sales'] for item in formatted_sale_per_timedelta if item['date'] == today), 0)
    sales_this_month = sum(item['sales'] for item in formatted_sale_per_timedelta 
                        if item['date'].month == current_month and item['date'].year == current_year
                    )
    sales_per_month = {}
    for item in formatted_sale_per_timedelta:
        month = item['date'].strftime('%m')
        if month not in sales_per_month:
            sales_per_month[month] = 0
        sales_per_month[month] += item['sales']

    # Format the sales per month as a list of dicts
    formatted_sales_per_month = [{"month": month, "sales": sales} for month, sales in sales_per_month.items()]
    return {"sales_per_day":formatted_sale_per_timedelta,"sales_today":sales_today,"sales_this_month":sales_this_month,"sales_per_month": formatted_sales_per_month}



def get_sale_counts(user,db:Session):

    sale_per_timedelta = db.query(
        func.date(Sale.created_at).label('dates'),
        func.count(Sale.id).label('total_sales_count')  # Count the number of sales (transactions) per day
    ).join(Product, Sale.pid == Product.id).filter(Sale.company_id == user.company_id).group_by(func.date(Sale.created_at)).all()

    # Format sales data into a list of dictionaries
    formatted_sale_per_timedelta = [{"date": dates, "sales_count": sales_count} for dates, sales_count in sale_per_timedelta] if sale_per_timedelta else 0

    # Get today's date
    today = date.today()

    # Get current month and year
    current_month = today.month
    current_year = today.year

    # Number of sales today (count of transactions)
    sales_today_count = next((item['sales_count'] for item in formatted_sale_per_timedelta if item['date'] == today), 0)

    # Number of sales this month (count of transactions)
    sales_this_month_count = sum(
        item['sales_count'] for item in formatted_sale_per_timedelta 
        if item['date'].month == current_month and item['date'].year == current_year
    )
    return {"sale_count_t":sales_today_count,"stm":sales_this_month_count}
    


def sales_per_product(user:get_current_user,db:Session):
    try:
        sales_per_product = db.query((Product.name).label("product"),
                            func.sum(Product.selling_price * Sale.quantity).label("sales")).join(Sale).join(Company).filter(user.company_id==Company.id)\
                         .group_by(Product.name).order_by(func.sum(Product.selling_price * Sale.quantity).desc()).all()
                      
        formatted_sales_per_prod = [{"prod_name":product,"sale":sale} for product,sale in sales_per_product] if sales_per_product else 0
        most_sold_product = formatted_sales_per_prod[0]
        top_5_products = formatted_sales_per_prod[:5]
        return {
            "sales_per_product":formatted_sales_per_prod,
            "most_sold_product":most_sold_product,
            "top_five_products":top_5_products
        }
    except Exception as error:
        raise HTTPException(status_code=500,detail=f'{error}')



def profit_per_day(user:get_current_user,db:Session):
    try:
        profit_day = db.query(func.date(Sale.created_at).label("dates"),
                            func.sum(Sale.quantity*(Product.selling_price -Product.buying_price)).label("profit")).join(Product).filter(user.company_id==Company.id).group_by('dates').all()
        if profit_day:
            profit_data =[{"date":dates,"profit":profit} for dates,profit in profit_day]
            return profit_data
        raise HTTPException(status_code=404,detail='Profit per day data not found')
    except Exception as error:
        raise HTTPException(status_code=500,detail=f'{error}')


def profit_per_product(user: get_current_user, db: Session):
    profit_product = db.query(
        Product.name.label("product"),
        func.sum(Sale.quantity * (Product.selling_price - Product.buying_price)).label("profit")
    ).join(Sale).join(Company).filter(Company.id == user.company_id).group_by(Product.name).order_by(
        func.sum(Sale.quantity * (Product.selling_price - Product.buying_price)).desc())
    if profit_product:
        profit_p = [{"product": product, "profit": profit} for product, profit in profit_product.all()]
        profit_five = [{"product": product, "profit": profit} for product, profit in profit_product.limit(5)]
        return {"profit_all_prods": profit_p, "profit_five_prods": profit_five}
    
    return None


def get_product_metrics(user,db:Session):
    try:
        product_by_price = db.query((Product.name).label('name'), (Product.selling_price).label('price')).filter(Product.company_id==user.company_id)\
               .group_by(Product.name,Product.selling_price).order_by(Product.selling_price).all()
        formatted_product_by_price = [{"name":name,"price":price} for name,price in product_by_price]
        if formatted_product_by_price:
            total_products = len(formatted_product_by_price)
            lowest_price_product = min(formatted_product_by_price, key=lambda x: x['price'])
            highest_price_product = max(formatted_product_by_price, key=lambda x: x['price'])
            total_price = sum(product['price'] for product in formatted_product_by_price)
            average_price = total_price / total_products
            
            return {"product_count":total_products,"lowest_price_product":lowest_price_product,"highest_price_product":highest_price_product,"average_price":average_price}
        else:
            lowest_price_product = None
            highest_price_product = None
            
    except Exception as e:
        raise HTTPException(status_code=500,detail={'Error getting prods by price':e})


def get_sales_today(user: get_current_user, db: Session):
    sales_today = db.query(
        func.sum(Sale.quantity * Product.selling_price).label('total_sales')
    ).select_from(Sale) \
    .join(Product, Sale.pid == Product.id) \
    .join(Company, Product.company_id == Company.id) \
    .filter(func.date(Sale.created_at) == date.today()) \
    .filter(Company.id == user.company_id) \
    .scalar()  
    return sales_today if sales_today is not None else 0


def get_depleting_products(user:get_current_user,db:Session):
    products = db.query(Stock).filter(Stock.stock_count < 20).filter(Stock.company_id==user.company_id).all()
    # data = [lowstock for lowstock in products]
    print(f"Test {products}")
    return len(products)


def get_products_by_company(user:get_current_user,db:Session):
    products = db.query(Product).join(Company,Company.id==Product.company_id).filter(Company.id==user.company_id).all()
    company_pids = {p.id for p in products}
    return company_pids


def get_all_stock(user,db:Session):
    stock_data = db.query(Stock).filter(Stock.company_id==user.company_id).all()
    stock_list =[]
    for stock in stock_data:
        stock_list.append({
            "stock_id":stock.id,
            "company_id":stock.company_id,
            "product_id":stock.product_id,
            "product_name":stock.product.name,
            "stock_count":stock.stock_count
        })
    stock_track_data = db.query(StockTracker).filter(StockTracker.company_id==user.company_id).all()
    stock_track_list =[]
    for stock_track in stock_track_data:
        formatted_created_at = stock_track.created_at.strftime("%H:%M: -> %d- %B -%Y")
        stock_track_list.append({
            "stock_tid":stock_track.id,
            "company_id":stock_track.company_id,
            "product_id":stock_track.product_id,
            "stock_added":stock_track.stock_added,
            "created_at":formatted_created_at
        })
    return{"stock_tracker_data":stock_track_list,"stock_data":stock_list}
    

def get_stock_metrics(user,db:Session):
    stock_metrics = db.query(Product.name,Stock.stock_count).join(Stock,Stock.product_id==Product.id).filter(Product.company_id==user.company_id).all()
    formatted_stock_metrics = [{"name":name,"stock":stock} for name,stock in stock_metrics]
    lowest_stock_product = min(formatted_stock_metrics,key=lambda x: x['stock'])
    highest_stock_product = max(formatted_stock_metrics,key=lambda x:x['stock'])
    return {"lowest_stock_product":lowest_stock_product,"highest_stock_product":highest_stock_product}

def get_stock_worth(user,db:Session):
    stock_worth = db.query(func.sum(Product.selling_price * Stock.stock_count)).join(Stock,Stock.product_id==Product.id)\
                .filter(Product.company_id==user.company_id).scalar()
    return stock_worth


def get_first_five_stock(user,db:Session):
    first_five = db.query(Product.name,Stock.stock_count).join(Product,Product.id==Stock.product_id).filter(Product.company_id==user.company_id).order_by(Stock.stock_count.desc()).limit(5)
    if first_five:
        result = [{"product_name": name, "stock_count": stock_count} for name, stock_count in first_five.all()]
        return result
    return None


def get_stock_by_month(user,db:Session):
    stock_by_month = db.query(func.date_trunc('month', Stock.created_at).label('month'),
        func.sum(Stock.stock_count).label('total_stock')
        ).filter(Stock.company_id==user.company_id).group_by('month').order_by('month').all()
    print(stock_by_month)
    if stock_by_month:
        formatted_stock_by_month = [{"month": month.strftime('%m'), "total_stock": total_stock} for month, total_stock in stock_by_month]
        return formatted_stock_by_month
    return None



def get_profit_by_month(user,db:Session):
    profit_by_month = db.query( func.date_trunc('month', Sale.created_at).label('month'), 
                        func.sum(Sale.quantity * (Product.selling_price-Product.buying_price).label('total_profit'))
                    ).join(Product, Sale.pid == Product.id).filter(Sale.company_id == user.company_id).group_by(func.date_trunc('month', Sale.created_at), Product.id).all()  

    if profit_by_month:
        formattted_profit_by_month = [{"month": month.strftime('%m'),"total_profit":total_profit} for month,total_profit in profit_by_month]
        return formattted_profit_by_month
    return None
                        
    
def first_five_sales_product(user,db:Session):
    five_sales_product = db.query(Product.name,(Sale.quantity * (Product.selling_price)).label('sales')).join(
        Sale,Sale.pid==Product.id).filter(Product.company_id==user.company_id).order_by(Sale.quantity * Product.selling_price).limit(5).all()
    if five_sales_product:
        formatted_five_sales_product =[{"product_name":name,"stock_count":stock_count} for name,stock_count in five_sales_product]
        return formatted_five_sales_product
    return None


def get_stock_per_product(user,db:Session):
    stock_per_product = db.query(Product.name,Stock.stock_count).join(Stock,Stock.product_id==Product.id
            ).filter(Product.company_id==user.company_id).all()
    if stock_per_product:
        formatted_stock_per_product = [{"product_name":name,"stock_count":stock_count} for name,stock_count in stock_per_product]
        depleting = [item for item in formatted_stock_per_product if item['stock_count']<20]
        return {"stock_per_product":formatted_stock_per_product,"depleting_products":len(depleting)}
    
    return None


def get_test_stock(user,db:Session):
    test_stock = db.query(Product.name,Stock.stock_count).join(Product,Product.id==Stock.product_id).filter(Product.company_id==user.company_id).order_by(Stock.stock_count.desc())
    first_five = test_stock.limit(5).all()
    all_stock = test_stock.all()
    if test_stock:
        result_five = [{"product_name":name,"stock_count":stock_count} for name ,stock_count in first_five]
        rest_stock = [{"product_name":name,"stock_count":stock_count} for name,stock_count in all_stock]
        return {
            "five":result_five,
            "all":rest_stock,
        }
    return None


def get_profit_time_data(user, db: Session):
    # Calculate the markup for profit
    markup = Product.selling_price - Product.buying_price

    # Fetch all profit data grouped by date (this already sums profits)
    all_profit = db.query(func.date(Sale.created_at).label('dates'),func.sum(Sale.quantity * markup).label("profit")
    ).join(Product, Product.id == Sale.pid) \
    .filter(Sale.company_id == user.company_id).group_by(func.date(Sale.created_at)).all()

    # Format the profit data for each date
    formatted_profit = [{"date": dates, "profit": profit} for dates, profit in all_profit] if all_profit else []

    today_date = date.today()
    today_profit = next((item['profit'] for item in formatted_profit if item['date'] == today_date), 0)  

    current_month = date.today().month
    current_year = date.today().year
    monthly_profit = sum(
        item['profit'] for item in formatted_profit if item['date'].year == current_year and item['date'].month == current_month )

    return {"formatted":formatted_profit,"today":today_profit,"month":monthly_profit}  
  

