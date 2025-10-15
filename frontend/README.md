# BTS Tracker Frontend

A modern, responsive web interface for the BTS Tracker AI Assistant.

## Features

✅ **Real-time Streaming** - See AI responses word-by-word as they generate
✅ **Conversation History** - Browse and resume previous chats
✅ **Modern UI** - Clean, responsive design that works on all devices
✅ **Multi-turn Conversations** - Full context awareness across messages
✅ **Sample Prompts** - Quick-start suggestions for new users

## Quick Start

### Option 1: Open Directly (Simplest)

Just open `index.html` in your browser! No build process needed.

```bash
cd frontend
open index.html  # Mac
# or
start index.html  # Windows
# or
xdg-open index.html  # Linux
```

### Option 2: Local Server (Recommended)

For better development experience with live reload:

```bash
cd frontend

# Using Python
python3 -m http.server 8000

# Using Node.js
npx serve

# Using PHP
php -S localhost:8000
```

Then open: http://localhost:8000

## Configuration

The API URL is configured in `app.js`:

```javascript
const API_URL = 'https://bts-tracker.onrender.com/chatkit';
const USER_ID = 'default-user';
```

### For Local Development:

If you're running the backend locally, change:

```javascript
const API_URL = 'http://localhost:10000/chatkit';
```

### For Production:

Deploy the frontend to:
- **Vercel** - Zero config, automatic HTTPS
- **Netlify** - Simple drag & drop
- **GitHub Pages** - Free hosting
- **Render Static Site** - Same platform as backend

## File Structure

```
frontend/
├── index.html      # Main HTML structure
├── styles.css      # All styling
├── app.js          # ChatKit integration & logic
└── README.md       # This file
```

## Usage

### Starting a Conversation

1. Click a sample prompt, or
2. Type your message and press Enter

### Creating New Chats

Click the "➕ New Chat" button in the header

### Viewing History

Click any conversation in the sidebar to load it

### Keyboard Shortcuts

- `Enter` - Send message
- `Shift + Enter` - New line in message

## Customization

### Change Colors

Edit CSS variables in `styles.css`:

```css
:root {
    --primary-color: #2563eb;     /* Brand color */
    --background: #f8fafc;        /* Page background */
    --surface: #ffffff;           /* Card background */
    --text-primary: #0f172a;      /* Main text */
    --text-secondary: #475569;    /* Muted text */
}
```

### Add Your Logo

Replace the emoji in `index.html`:

```html
<h1>🐛 BTS Tracker</h1>
<!-- Change to: -->
<h1><img src="logo.png" alt="Logo"> BTS Tracker</h1>
```

### Modify Sample Prompts

Edit in `index.html`:

```html
<button class="sample-prompt" data-prompt="Your custom prompt here">
    💬 Your Button Text
</button>
```

## Features Explained

### Real-time Streaming

The app uses Server-Sent Events (SSE) to stream AI responses:

```javascript
const reader = response.body.getReader();
// Reads chunks and displays them immediately
```

### Conversation Management

- Auto-saves all conversations to the backend
- Loads thread history on demand
- Shows preview of recent messages

### Error Handling

- Network errors are caught and displayed
- Retries failed requests
- Shows helpful error messages

## Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## Deployment

### Deploy to Vercel:

```bash
cd frontend
npx vercel
```

### Deploy to Netlify:

```bash
cd frontend
npx netlify-cli deploy
```

### Deploy to GitHub Pages:

1. Push frontend folder to GitHub
2. Go to Settings → Pages
3. Select branch and `/frontend` folder
4. Done!

## Troubleshooting

### CORS Errors

Make sure your backend has CORS enabled (already done in main.py):

```python
app.add_middleware(CORSMiddleware, allow_origins=["*"])
```

### Streaming Not Working

Check browser console for errors. Make sure:
- Backend is running
- API_URL is correct
- OPENAI_API_KEY is set in Render

### Messages Not Loading

1. Check Network tab in DevTools
2. Verify API responses are 200 OK
3. Check backend logs on Render

## Next Steps

- Add user authentication
- Implement file attachments
- Add markdown rendering for code blocks
- Add voice input
- Add export conversation feature
- Add dark mode toggle

## Support

For issues or questions:
- Check backend logs on Render
- Review browser console for errors
- Test API directly with curl

---

**Your frontend is ready to use!** 🚀

Just open `index.html` and start chatting with your AI assistant.
