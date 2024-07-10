from datetime import timedelta
from fastapi import FastAPI,Depends, HTTPException,status
from sqlalchemy import or_
from models import User,engine

from sqlalchemy.orm import Session, sessionmaker
from typing import List, Optional
from schemas import CreateUser
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


from jwt_utils import create_access_token,decode_token, get_password_hash,verify_password

oauth2_scheme=OAuth2PasswordBearer(tokenUrl='login')


SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

app = FastAPI()

def get_db():
    db=SessionLocal()
    try:
        yield db
        # yield is used 
    finally:
        db.close()


@app.post('/users/',response_model=CreateUser)
async def register(user:CreateUser,db:Session=Depends(get_db)):
    if db.query(User).filter(or_(User.email == user.email,
                             User.username == user.username,
                             User.phone_number == user.phone_number)).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Email, username, or phone number already registered')

    hashed_password=get_password_hash(user.password)
    user= User(**user.dict())
    user.password=hashed_password
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post('/login/')
async def login(form_data: OAuth2PasswordRequestForm = Depends(),db:Session=Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invalid Credentials')
    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invalid Credentials')
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}



@app.get('/users/',response_model=List[CreateUser])
async def get_users(q: Optional[str] = None,db:Session=Depends(get_db),limit:int=10,skip:int=0,sort:str='id',order:str='asc',token:str=Depends(oauth2_scheme)):
    users=db.query(User).all()
    if q:
        users=db.query(User).filter(User.username.contains(q)).all()
    return users

@app.get('/users/{user_id}',response_model=CreateUser)
async def get_user(user_id:int,db:Session=Depends(get_db)):
    user=db.query(User).filter(User.id==user_id).first()
    return user


@app.put('/users/{user_id}', response_model=CreateUser)
async def update_user(user_id: int, user: CreateUser, db: Session = Depends(get_db)):
    # Check if the user with user_id exists
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    for field, value in user.dict(exclude_unset=True).items():
        setattr(db_user, field, value)
    # exlude unset fields to avoid setting unset fields to None,
    # this will allow us to update only the fields that are set in the request, 
    # and leave the others as they are.
    
    db.commit()

    # Refresh the db_user object to reflect the updated state
    db.refresh(db_user)

    return db_user
@app.delete('/users/{user_id}')
async def delete_user(user_id:int,db:Session=Depends(get_db)):
    user=db.query(User).filter(User.id==user_id).delete()
    db.commit()
    return {'message':'User deleted successfully'}

