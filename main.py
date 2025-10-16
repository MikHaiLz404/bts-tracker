"""
OpenAI Hosted ChatKit Server
This is the simpler approach using OpenAI's Agent Builder workflow.
Your workflow ID: wf_68ede44222f88190a40adde9470d356c0357b9e0e6a723a9
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Your Agent Builder workflow ID (BTS query classifier)
WORKFLOW_ID = "wf_68ede44222f88190a40adde9470d356c0357b9e0e6a723a9"


class SessionRequest(BaseModel):
    """Optional: Add any custom parameters you need"""
    user_id: str | None = None
    metadata: dict | None = None


@app.get("/")
async def root():
    """Serve the ChatKit frontend"""
    return FileResponse("frontend/index_chatkit_hosted.html")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "BTS Train Assistant - OpenAI ChatKit",
        "workflow_id": WORKFLOW_ID,
        "endpoints": {
            "chat": "/ (GET)",
            "session": "/api/chatkit/session (POST)",
            "health": "/health (GET)"
        }
    }


# Serve static files from frontend directory
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.post("/api/chatkit/session")
async def create_chatkit_session(request: SessionRequest | None = None):
    """
    Create a new ChatKit session for the frontend.
    This endpoint is called by your frontend to initialize ChatKit UI.

    Returns the client_secret that the frontend uses to connect to OpenAI's ChatKit server.

    This follows the official OpenAI ChatKit documentation pattern.
    """
    try:
        # Generate a device/user ID (you can customize this based on your auth)
        user_id = request.user_id if request and request.user_id else "default-user"

        print(f"Creating ChatKit session for workflow: {WORKFLOW_ID}, user: {user_id}")

        # Create session with your workflow (following official docs pattern)
        session = openai_client.chatkit.sessions.create(
            workflow={"id": WORKFLOW_ID},
            user=user_id,
            # Optional: Add custom metadata
            # metadata=request.metadata if request and request.metadata else {}
        )

        print(f"Session created successfully")

        # Return just the client_secret as per docs
        return {
            "client_secret": session.client_secret
        }

    except Exception as e:
        print(f"Error creating ChatKit session: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "type": type(e).__name__
        }, 500


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
