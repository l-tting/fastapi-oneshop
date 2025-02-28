from base64 import b64encode
from fastapi import HTTPException
from sqlalchemy.orm import Session
import requests
from datetime import datetime
import httpx
from app import schemas,models

consumer_key = '7tWrv1GzADCWG7gdFeXlGGfWKJdu9iplFEXA3AL2L0c6KDoT'
consumer_secret = 'VIzhHEdmCN8519EsnkKH4DpZ0nOoMBcFNDCXlpQktZnKn4YktpL8fB0A1YenRanE'
pass_key = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
saf_url = "https://sandbox.safaricom.co.ke/"
short_code = '174379'
callback_url = 'https://oneshop.co.ke/stk_callback'



def get_access_token():
   
    try:
        if not consumer_key or not consumer_secret:
            raise ValueError("CONSUMER_KEY or CONSUMER_SECRET not set")

        credentials = f"{consumer_key}:{consumer_secret}"
        encoded_credentials = b64encode(credentials.encode()).decode()
        print(f"Encoded Credentials: {encoded_credentials}") 

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json"
        }

        url = f"{saf_url}oauth/v1/generate?grant_type=client_credentials"
        
        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code != 200:
            print(f"Response body: {response.text}")  
            raise Exception(f"Auth failed: {response.status_code} - {response.text}")

        json_response = response.json()
        
        access_token = json_response.get("access_token")
        if not access_token:
            raise Exception(f"No access token found in the response: {json_response}")
        return access_token

    except Exception as e:
        print(f"Error getting access token: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get access token: {str(e)}")


async def stk_push_sender(mobile:str, amount:float, access_token:str):
    try:

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        stk_password = b64encode((short_code + pass_key + timestamp).encode('utf-8')).decode()

        url = f"{saf_url}mpesa/stkpush/v1/processrequest"
        headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

        request = {
            "BusinessShortCode": str(short_code),
            "Password": stk_password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": str(mobile),
            "PartyB": short_code,
            "PhoneNumber": str(mobile),
            "CallBackURL": callback_url,
            "AccountReference": "myduka1",
            "TransactionDesc": "Testing STK Push"
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=request, headers=headers)
        
        response.raise_for_status()  
       
        print("Raw response from MPESA:", response.text)
        return response.json()

    except httpx.RequestError as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Error occurred: {str(e)}"}
    

    

def check_transaction_status(merchant_request_id: str, checkout_request_id: str, db):
    transaction = db.query(models.STK_Push).filter(
        models.STK_Push.merchant_request_id == merchant_request_id,
        models.STK_Push.checkout_request_id == checkout_request_id ).first()
    
    if not transaction:
         raise HTTPException(status_code=404, detail="Transaction not found")
    
    return transaction
    
    

async def process_stk_push_callback(callback_data: schemas.MpesaCallback, db: Session):
    try:
        transaction = db.query(models.STK_Push).filter(
            models.STK_Push.merchant_request_id == callback_data.merchant_request_id,
            models.STK_Push.checkout_request_id == callback_data.checkout_request_id
        ).first()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")

        if callback_data.result_code != "0":
            transaction.status = models.MPESAStatus.FAILED
            transaction.result_code = callback_data.result_code
            transaction.result_desc = callback_data.result_desc
            db.commit()
            return {
                "status": "failure",
                "message": "Transaction failed",
                "result_code": callback_data.result_code,
                "result_desc": callback_data.result_desc
            }

        transaction.status = models.MPESAStatus.COMPLETED
        transaction.result_code = callback_data.result_code
        transaction.result_desc = callback_data.result_desc
        db.commit()
        return {
            "status": "success",
            "message": "Transaction completed"
        }
    except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
    
