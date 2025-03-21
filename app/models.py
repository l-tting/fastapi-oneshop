from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func,Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum
# from database import Base

class Company(Base):
    __tablename__ = 'companies'
    id = Column(Integer,primary_key=True,index=True)
    company_name = Column(String,nullable=False)
    phone_number = Column(Integer,nullable=False)
    email = Column(String,unique=True,nullable=False)
    user = relationship('User', back_populates='company')
    subscription = relationship('Subscription',back_populates='company')
    product = relationship('Product',back_populates='company')
    sales = relationship('Sale',back_populates='company')
    stock = relationship("Stock",back_populates='company')
    stock_tracker = relationship("StockTracker",back_populates='company')


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer,ForeignKey('companies.id'),nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String,nullable=False)
    role = Column(String,nullable=False,default='user')
    company = relationship("Company",back_populates='user')



class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    company_id =Column(Integer,ForeignKey('companies.id'),nullable=False)
    name = Column(String, nullable=False)
    buying_price = Column(Integer, nullable=False)
    selling_price = Column(Integer, nullable=False)
    sales = relationship("Sale", back_populates='product')
    company = relationship("Company",back_populates='product')
    stock = relationship("Stock",back_populates='product')
    stock_tracker = relationship("StockTracker",back_populates='product')
    
class Stock(Base):
    __tablename__ = 'stock'
    id = Column(Integer,primary_key=True)
    company_id = Column(Integer,ForeignKey('companies.id'),nullable=False)
    product_id = Column(Integer,ForeignKey('products.id'),nullable=False)
    stock_count = Column(Integer,nullable=False,default=0)
    product = relationship("Product",back_populates='stock')
    company = relationship("Company",back_populates='stock')
    
class StockTracker(Base):
    __tablename__ = 'stock_tracker'
    id = Column(Integer,primary_key=True)
    company_id = Column(Integer,ForeignKey('companies.id'),nullable=False)
    product_id = Column(Integer,ForeignKey('products.id'),nullable=False)
    stock_added = Column(Integer,nullable=False)
    created_at = Column(DateTime,default=func.now())
    product = relationship("Product",back_populates='stock_tracker')
    company = relationship("Company",back_populates='stock_tracker')
    

class Sale(Base):
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True)
    pid = Column(Integer, ForeignKey('products.id'), nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now())
    product = relationship("Product", back_populates='sales')
    payment = relationship('Payment',back_populates='sale')
    company = relationship("Company",back_populates='sales')


class Vendor(Base):
    __tablename__ = 'vendors'
    id = Column(Integer,primary_key=True)
    company_id = Column(Integer,ForeignKey('companies.id'),nullable=False)
    vendor_name = Column(String,nullable=False,unique=True)
    phone_number = Column(String,nullable=False,unique=True)
    email = Column(String,nullable = False, unique=True)
    address = Column(String,nullable=False)



    
class Payment(Base):
    __tablename__ = 'payments'
    payment_id = Column(String,primary_key=True)
    sale_id = Column(Integer,ForeignKey('sales.id'),nullable=False)
    amount = Column(Integer,nullable=False)
    mode = Column(String,nullable=False)
    transaction_code = Column(String,nullable=False)
    created_at = Column(DateTime,server_default=func.now())
    sale = relationship('Sale',back_populates='payment')


# The enum module is used to define an enumeration of possible values for a column
class MPESAStatus(str, enum.Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    TIMEOUT = 'timeout'


class STK_Push(Base):
    __tablename__= 'stk_push'
    stk_id = Column(Integer,primary_key=True)
    merchant_request_id = Column(String,nullable=False)
    checkout_request_id = Column(String,nullable=False)
    amount = Column(Integer,nullable=False)
    phone = Column(String,nullable=False)
    status = Column(Enum(MPESAStatus, name='mpesa_status_enum'),
        default=MPESAStatus.PENDING,
        nullable=False
    )
    result_code = Column(String,nullable=True)
    result_desc = Column(String,nullable=True)
    created_at = Column(DateTime,server_default=func.now())


class Tier(Base):
    __tablename__ = 'tiers'
    id = Column(Integer,primary_key=True)
    name = Column(String,nullable=False)
    description=Column(String,nullable=False)
    amount = Column(Integer,nullable=False)
    subscription = relationship('Subscription',back_populates='tier')


class SubscriptionStatus(str, enum.Enum):
    INACTIVE ='inactive',
    ACTIVE = 'active'
    EXPIRED = 'expired'
    CANCELLED = 'cancelled'

class Subscription(Base):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    tier_id = Column(Integer, ForeignKey('tiers.id'))
    subscription_status = Column(Enum(SubscriptionStatus),name='subscription_status_enum', default=SubscriptionStatus.INACTIVE,nullable=False)
    # transaction_code = Column(String, unique=True)
    created_at = Column(DateTime,server_default=func.now())
    company = relationship("Company",back_populates='subscription')
    tier = relationship("Tier",back_populates='subscription')
#status for subscription
    
class Test(Base):
    pass