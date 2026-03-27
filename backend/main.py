from fastapi import FastAPI

app = FastAPI()

@app.post("/jobs")
async def create_job():
    return {"status": "TODO"}

@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    return {"status": "TODO"}
