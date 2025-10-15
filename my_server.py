import os
from typing import Any, AsyncIterator

from agents import Agent
from chatkit.agents import AgentContext, stream_agent_response, ThreadItemConverter
from chatkit.server import ChatKitServer
from chatkit.types import ThreadMetadata, UserMessageItem, ThreadStreamEvent
from postgres_store import PostgresStore


class MyChatKitServer(ChatKitServer):
    """
    BTS Tracker ChatKit Server with AI Agent integration.

    This server uses the OpenAI Agents SDK to provide intelligent responses
    with support for workflows, streaming, and tool calling.
    """

    def __init__(self, store: PostgresStore):
        super().__init__(store)

        # Initialize the AI agent
        # You can customize the system prompt and model here
        self.agent = Agent(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            system_prompt=self._get_system_prompt(),
        )

        # Thread item converter for transforming ChatKit items to agent input
        self.converter = ThreadItemConverter()

    def _get_system_prompt(self) -> str:
        """
        Define your agent's system prompt here.
        Customize this to match your BTS Tracker use case.
        """
        return """You are a helpful AI assistant for the BTS Tracker system.

Your role is to help users track and manage their BTS (Bug Tracking System) items.
You can:
- Answer questions about bugs, tasks, and issues
- Help users search and filter their tracked items
- Provide status updates and summaries
- Assist with creating and updating tickets

Be concise, helpful, and professional in your responses."""

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: Any,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """
        Generate an AI response using the OpenAI Agents SDK.

        This method:
        1. Loads the conversation history from the database
        2. Converts it to agent input format
        3. Streams the agent's response with workflows and reasoning
        4. Handles tool calls and custom actions
        """

        # Create agent context for streaming events
        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )

        # Load thread history from database
        items = await self.store.load_thread_items(
            thread.id,
            after=None,
            limit=50,  # Load last 50 messages for context
            order="asc",
            context=context,
        )

        # Convert thread items to agent input format
        agent_input = await self.converter.to_agent_input(items.data)

        # Add the new user message if present
        if input_user_message:
            new_input = await self.converter.to_agent_input(input_user_message)
            agent_input.extend(new_input)

        # Run the agent and stream responses
        result = self.agent.run_stream(
            input=agent_input,
            # You can add additional parameters here:
            # temperature=0.7,
            # max_tokens=4096,
            # tools=[...],  # Add custom tools
        )

        # Stream the agent's response through ChatKit
        async for event in stream_agent_response(agent_context, result):
            yield event