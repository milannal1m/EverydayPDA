from fastapi import FastAPI

app = FastAPI()

@app.get("/answer")
def read_root():
    return {"Hello": "World"}

@app.post("/preferences/init")
def read_root():
    return {"Hello": "World"}

@app.get("/preferences/username")
def read_root():
    return {"Hello": "World"}

@app.update("/preferences/username")
def read_root():
    return {"Hello": "World"}