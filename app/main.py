from fastapi import FastAPI
from app.db.base_class import Base
from app.db.session import engine

from app.api.routes import user
from app.api.routes import admin
from app.models import  role, permissions, tokens, otp



app=FastAPI()

@app.get("/")
def read_root():
    return {"Message": " Welcome User"}

app.include_router(user.router),
app.include_router(admin.router)