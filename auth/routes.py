from fastapi import APIRouter, HTTPException, status, Request, Depends, Query
from typing import List, Optional
from beanie import PydanticObjectId, Document
from pydantic import BaseModel
import datetime
import secrets
import string

from mongodb.models.user import User, Token, Project, Log
import utils.pydantic_encoder as pydantic_encoder

router = APIRouter()


async def verify_token(token: str = Query(...)):
    token_document = await Token.find_one(Token.value == token)
    if token_document is None:
        raise HTTPException(status_code=403, detail="Invalid or missing token")
    
async def token_to_user_id(token: str):
    user = (await Token.find_one(Token.value == token)).user
    return user



@router.post("/sign-up", status_code=status.HTTP_201_CREATED, response_model=User)
async def sign_up(user: User):
    existing_email = await User.find(User.email == user.email).to_list()
    if (len(existing_email) > 0):
        raise HTTPException(400, detail="A user with that email already exists.")
    existing_username = await User.find(User.username == user.username).to_list()
    if (len(existing_email) > 0):
        raise HTTPException(400, detail="That username is taken.")
    await user.insert()
    return user


class ReturnUser(BaseModel):
    user: User
    token: Token
    projects: List[Project]
    logs: List[Log]


@router.get("/sign-in", status_code=status.HTTP_200_OK, response_model=ReturnUser)
async def sign_in(username: str, hash: str):
    user: User = await User.find_one(User.username == username)
    if user == None or user.hash != hash:
        raise HTTPException(403, detail="Incorrect username or password.")
    
    my_length = 14
    crypt = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(my_length))
    new_token = Token(user=user.id, time_created=str(datetime.datetime.now()), value=crypt)
    await new_token.insert()

    projects = await Project.find(Project.user == user.id).to_list()
    logs = await Log.find(Log.user == user.id).to_list()
    return ReturnUser(user=user, token=new_token, projects=projects, logs=logs)


class UpdateUser(BaseModel):
    projects: List[Project]
    logs: List[Log]
@router.get("/get-updates", status_code=status.HTTP_200_OK, response_model=UpdateUser)
async def get_updates(token: str):
    try:
        user_id = (await token_to_user_id(token))
        user = await User.find(User.id == user_id).to_list()
        if len(user) == 0:
            raise HTTPException(status_code=status.HTTP_200_OK, detail="User not found for that token.")
        user = user[0]
        projects = await Project.find(Project.user == user.id).to_list()
        logs = await Log.find(Log.user == user.id).to_list()
        return UpdateUser(projects=projects, logs=logs)
    except Exception as e:
        # print(e)
        print("An error occurred.")