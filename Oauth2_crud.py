'''#crud program using the oauth2 authentication ''''''(CREATE,READ,UPDATE,DELETE)'''

from fastapi import FastAPI,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from sqlalchemy import create_engine,Column,String,Integer
from sqlalchemy.orm import declarative_base,Session,sessionmaker
from jose import jwt,JWTError
from passlib.context import CryptContext
from datetime import datetime,timezone,timedelta
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

#jwt configiration 
SECRET_KEY = "my-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = 30

#passlib password hashing algorithm setup
pwt_context = CryptContext(schemes=["bcrypt"],deprecated = "auto")

#oauth2passowrdbearer setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

#database configuration (sqlalchemy)
DATABASE_URL = "sqlite:///./student_2.db"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread":False}
)

#database basemodel setup 
Base = declarative_base()
'''#user_model'''
class user_details(Base):
    __tablename__ ="user_info"
    id = Column(Integer,primary_key=True,index=True)
    username = Column(String,index=True)
    hashed_password = Column(String)
'''student_model'''
class student_details(Base):
    __tablename__ = "student_info"
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String,index=True)
    age = Column(Integer)
    marks = Column(Integer)
    city = Column(String)

Base.metadata.create_all(engine)

#creating the session
sessionLocal = sessionmaker(autoflush=False,autocommit=False,bind=engine)

#data dependency
def get_db():
    db= sessionLocal()
    try:
        yield db
    finally:
        db.close()

#hasing the password 
def hash_password(password:str):
    return pwt_context.hash(password)

#verifying the hashed password
def verify_password(plain_password:str,hashed_password:str):
    return pwt_context.verify(plain_password,hashed_password)

#creating the token
def create_token(data:dict,expire_delta:Optional[timedelta]=None):
    to_encode = data.copy()
    expire_delta = expire_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    expire = datetime.now(timezone.utc) + expire_delta
    to_encode.update({"exp":expire})
    token = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return token

#verify the token
def get_user_data(token:str=Depends(oauth2_scheme)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid token credential",
        headers={"WWW-Authenticate":"bearer"}
    )
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credential_exception
    except JWTError:
        raise credential_exception
    return username

#pydantic model setup
'''usermodel'''
class user_model(BaseModel):
    username:str
    password:str
'''studentmodel'''
class student_model(BaseModel):
    name:str
    age:int
    marks:int
    city:str

#registraion route
@app.post("/register")
def register(user_data:user_model,db:Session=Depends(get_db)):
    exsisting_user = db.query(user_details).filter(user_details.username == user_data.username).first()
    if exsisting_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="!!! user already exits !!!"
        )
    new_user = user_details(
        username=user_data.username,
        hashed_password = hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "message":"user registerd successfully",
        "user_details":new_user.username
    }

#login route
@app.post("/login")
def login(new_data:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    db_data = db.query(user_details).filter(user_details.username == new_data.username).first()
    if not db_data or not verify_password(new_data.password,db_data.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect username or password"

        )
    access_token = create_token(data={"sub":new_data.username})
    return {
        "message":"Authentication successfull",
        "access_token":access_token,
        "token_type":"bearer"
    }

#crate new student route
@app.post("/create_student")
def create_student(new_data:student_model,user_data:str=Depends(get_user_data),db:Session=Depends(get_db)):
    exsisting_student = db.query(student_details).filter(student_details.name == new_data.name).first()
    if exsisting_student :
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="student already exists"
        )
    new_student = student_details(
        name = new_data.name,
        age = new_data.age,
        marks = new_data.marks,
        city = new_data.city
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return {
        "messge":"Student Added Successfull",
        "new_student":new_student.name,
        "user_details":user_data
    }

#read student route
@app.get("/studen_details")
def student_information(id:int,user_data:str=Depends(get_user_data),db:Session=Depends(get_db)):
    student_data = db.query(student_details).filter(student_details.id == id).first()
    if student_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="student doesnt exists"
        )
    return {
        "message":"Authentication successfull",
        "data":student_data,
        "user_details":user_data
    }

#update student data route
@app.put("/student_update")
def update_student(id:int,marks:int,user_data:str=Depends(get_user_data),db:Session=Depends(get_db)):
    student_data = db.query(student_details).filter(student_details.id == id).first()
    if student_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="student not found"
        )
    student_data.marks = marks
    db.commit()
    db.refresh(student_data)
    return {
        "message":"student updated successfull",
        "user_details":user_data,
        "updated_data":f'marks :- {marks}'
    }
#delete student route
@app.delete("/delete_student")
def delete_student(id:int,user_data:str=Depends(get_user_data),db:Session=Depends(get_db)):
    student_data=db.query(student_details).filter(student_details.id == id).first()
    if student_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found"
        )
    db.delete(student_data)
    db.commit()
    return {
        "message":"user delete successfull",
        "user_details":user_data,
        "deleted_data":student_data.name
    }









