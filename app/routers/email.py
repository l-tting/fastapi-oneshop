from fastapi import APIRouter,HTTPException,BackgroundTasks,Depends
from pydantic import BaseModel
from app.schemas import EmailSchema
from fastapi_mail import FastMail,MessageSchema,ConnectionConfig
from app.auth import get_current_user


router = APIRouter()

class Config:
    MAIL_USERNAME = "brianletting01@gmail.com"
    MAIL_PASSWORD = "azgr nfjo pmah mfvp"
    MAIL_FROM = "brianletting01@gmail.com"
    MAIL_PORT = 587
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_TLS = True
    MAIL_SSL = False
    USE_CREDENTIALS = True
    VALIDATE_CERTS = True

conf = ConnectionConfig(
    MAIL_USERNAME=Config.MAIL_USERNAME,
    MAIL_PASSWORD=Config.MAIL_PASSWORD,
    MAIL_FROM=Config.MAIL_FROM,
    MAIL_PORT=Config.MAIL_PORT,
    MAIL_SERVER=Config.MAIL_SERVER,
     MAIL_STARTTLS = True,  
    MAIL_SSL_TLS = False , 
    USE_CREDENTIALS=Config.USE_CREDENTIALS,
    VALIDATE_CERTS=Config.VALIDATE_CERTS
)

fm = FastMail(conf)

DEFAULT_RECIPIENT= 'brianletting01@gmail.com'

@router.post('/')
async def send_email(background_tasks:BackgroundTasks,email:EmailSchema,user=Depends(get_current_user)):

    html_content_customer = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="background-color: #f4f4f9; padding: 20px; border-radius: 8px;">
                <h1 style="color: #4CAF50;">Customer Support Request</h1>
                <p>Dear OneShop team,</p>

                <p>I hope you're doing well. I’m reaching out with the following request:</p>

                <h2 style="color: #333;">Customer Information:</h2>
                <ul>
                    <li><strong>Name:</strong> {email.sender_name}</li>
                    <li><strong>Email:</strong> {email.sender_email}</li>
                    <li><strong>Phone Number:</strong> {email.sender_phone}</li>
                </ul>

                <h3 style="color: #333;"> Inquiry/Request Details:</h3>
                <p style="color: #555;">{email.body}</p>


                <p style="margin-top: 20px; color: #555;">I would appreciate your prompt attention to this matter, and please let me know if you require any further information.</p>

                <p style="color: #555;">Thank you for your time and assistance.</p>

                <footer style="font-size: 12px; color: #999; text-align: center; margin-top: 30px;">
                    <p>Best regards,</p>
                    <p><strong>{email.sender_name}</strong></p>
                    <p>{email.sender_phone}</p>
                    <p>{email.sender_email}</p>
                </footer>
            </div>
        </body>
    </html>
    """

    message = MessageSchema(
        subject=f"Customer Support Request from {email.sender_name}",
        recipients=[DEFAULT_RECIPIENT],
        body=html_content_customer,
        subtype='html'
    )

    try:

        background_tasks.add_task(fm.send_message, message)
    except Exception as e:
        raise HTTPException(status_code=500,detail=f'Error sending mail {e}')
    
    return {"message": "Email sent successfully in the background!"}

