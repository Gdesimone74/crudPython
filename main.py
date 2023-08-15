from fastapi.templating import Jinja2Templates
from task import Task

from typing import List

from fastapi import FastAPI, File ,HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse
import redis, json, io
import pandas as pd

listTask=[]

app = FastAPI()

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
templates = Jinja2Templates(directory="templates")

@app.get("/testBD")
async def test_redis_connection():
    result = ""
    response = r.ping()
    if response:
            result="Succesful conection"
    else:
            result="Error conection"
    return result

@app.get("/")
async def read_root(request: Request):
    tasks = r.lrange("tasks", 0, -1)
    tasks_list = []

    for task_json in tasks:
        task_data = json.loads(task_json)
        tasks_list.append(task_data)

    return templates.TemplateResponse("index.html", {"request": request, "tasks": tasks_list})


@app.get("/list")
def list_task():
    tasks = r.lrange("tasks", 0, -1)
    return tasks

@app.get("/list")
def list_task():
    return listTask

@app.post("/create")
def create_task(task: Task):
    task_dict = {"title": task.title, "description": task.description}
    r.rpush("tasks", json.dumps(task_dict))
    return r.lrange("tasks", 0, -1)

@app.delete("/delete/{title}")
def delete_task(title: str):
    r.lrem("tasks", 0, 1)
    print(title)
    tasks = r.lrange("tasks", 0, -1)
    print(tasks)
    index_to_delete = None
    for index, task_json in enumerate(tasks):
        task_dict = json.loads(task_json)
        if task_dict.get("title") == title:
            print('lo encontro')
            index_to_delete = index
            break

    if index_to_delete is not None:
        print(index_to_delete)
        r.lrem("tasks", index_to_delete, 1)  # Eliminar el elemento en el índice
        return {"message": "Task deleted"}
    else:
        raise HTTPException(status_code=404, detail="Task not found")


@app.post("/upload")
async def upload_csv(csv_file: UploadFile = File(...)):
    if csv_file.filename.endswith(".csv"):
      
        csv_content = await csv_file.read()
        df = pd.read_csv(io.BytesIO(csv_content))
        
       
        for index, row in df.iterrows():
            title = row["title"]
            description = row["description"]
            task_dict = {"title": title, "description": description}
            r.rpush("tasks", json.dumps(task_dict))
        
       
        return RedirectResponse("/", status_code=302)
    else:
        return {"message": "Invalid file format"}
