from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel , Field
from models import Tasks
from starlette import status
from database import db_dependecy

router = APIRouter()

class TaskRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool

    # class Config:
    #     json_schema_extra = {
    #         'examples': {
    #             'title': 'Title of the task',
    #             'description': 'Description of a task',
    #             'priority': 'test',
    #             'complete': True
    #         }
    #     }

@router.get("/", status_code=status.HTTP_200_OK)
async def get_tasks(db: db_dependecy):
     return db.query(Tasks).all()

@router.get("/tasks/{id}", status_code=status.HTTP_200_OK)
async def get_task_by_id(db: db_dependecy, id: int = Path(gt=0)):
    task = db.query(Tasks).filter(Tasks.id == id).first()
    if task is not None:
        return task
    raise HTTPException(status_code=404, detail="Task not found")

@router.post("/create-task", status_code=status.HTTP_201_CREATED)
async def create_tasks(db: db_dependecy, task_request: TaskRequest):
    add_task = Tasks(**task_request.dict())
    db.add(add_task)
    db.commit() 

@router.put("/task/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_task(db: db_dependecy, task_request: TaskRequest, id: int = Path(gt=0)):
    update_task = db.query(Tasks).filter(Tasks.id == id).first()
    if update_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    update_task.title = task_request.title
    update_task.description = task_request.description
    update_task.priority = task_request.priority
    update_task.complete = task_request.complete
    db.add(update_task)
    db.commit()

@router.delete("/task/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(db: db_dependecy, id: int = Path(gt=0)):
    delete_task = db.query(Tasks).filter(Tasks.id == id).first()
    if delete_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.query(Tasks).filter(Tasks.id == id).delete()
    db.commit()