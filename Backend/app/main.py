from fastapi import FastAPI

app = FastAPI(title="Student API")

@app.get("/")
def health_check():
    return {"status": "API is running"}
