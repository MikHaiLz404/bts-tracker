from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse, Response
from postgres_store import PostgresStore
from my_server import MyChatKitServer  # import your custom server class
from request_context import RequestContext
from pydantic import ValidationError
import json

app = FastAPI()

# Initialize store and server
try:
    print("Initializing PostgresStore...")
    store = PostgresStore()
    print("PostgresStore initialized successfully")

    print("Initializing MyChatKitServer...")
    server = MyChatKitServer(store)
    print("MyChatKitServer initialized successfully")
except Exception as e:
    print(f"FATAL ERROR during initialization: {e}")
    import traceback
    traceback.print_exc()
    raise

@app.get("/")
async def health_check():
    """Health check endpoint for monitoring and root access."""
    return {
        "status": "ok",
        "service": "BTS Tracker ChatKit Server",
        "endpoints": {
            "chatkit": "/chatkit (POST)",
            "health": "/ (GET)"
        }
    }

@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    print(f"=== Received ChatKit request ===")
    try:
        # Get the raw body
        body = await request.body()

        # Try to parse as JSON for better error messages
        try:
            request_json = json.loads(body)

            # Check if 'type' field exists
            if not isinstance(request_json, dict) or 'type' not in request_json:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "Invalid request format",
                        "message": "Request must be a JSON object with a 'type' field",
                        "details": "Expected format: {\"type\": \"threads.create\", \"params\": {...}}",
                        "valid_types": [
                            "threads.create",
                            "threads.add_user_message",
                            "threads.add_client_tool_output",
                            "threads.retry_after_item",
                            "threads.custom_action",
                            "threads.get_by_id",
                            "threads.list",
                            "items.list",
                            "items.feedback",
                            "attachments.create",
                            "attachments.delete",
                            "threads.update",
                            "threads.delete"
                        ],
                        "note": "Use dots (.) not slashes (/) in type names"
                    }
                )
        except json.JSONDecodeError:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Invalid JSON",
                    "message": "Request body must be valid JSON"
                }
            )

        # Create a request context
        # For now, use a default user_id. In production, extract from auth headers
        # You can get user_id from JWT token, session, or other auth mechanism
        user_id = request.headers.get("X-User-ID", "default-user")
        context = RequestContext(user_id=user_id)
        print(f"Created context with user_id: {user_id}")

        # Process the request through ChatKit server
        print(f"Processing request through ChatKit server...")
        result = await server.process(body, context)
        print(f"Request processed successfully, result type: {type(result).__name__}")

        # Handle streaming vs non-streaming responses
        if hasattr(result, 'json_events'):
            # Streaming response (threads.create, threads.add_user_message, etc.)
            print("Returning streaming response")
            return StreamingResponse(
                result.json_events,
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        elif hasattr(result, 'json'):
            # Non-streaming response (threads.list, threads.get_by_id, etc.)
            print("Returning non-streaming response")
            return Response(
                content=result.json,
                media_type="application/json"
            )
        else:
            print(f"ERROR: Unknown result type: {type(result)}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": f"Unknown result type: {type(result).__name__}"
                }
            )

    except ValidationError as e:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Validation error",
                "message": str(e),
                "details": e.errors() if hasattr(e, 'errors') else None
            }
        )
    except Exception as e:
        # Log the error (in production, use proper logging)
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error processing ChatKit request: {str(e)}")
        print(f"Full traceback:\n{error_trace}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": str(e),
                "type": type(e).__name__,
                "traceback": error_trace.split('\n')[-10:]  # Last 10 lines of traceback
            }
        )