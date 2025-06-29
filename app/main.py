from fastapi import FastAPI

from app.api import auth, employee, account, transaction

app = FastAPI()

app.include_router(auth.router)
app.include_router(employee.router)
app.include_router(account.router)
app.include_router(transaction.router)

@app.get("/")
def root():
    return {"message": "BankBase API is running"}
