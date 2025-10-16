# BTS Train Assistant - OpenAI ChatKit Setup

## Quick Start Guide

Your workflow is ready: `wf_68ede44222f88190a40adde9470d356c0357b9e0e6a723a9`

### Step 1: Deploy the Backend

**Switch to the ChatKit hosted server:**

```bash
# Backup your current setup
mv main.py main_custom_backup.py

# Use the simplified ChatKit server
cp main_chatkit_hosted.py main.py

# Commit and push
git add main.py
git commit -m "Use OpenAI hosted ChatKit"
git push
```

Render will auto-deploy. The server only needs to:
- Create ChatKit sessions
- Return client_secret

### Step 2: Test the Frontend

**Option A: Vanilla JavaScript (Simple)**

```bash
cd frontend
open index_chatkit_hosted.html
```

Change the API_URL if testing locally:
```javascript
const API_URL = 'http://localhost:10000/api/chatkit/session';
```

**Option B: React (Recommended for production)**

```bash
# Install dependencies
npm install @openai/chatkit-react

# Use the example component
# See: frontend/chatkit-react-example.tsx
```

### Step 3: Verify It Works

1. Open your frontend
2. Check browser console for logs
3. You should see:
   - "ChatKit SDK loaded"
   - "Got client secret"
   - "ChatKit initialized successfully"
4. Ask: "What time is the first train from Siam?"

Your workflow will:
- Classify the query as `schedule_query`
- Return appropriate BTS train information

## Architecture

```
Frontend (Your HTML/React)
    ↓ Fetch client_secret
Backend (/api/chatkit/session)
    ↓ Create session with workflow ID
OpenAI ChatKit Server (Hosted)
    ↓ Run your workflow
Agent Builder Workflow (wf_68ede...)
    ↓ Classify & respond
User gets answer!
```

## Files Overview

| File | Purpose |
|------|---------|
| `main_chatkit_hosted.py` | Session endpoint (deploy this) |
| `index_chatkit_hosted.html` | Vanilla JS frontend |
| `chatkit-react-example.tsx` | React component example |
| `main_custom_backup.py` | Your old custom server (backup) |

## Environment Variables

Make sure these are set in Render:

```bash
OPENAI_API_KEY=sk-...  # Required
```

That's it! No DATABASE_URL needed for hosted ChatKit.

## Customization

### Change Theme

In HTML:
```javascript
const chatkit = await window.OpenAI.ChatKit.create({
    clientSecret: clientSecret,
    container: container,
    theme: {
        primaryColor: '#10b981', // Green for BTS
        // More theme options...
    }
});
```

In React:
```tsx
<ChatKit
    control={control}
    className="h-[600px]"
    theme={{ primaryColor: '#10b981' }}
/>
```

### Add User Authentication

Update the session endpoint:

```python
@app.post("/api/chatkit/session")
async def create_chatkit_session(request: SessionRequest):
    # Get user from your auth system
    user_id = get_authenticated_user_id(request)

    session = openai_client.chatkit.sessions.create(
        workflow={"id": WORKFLOW_ID},
        user=user_id,  # Track per-user conversations
    )
    return {"client_secret": session.client_secret}
```

### Modify Your Workflow

1. Go to OpenAI Agent Builder
2. Find workflow: `wf_68ede44222f88190a40adde9470d356c0357b9e0e6a723a9`
3. Edit the classification logic
4. Add more response types
5. Changes take effect immediately (no redeployment needed!)

## Troubleshooting

### "Failed to load ChatKit"

**Check 1: Is your server running?**
```bash
curl -X POST https://bts-tracker.onrender.com/api/chatkit/session
```

Should return: `{"client_secret": "..."}`

**Check 2: Is OPENAI_API_KEY set?**
- Go to Render dashboard
- Environment tab
- Verify OPENAI_API_KEY exists

**Check 3: Browser console errors?**
- Open DevTools (F12)
- Check Console tab
- Look for specific error messages

### "Workflow not found"

Your workflow ID might be incorrect. Verify in OpenAI dashboard:
```
Current: wf_68ede44222f88190a40adde9470d356c0357b9e0e6a723a9
```

### CORS errors

Already handled in `main_chatkit_hosted.py`:
```python
app.add_middleware(CORSMiddleware, allow_origins=["*"])
```

### Session expires

The frontend automatically handles this with the `getClientSecret(existing)` callback.

## Testing Locally

```bash
# Terminal 1: Run server
python3 -m uvicorn main_chatkit_hosted:app --reload --port 10000

# Terminal 2: Serve frontend
cd frontend
python3 -m http.server 8000

# Open: http://localhost:8000/index_chatkit_hosted.html
```

## Deployment

### Backend (Already on Render)
- Just push `main_chatkit_hosted.py` as `main.py`
- Render auto-deploys

### Frontend Options

**Option 1: Vercel (Recommended)**
```bash
cd frontend
npx vercel
```

**Option 2: Netlify**
```bash
cd frontend
npx netlify-cli deploy
```

**Option 3: GitHub Pages**
- Push to GitHub
- Settings → Pages
- Deploy from branch

## Next Steps

1. ✅ Deploy backend with `main_chatkit_hosted.py`
2. ✅ Test with `index_chatkit_hosted.html`
3. 🔜 Customize theme and styling
4. 🔜 Add user authentication
5. 🔜 Enhance your Agent Builder workflow
6. 🔜 Deploy frontend to production

## Resources

- **ChatKit Docs**: https://platform.openai.com/docs/chatkit
- **Agent Builder**: https://platform.openai.com/agent-builder
- **React SDK**: https://github.com/openai/chatkit-js
- **Your Workflow**: Check OpenAI dashboard

---

**You're ready to go!** Just switch to `main_chatkit_hosted.py` and test the frontend.
