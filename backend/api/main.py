from fastapi import FastAPI

app = FastAPI()

@app.get("/answer")
def get_answer():
    return {"Hello": "World"}

@app.post("/preferences/init")
def init_preferences():
    return {"Hello": "World"}

@app.get("/preferences/{username}")
def get_preferences():
    return {"Hello": "World"}

@app.put("/preferences/{username}")
def update_preferences():
    return {"Hello": "World"}