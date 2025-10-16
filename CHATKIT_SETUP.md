# OpenAI ChatKit Setup (Hosted Approach)

You now have **two approaches** in this repo:

## Approach 1: Custom ChatKit Server (What we built first)
- Files: `main.py`, `my_server.py`, `postgres_store.py`
- Full control over agent logic
- You manage everything

## Approach 2: OpenAI Hosted ChatKit (Simpler - What you need)
- Files: `main_chatkit_hosted.py`, `frontend/index_chatkit_hosted.html`
- Uses your Agent Builder workflow
- OpenAI manages the AI backend

---

# Using OpenAI Hosted ChatKit (Recommended for your workflow)

## Step 1: Your Workflow is Ready ✅

You already created it in Agent Builder:
```
Workflow ID: wf_68ede44222f88190a40adde9470d356c0357b9e0e6a723a9
```

This workflow classifies BTS queries into:
- `schedule_query`
- `route_planning`
- `realtime_status`

## Step 2: Deploy the Session Endpoint

### Option A: Use the new simplified server

**Replace your current main.py with the hosted version:**

```bash
# Backup old main.py
mv main.py main_custom.py

# Use the hosted version
cp main_chatkit_hosted.py main.py
```

**Then commit and push:**
```bash
git add main.py
git commit -m "Switch to OpenAI hosted ChatKit"
git push
```

Render will auto-deploy.

### Option B: Add the endpoint to existing main.py

Add this to your current `main.py`:

```python
from openai import OpenAI

openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
WORKFLOW_ID = "wf_68ede44222f88190a40adde9470d356c0357b9e0e6a723a9"

@app.post("/api/chatkit/session")
async def create_chatkit_session():
    session = openai_client.chatkit.sessions.create(
        workflow_id=WORKFLOW_ID
    )
    return {"client_secret": session.client_secret}
```

## Step 3: Use the New Frontend

**Open the hosted ChatKit frontend:**

```bash
cd frontend
open index_chatkit_hosted.html
```

Or deploy it to:
- Vercel
- Netlify
- GitHub Pages
- Anywhere that serves static HTML

## Step 4: Test It

1. Make sure `OPENAI_API_KEY` is set in Render
2. Open `index_chatkit_hosted.html` in browser
3. ChatKit UI will load automatically
4. Ask: "What time is the first train from Siam to Asok?"

## Architecture

```
Your Frontend (HTML + ChatKit UI)
    ↓ (Fetch client_secret)
Your Server (/api/chatkit/session)
    ↓ (Create session)
OpenAI ChatKit Server (Hosted by OpenAI)
    ↓ (Run workflow)
Your Agent Builder Workflow (wf_68ede...)
    ↓ (Classify & respond)
User gets answer!
```

## Key Differences

| Feature | Custom Server | Hosted ChatKit |
|---------|--------------|----------------|
| **Complexity** | High | Low |
| **Control** | Full | Limited |
| **Maintenance** | You manage | OpenAI manages |
| **Cost** | Your infrastructure | OpenAI API calls |
| **Setup Time** | Hours | Minutes |
| **Best For** | Custom needs | Quick deployment |

## What Your Workflow Does

Your Agent Builder workflow (`wf_68ede...`) receives questions like:

**Input:** "What time is the first train from Siam?"

**Output (Classification):**
```json
{
  "classification": "schedule_query"
}
```

The workflow classifies and responds appropriately for each type.

## Next Steps

1. **Test the hosted version** - Open `index_chatkit_hosted.html`
2. **Deploy to production** - Use Vercel/Netlify for frontend
3. **Customize the workflow** - Edit in Agent Builder
4. **Add more features** - Authentication, analytics, etc.

## Troubleshooting

### "Failed to load ChatKit"
- Check OPENAI_API_KEY is set in Render
- Check `/api/chatkit/session` endpoint is working
- Check browser console for errors

### "Workflow not found"
- Verify workflow ID: `wf_68ede44222f88190a40adde9470d356c0357b9e0e6a723a9`
- Check it exists in your OpenAI Agent Builder

### CORS errors
- CORS middleware is already configured in the server
- Make sure it's deployed and accessible

## Documentation

- **ChatKit Docs**: https://platform.openai.com/docs/chatkit
- **Agent Builder**: https://platform.openai.com/agent-builder
- **Your Workflow**: Check OpenAI dashboard

---

**You're almost done!** Just switch to `main_chatkit_hosted.py` and test the new frontend.
