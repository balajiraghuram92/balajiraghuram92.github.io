from fastapi import FastAPI
from pydantic import BaseModel
import datetime

app = FastAPI(title="Deskbuddy Tools")

class Calc(BaseModel):
    expression: str

@app.post("/calculator")
def calculator(c: Calc):
    try:
        return {"result": eval(c.expression, {"__builtins__": {}})}
    except Exception as e:
        return {"error" : str(e)}


@app.get("/datetime")
def get_datetime():
    return {"result": datetime.datetime.now().isoformat()}
