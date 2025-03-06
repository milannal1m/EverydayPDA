from fastapi import FastAPI

app = FastAPI(root_path="/user")


@app.get("/")
def read_root():
    return {"Hello": "World"}