import os
from typing import Any, AsyncIterator

from agents import Agent, Runner
from chatkit.agents import AgentContext, stream_agent_response, ThreadItemConverter
from chatkit.server import ChatKitServer
from chatkit.types import ThreadMetadata, UserMessageItem, ThreadStreamEvent
from postgres_store import PostgresStore


class MyChatKitServer(ChatKitServer):
    """
    BTS (Bangkok Mass Transit System) ChatKit Server with AI Agent integration.

    This server helps users with BTS Skytrain queries including schedules,
    routes, and real-time status information.
    """

    def __init__(self, store: PostgresStore):
        super().__init__(store)

        # Initialize the AI agent
        # You can customize the instructions and model here
        model = os.getenv("OPENAI_MODEL", "gpt-4o")
        instructions = self._get_instructions()

        self.agent = Agent(
            name="BTS Train Assistant",
            model=model,
            instructions=instructions,
        )

        # Thread item converter for transforming ChatKit items to agent input
        self.converter = ThreadItemConverter()

    def _get_instructions(self) -> str:
        """
        Define your agent's instructions for BTS train queries.
        """
        return """You are a helpful AI assistant for the BTS (Bangkok Mass Transit System) Skytrain in Bangkok, Thailand.

Your role is to help users with BTS train information and queries in these categories:

1. **Schedule Queries** - Train timetables, operating hours, first/last train times
2. **Route Planning** - How to travel between stations, transfers, directions, estimated travel time
3. **Real-time Status** - Current train status, delays, service disruptions, platform information

When users ask questions, you should:
- Provide accurate, helpful information about BTS trains
- Classify their question type (schedule_query, route_planning, or realtime_status)
- Extract relevant details like station names, times, and directions
- Be concise and friendly in your responses
- If you don't have specific real-time data, acknowledge it and provide general guidance

The BTS has two lines:
- **Sukhumvit Line** (Light Green): Mo Chit to Kheha/Samrong
- **Silom Line** (Dark Green): National Stadium to Bang Wa

Operating hours: Approximately 5:30 AM - midnight daily (may vary by station)

Be helpful, professional, and focused on transit information."""

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
        result = Runner.run_streamed(
            self.agent,
            input=agent_input,
            # You can add additional parameters here:
            # temperature=0.7,
            # max_tokens=4096,
            # tools=[...],  # Add custom tools
        )

        # Stream the agent's response through ChatKit
        async for event in stream_agent_response(agent_context, result):
            yield event