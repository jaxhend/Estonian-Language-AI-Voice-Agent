from fastapi import FastAPI
from app.api.ws import router as ws_router
from app.api.bookings_router import router as bookings_router
from app.api.analytics_router import router as analytics_router
import importlib
import pkgutil

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware to allow connections from any origin.
# This is necessary to allow our Python test client to connect.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.on_event("startup")
async def startup_event():
    """
    Dynamically imports all submodules on startup to ensure all event
    subscribers are registered with the shared event bus.
    """
    print("--- Running startup event: Discovering and importing submodules ---")
    package_name = "app"
    package = importlib.import_module(package_name)
    for _, module_name, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        try:
            print(f"Importing submodule: {module_name}")
            importlib.import_module(module_name)
        except Exception as e:
            print(f"Failed to import {module_name}: {e}")
    print("--- Submodule discovery complete ---")


app.include_router(ws_router)
app.include_router(bookings_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

