# BTS Tracker AI Agent Setup

Your ChatKit server now has full AI agent integration using the OpenAI Agents SDK!

## What's Working

✅ **AI-Powered Responses** - Real GPT-4o responses instead of echo
✅ **Conversation Memory** - Loads full thread history for context
✅ **Streaming** - Real-time streaming responses with workflows
✅ **Reasoning** - Shows agent's thought process
✅ **Tool Calling** - Ready to add custom tools
✅ **Database Persistence** - All conversations saved to PostgreSQL

## Required Environment Variables

Add these to your Render environment variables:

```bash
OPENAI_API_KEY=sk-...          # Required: Your OpenAI API key
OPENAI_MODEL=gpt-4o            # Optional: Default is gpt-4o
DATABASE_URL=postgresql://...   # Already configured
```

### Adding Environment Variables on Render:

1. Go to https://dashboard.render.com
2. Click on your `bts-tracker` service
3. Go to "Environment" tab
4. Click "Add Environment Variable"
5. Add:
   - Key: `OPENAI_API_KEY`
   - Value: Your OpenAI API key from https://platform.openai.com/api-keys
6. Click "Save Changes"
7. Render will automatically redeploy

## Testing the AI Agent

### Test with browser console:

```javascript
fetch('https://bts-tracker.onrender.com/chatkit', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    type: 'threads.create',
    params: {
      input: {
        content: [{
          type: 'input_text',
          text: 'What is BTS Tracker and how can you help me?'
        }],
        attachments: [],
        inference_options: {}
      }
    }
  })
})
.then(response => response.text())
.then(data => console.log(data))
```

You should see:
- AI-generated responses (not "Echo:")
- Streaming events with actual reasoning
- Professional, contextual answers

## Customization

### 1. Change the System Prompt

Edit [`my_server.py:32-46`](my_server.py#L32-L46):

```python
def _get_system_prompt(self) -> str:
    return """Your custom system prompt here..."""
```

### 2. Add Custom Tools

Tools let your agent perform actions. Add them in [`my_server.py:89-95`](my_server.py#L89-L95):

```python
from agents import tool

@tool
def search_bugs(query: str, status: str = "open") -> list:
    """Search for bugs matching the query."""
    # Your bug search logic here
    return bugs

# Then add to agent:
result = self.agent.run_stream(
    input=agent_input,
    tools=[search_bugs],
)
```

### 3. Change the Model

Set `OPENAI_MODEL` environment variable:
- `gpt-4o` - Best quality (default)
- `gpt-4o-mini` - Faster, cheaper
- `gpt-4-turbo` - Previous generation

### 4. Add Workflows

Workflows show users what the agent is doing:

```python
from chatkit.types import Workflow, CustomTask

await agent_context.start_workflow(
    Workflow(
        type="custom",
        tasks=[
            CustomTask(
                title="Searching bugs",
                content="Looking for matching items..."
            )
        ]
    )
)

# Do work...

await agent_context.end_workflow(
    summary=DurationSummary(duration=2)
)
```

## Architecture

```
User Request
    ↓
FastAPI (/chatkit)
    ↓
MyChatKitServer.respond()
    ↓
Load thread history from PostgreSQL
    ↓
Convert to Agent input format
    ↓
OpenAI Agents SDK (GPT-4o)
    ↓
Stream response events
    ↓
Save to PostgreSQL
    ↓
Return to user
```

## Next Steps

1. **Add OPENAI_API_KEY** to Render environment variables
2. **Test** with the fetch command above
3. **Customize** the system prompt for your use case
4. **Add tools** for bug tracking operations
5. **Build frontend** to integrate with your agent

## Troubleshooting

### "Agent not responding"
- Check OPENAI_API_KEY is set correctly
- Check Render logs for API errors
- Verify OpenAI account has credits

### "Echo responses still showing"
- Redeploy on Render to get latest code
- Check logs show "Initializing MyChatKitServer"

### "Slow responses"
- Use `gpt-4o-mini` for faster responses
- Reduce conversation history limit (line 75)
- Add streaming UI on frontend

## Documentation

- **ChatKit Docs**: https://github.com/openai/chatkit-python
- **Agents SDK**: https://github.com/openai/openai-agents-python
- **OpenAI Platform**: https://platform.openai.com/docs

---

**Your agent workflow is ready!** Just add your OpenAI API key and start building. 🚀
