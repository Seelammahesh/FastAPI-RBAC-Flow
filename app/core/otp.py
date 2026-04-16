from passlib.context import CryptContext
import random

pwd_context= CryptContext(schemes=["bcrypt"],deprecated="auto")


def generate_otp():
    otp = random.randint(100000, 999999)
    return otp


def hash_otp(otp: str):
    return pwd_context.hash(otp)


def verify_otp(plain_otp : str, hashed_otp:str):
    return pwd_context.verify(plain_otp, hashed_otp)
