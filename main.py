from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import os

API_KEY = "67url67jxishsj"  # CHANGE THIS

BASE_DIR = "files"
os.makedirs(BASE_DIR, exist_ok=True)

app = FastAPI()

@app.post("/save")
async def save_file(request: Request):
    auth = request.headers.get("authorization")

    if auth != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Invalid API key")

    data = await request.json()
    path = data.get("path")
    content = data.get("content")

    if not path or not content:
        raise HTTPException(status_code=400, detail="Missing path or content")

    safe_path = os.path.normpath(path).replace("..", "")
    full_path = os.path.join(BASE_DIR, safe_path)

    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

    return {"status": "saved", "path": f"/{safe_path}"}

@app.get("/{file_path:path}")
async def get_file(file_path: str):
    full_path = os.path.join(BASE_DIR, file_path)

    if not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="File not found")

    with open(full_path, "r", encoding="utf-8") as f:
        return PlainTextResponse(f.read())
