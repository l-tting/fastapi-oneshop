from pydantic import BaseModel
from typing import Optional

class Product(BaseModel):

    name:str
    buying_price:int
    selling_price:int
    

class Sale(BaseModel):
    pid: int
    quantity: int

class User(BaseModel):
    full_name:str
    email:str
    password:str


class UserLogin(BaseModel):
    email:str
    password:str

class PasswordReset(BaseModel):
    email:str
    password:str
    confirm_password:str

class Product_Update(BaseModel):
    name: Optional[str] = None
    buying_price: Optional[float] = None
    selling_price: Optional[float] = None
    stock_quantity: Optional[int] = None

class VendorCreate(BaseModel):
    name: str
    phone_number:str
    email:str
    address:str

class Stock(BaseModel):
    product_id:int
    stock_count:int
  

class STK_PushResponse(BaseModel):
    merchant_request_id:str
    checkout_request_id:str
    status:str
    response_code:str='0'
    response_desc:str='Success. Request accepted for processing'
    customer_message: str = "Please check your phone to complete the payment" 


class MpesaCallback(BaseModel):
    merchant_request_id: str
    checkout_request_id: str
    result_code: str
    result_desc: str


class STK_PushCreate(BaseModel):
    phone_number:str
    amount: float

class STKPushCheckResponse(BaseModel):
    success: bool
    message: str
    status: Optional[str] = None

class CompanyCreate(BaseModel):
    name: str
    phone_number:str
    email:str
    

class TierCreate(BaseModel):
    name:str
    description:str
    amount:float

class EmailSchema(BaseModel):
    sender_name:str
    sender_email:str
    sender_phone:str
    body:str