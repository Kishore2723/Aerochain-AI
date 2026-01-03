from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from agent import generate_response
import uvicorn
import os

app = FastAPI(title="Aerochain")


# Mount frontend directory
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# CORS Configuration
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/health")
async def health_check():
    return {"status": "ok", "system": "Aerochain Core Online"}

@app.post("/chat")
async def chat_endpoint(
    message: str = Form(...),
    file: UploadFile = File(None)
):
    """
    Streaming chat endpoint with multimodal support.
    """
    if not message and not file:
        raise HTTPException(status_code=400, detail="Message or file required")

    return StreamingResponse(
        generate_response(message, file),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
