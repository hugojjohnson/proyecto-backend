from fastapi import APIRouter, HTTPException, status
from typing import List
from beanie import PydanticObjectId
from pydantic import BaseModel
import os
import http.client
import json


from mongodb.models.user import User, Token, Project, Log
import utils.pydantic_encoder as pydantic_encoder
from auth.routes import token_to_user_id

router = APIRouter()


# Create project
@router.post("/create-project", status_code=status.HTTP_201_CREATED, response_model=Project)
async def create_project(token: str, project: Project):
    user_id = (await token_to_user_id(token))
    project.user = user_id
    await project.insert()
    return project


# Read projects
@router.get("/get-projects", status_code=status.HTTP_200_OK, response_model=List[Project])
async def get_projects(token: str):
    user_id = (await token_to_user_id(token))
    projects = await Project.find(Project.user == user_id).to_list()
    return projects

# Update project
@router.put("/edit-project", status_code=status.HTTP_200_OK, response_model=Project)
async def edit_project(token: str, project: Project):
    user_id = (await token_to_user_id(token))
    if project.user != user_id:
        raise HTTPException(400, detail="project.user does not match token.")
    project_document = (await Project.find(Project.id == (project.id)).to_list())[0]

    if project_document == None:
        raise HTTPException(500, detail="Project could not be found.")
    _ = await project_document.update({"$set": project})
    updated_project = await project.get(project.id)
    return updated_project

# Delete project
@router.get("/delete-project", status_code=status.HTTP_200_OK, response_model=str)
async def delete_project(id: str):
    id = PydanticObjectId(id)
    proj = await Project.get(id)
    if not proj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project with id {id} not found")
    await proj.delete()
    logs = await Log.find(Log.project == proj.id).to_list()
    for log in logs:
        await log.delete()
    return "Success"



# Create log
@router.post("/create-log", status_code=status.HTTP_201_CREATED, response_model=Log)
async def create_log(token: str, log: Log):
    print(log.date)
    user_id = (await token_to_user_id(token))
    log.user = user_id
    await log.insert()
    return log

# # Read logs
# @router.get("/get-logs", status_code=status.HTTP_200_OK, response_model=List[Project])
# async def get_projects(token: str):
#     user_id = (await token_to_user_id(token))
#     projects = await Project.find(Project.user == user_id).to_list()
#     return projects


# Update log
@router.get("/edit-log", status_code=status.HTTP_200_OK, response_model=Log)
async def edit_log(token: str, id: str, goal: str, notes: str):
    user_id = (await token_to_user_id(token))
    log_document = (await Log.find((Log.id == PydanticObjectId(id))).to_list())
    if (len(log_document) == 0):
        raise HTTPException(500, detail="Log could not be found.")
    log_document = log_document[0]
    if log_document.user != user_id:
        raise HTTPException(400, detail="log.user does not match token.")

    log_document.goal = goal
    log_document.notes = notes
    _ = await log_document.update({"$set": log_document})
    updated_log = await Log.get(log_document.id)
    return updated_log

# Delete log
@router.get("/delete-log", status_code=status.HTTP_200_OK, response_model=str)
async def delete_log(id: str):
    id = PydanticObjectId(id)
    log = await Log.get(id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Log with id {id} not found")
    await log.delete()
    return "Success"


@router.get("/get-quote", status_code=status.HTTP_200_OK, response_model=str)
async def get_quote(token: str):
    user_id = (await token_to_user_id(token))
    print(os.environ["NINJA_KEY"])
    category = 'happiness'

    # make request
    api_key = os.environ["NINJA_KEY"]

    conn = http.client.HTTPSConnection('api.api-ninjas.com')
    headers = {'X-Api-Key': api_key}
    conn.request('GET', f'/v1/quotes?category={category}', headers=headers)

    response = conn.getresponse()
    data = response.read().decode()

    conn.close()

    if response.status == 200:
        print(data)
        return data
    else:
        print("Error:", response.status, data)
        return "Error:", response.status, data