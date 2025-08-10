# reconmaster/app/main.py

from fastapi import FastAPI, Request # <-- MODIFIED: Add Request
from fastapi.responses import HTMLResponse # <-- ADD THIS LINE
from fastapi.staticfiles import StaticFiles # <-- ADD THIS LINE
from fastapi.templating import Jinja2Templates # <-- ADD THIS LINE

from .db import models
from .db.database import engine
from .api import routes

# This line creates the database tables if they don't exist.
models.Base.metadata.create_all(bind=engine)

# Create the FastAPI application instance
app = FastAPI(
    title="ReconMaster API",
    description="An API for running reconnaissance tools.",
    version="0.1.0"
)

# Mount the static directory to serve CSS, JS, etc.
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 templates for rendering HTML
templates = Jinja2Templates(directory="templates")

# Include the API routes from the routes.py file
app.include_router(routes.router, prefix="/api")

# Define the root endpoint to serve the main HTML page
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    """
    Serves the main index.html page.
    """
    return templates.TemplateResponse("index.html", {"request": request})
