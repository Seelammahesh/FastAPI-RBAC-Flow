from pydantic import BaseModel

class UserCreate(BaseModel):
    username : str
    password : str
    role : str  #role name input

class UserLogin(BaseModel):
    username : str
    password : str

class UserOut(BaseModel):
    id : int
    username : str
    role : str


    class Config:
        from_attribute = True