from fastapi import APIRouter, HTTPException, Path, Depends
from pydantic import BaseModel , Field
from models import Tasks
from starlette import status
from database import db_dependecy
from typing import Annotated
from .auth import get_current_user

router = APIRouter()
user_dependency = Annotated[dict, Depends(get_current_user)]


class TaskRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool

@router.get("/", status_code=status.HTTP_200_OK)
async def get_tasks(user: user_dependency, db: db_dependecy):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Tasks).filter(Tasks.owner_id == user.get('id')).all()

@router.get("/tasks/{id}", status_code=status.HTTP_200_OK)
async def get_task_by_id(user: user_dependency, db: db_dependecy, id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    
    task = db.query(Tasks).filter(Tasks.id == id)\
        .filter(Tasks.owner_id == user.get('id')).all()
    if task is not None:
        return task
    raise HTTPException(status_code=404, detail="Task not found")

@router.post("/create-task", status_code=status.HTTP_201_CREATED)
async def create_tasks(user: user_dependency, db: db_dependecy, task_request: TaskRequest):
    print(f"This is user_dependency: {user_dependency}")
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    add_task = Tasks(**task_request.dict(), owner_id=user.get('id'))
    db.add(add_task)
    db.commit() 

@router.put("/task/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_task(user: user_dependency, db: db_dependecy, task_request: TaskRequest, id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    update_task = db.query(Tasks).filter(Tasks.id == id)\
        .filter(Tasks.owner_id == user.get('id')).first()
    if update_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    update_task.title = task_request.title
    update_task.description = task_request.description
    update_task.priority = task_request.priority
    update_task.complete = task_request.complete
    db.add(update_task)
    db.commit()

@router.delete("/task/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(user: user_dependency, db: db_dependecy, id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    delete_task = db.query(Tasks).filter(Tasks.id == id)\
        .filter(Tasks.owner_id == user.get('id')).first()
    if delete_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.query(Tasks).filter(Tasks.id == id).delete()
    db.commit()