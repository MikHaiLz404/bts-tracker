from chatkit.server import ChatKitServer
from postgres_store import PostgresStore  # or your preferred Store
from chatkit.types import (
    ThreadMetadata,
    UserMessageItem,
    ThreadStreamEvent,
    AssistantMessageItem,
    AssistantMessageContent,
    ThreadItemDoneEvent
)
from typing import Any, AsyncIterator
from datetime import datetime

class MyChatKitServer(ChatKitServer):
    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: Any,
    ) -> AsyncIterator[ThreadStreamEvent]:
        # Simple echo implementation as a placeholder

        # Get the user's message text
        user_text = ""
        if input_user_message and input_user_message.content:
            for content_item in input_user_message.content:
                if hasattr(content_item, 'text'):
                    user_text = content_item.text
                    break

        # Create response message
        response_text = f"Echo: {user_text}" if user_text else "Hello! I'm your BTS Tracker assistant."

        # Create the assistant message item with proper structure
        assistant_item = AssistantMessageItem(
            id=self.store.generate_item_id("message", thread, context),
            thread_id=thread.id,
            created_at=datetime.now(),
            content=[
                AssistantMessageContent(
                    type="output_text",
                    text=response_text,
                    annotations=[]
                )
            ],
        )

        # Yield the completed item
        yield ThreadItemDoneEvent(item=assistant_item)