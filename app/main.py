from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import products,sales,stock,users,vendors,daraja,company,dashboard,tier,email
from app import models,database
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
# from limiter import limiter 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(database.engine)

# app.state.limiter = limiter

# Add exception handler for rate limit exceeded
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Include the routers for different modules
app.include_router(tier.router, prefix='/tier' ,tags=['tier'])
app.include_router(company.router, prefix='/company' ,tags=['company'])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(dashboard.router,prefix='/dashboard',tags=['dashboard'])
app.include_router(sales.router, prefix="/sales", tags=["sales"])
app.include_router(vendors.router, prefix="/vendors", tags=["vendors"])
app.include_router(stock.router, prefix="/stock", tags=["stocks"])
app.include_router(daraja.router, prefix='/stk_push' ,tags=['stk_push'])
app.include_router(email.router, prefix='/send_mail' ,tags=['send_email'])

@app.get('/')
def index():
    return {"message": "Welcome to MyDuka FASTAPI"}


