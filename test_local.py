#!/usr/bin/env python3
"""
Local test script to debug the ChatKit server
"""
import asyncio
import os
from request_context import RequestContext
from postgres_store import PostgresStore
from my_server import MyChatKitServer

async def test_thread_create():
    """Test creating a thread locally"""
    try:
        print("Initializing store...")
        store = PostgresStore()

        print("Initializing server...")
        server = MyChatKitServer(store)

        print("Creating request context...")
        context = RequestContext(user_id="test-user")

        print("Creating test request...")
        request_body = b'''{
            "type": "threads.create",
            "params": {
                "input": {
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Hello, this is a test message"
                        }
                    ],
                    "attachments": [],
                    "inference_options": {}
                }
            }
        }'''

        print("Processing request...")
        result = await server.process(request_body, context)

        print("\n=== SUCCESS ===")
        print(f"Result type: {type(result)}")
        print(f"Result: {result}")

    except Exception as e:
        print("\n=== ERROR ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_thread_create())
