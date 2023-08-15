from typing import Union

from fastapi import FastAPI, HTTPException

from task import Task

from typing import List

import redis, json

listTask=[]

app = FastAPI()

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


@app.get("/testBD")
async def test_redis_connection():
    result = ""
    response = r.ping()
    if response:
            result="Succesful conection"
    else:
            result="Error conection"
    return result

@app.get("/list")
def list_task():
    tasks = r.lrange("tasks", 0, -1)
    return tasks

@app.get("/list")
def list_task():
    return listTask

@app.post("/create")
def create_task(task: Task):
    listTask.append(task)
    r.rpush("tasks", task.model_dump_json())
    return listTask

@app.delete("/delete/{title}")
def delete_task(title: str):
    # Eliminar la tarea de Redis
    tasks_before = r.lrange("tasks", 0, -1)
    r.lrem("tasks", 0, title)
    tasks_after = r.lrange("tasks", 0, -1)
    
    if tasks_before == tasks_after:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    return "Task deleted"

@app.get("/description/{title}")
def get_description(title: str):
    # Obtener la tarea por título desde el índice hash
    print(title)
    task_json = r.hget("tasks_by_title", title)

    if task_json is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    task_data = json.loads(task_json)
    task_instance = Task(**task_data) 
    
    if not task_json:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    return task_instance.description

