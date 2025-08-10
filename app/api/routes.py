# reconmaster/app/api/routes.py

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List

from ..db import models
from ..db.database import SessionLocal
from . import schemas
from ..services import executor # <-- ADD THIS IMPORT

router = APIRouter()

# Dependency to get a DB session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Reusable function to get tool from DB ---
def get_tool(db: Session, tool_id: int):
    tool = db.query(models.Tool).filter(models.Tool.id == tool_id).first()
    if tool is None:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool

# --- API endpoint to get a list of all tools ---
@router.get("/tools", response_model=List[schemas.Tool])
def get_all_tools(db: Session = Depends(get_db)):
    tools = db.query(models.Tool).all()
    return tools

# --- API endpoint to get a single tool by its ID ---
@router.get("/tools/{tool_id}", response_model=schemas.Tool)
def get_tool_by_id(tool_id: int, db: Session = Depends(get_db)):
    return get_tool(db=db, tool_id=tool_id)


# --- NEW: WebSocket endpoint for running commands ---
@router.websocket("/ws/run/{tool_id}")
async def websocket_endpoint(websocket: WebSocket, tool_id: int, db: Session = Depends(get_db)):
    await websocket.accept()
    try:
        # 1. Get the tool details from the database
        tool = get_tool(db=db, tool_id=tool_id)

        # 2. Wait for the client to send the target
        target = await websocket.receive_text()
        await websocket.send_text(f"INFO: Received target '{target}' for tool '{tool.name}'. Starting process...")

        # 3. Call the executor to run the command and stream output
        await executor.run_command_stream(
            tool_name=tool.name,
            target=target,
            websocket=websocket
        )

    except WebSocketDisconnect:
        print(f"Client disconnected from WebSocket.")
    except Exception as e:
        # Handle any other exceptions and inform the client
        error_message = f"An unexpected error occurred: {str(e)}"
        print(error_message)
        await websocket.send_text(f"ERROR: {error_message}")
    finally:
        # Ensure the websocket is closed
        await websocket.close()
