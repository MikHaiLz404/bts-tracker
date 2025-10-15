// Configuration
const API_URL = 'https://bts-tracker.onrender.com/chatkit';
const USER_ID = 'default-user'; // You can make this dynamic with auth

// State
let currentThreadId = null;
let threads = [];
let isStreaming = false;
let currentStreamingMessage = null;

// DOM Elements
const welcomeScreen = document.getElementById('welcomeScreen');
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const sendBtnText = document.getElementById('sendBtnText');
const sendBtnLoader = document.getElementById('sendBtnLoader');
const newThreadBtn = document.getElementById('newThreadBtn');
const threadList = document.getElementById('threadList');
const statusBar = document.getElementById('statusBar');
const statusText = document.getElementById('statusText');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadThreads();
    setStatus('Ready');
});

// Event Listeners
function setupEventListeners() {
    sendBtn.addEventListener('click', sendMessage);
    newThreadBtn.addEventListener('click', createNewThread);

    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    messageInput.addEventListener('input', () => {
        autoResizeTextarea();
    });

    // Sample prompts
    document.querySelectorAll('.sample-prompt').forEach(btn => {
        btn.addEventListener('click', () => {
            const prompt = btn.dataset.prompt;
            messageInput.value = prompt;
            sendMessage();
        });
    });
}

// Auto-resize textarea
function autoResizeTextarea() {
    messageInput.style.height = 'auto';
    messageInput.style.height = messageInput.scrollHeight + 'px';
}

// Create new thread
async function createNewThread() {
    currentThreadId = null;
    chatMessages.innerHTML = '';
    chatMessages.style.display = 'none';
    welcomeScreen.style.display = 'flex';
    messageInput.value = '';
    messageInput.focus();
    updateThreadList();
    setStatus('Ready for new conversation');
}

// Send message
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || isStreaming) return;

    // Add user message to UI
    addUserMessage(message);
    messageInput.value = '';
    autoResizeTextarea();

    // Show chat messages, hide welcome
    welcomeScreen.style.display = 'none';
    chatMessages.style.display = 'flex';

    // Disable input
    setLoading(true);

    try {
        if (currentThreadId) {
            // Add to existing thread
            await addMessageToThread(currentThreadId, message);
        } else {
            // Create new thread
            await createThreadWithMessage(message);
        }
    } catch (error) {
        console.error('Error sending message:', error);
        addSystemMessage('Error: Failed to send message. Please try again.');
        setLoading(false);
    }
}

// Create thread with first message
async function createThreadWithMessage(message) {
    setStatus('Creating new conversation...');

    const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-User-ID': USER_ID
        },
        body: JSON.stringify({
            type: 'threads.create',
            params: {
                input: {
                    content: [{
                        type: 'input_text',
                        text: message
                    }],
                    attachments: [],
                    inference_options: {}
                }
            }
        })
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    await handleStreamResponse(response);
}

// Add message to existing thread
async function addMessageToThread(threadId, message) {
    setStatus('Sending message...');

    const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-User-ID': USER_ID
        },
        body: JSON.stringify({
            type: 'threads.add_user_message',
            params: {
                thread_id: threadId,
                input: {
                    content: [{
                        type: 'input_text',
                        text: message
                    }],
                    attachments: [],
                    inference_options: {}
                }
            }
        })
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    await handleStreamResponse(response);
}

// Handle streaming response
async function handleStreamResponse(response) {
    isStreaming = true;
    setStatus('AI is thinking...');

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    try {
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    try {
                        const event = JSON.parse(data);
                        handleStreamEvent(event);
                    } catch (e) {
                        console.error('Error parsing event:', e, data);
                    }
                }
            }
        }
    } finally {
        isStreaming = false;
        currentStreamingMessage = null;
        setLoading(false);
        setStatus('Ready');
    }
}

// Handle individual stream events
function handleStreamEvent(event) {
    switch (event.type) {
        case 'thread.created':
            currentThreadId = event.thread.id;
            addThreadToList({
                id: event.thread.id,
                title: 'New Conversation',
                preview: 'Just now',
                created_at: event.thread.created_at
            });
            break;

        case 'thread.item.done':
            if (event.item.type === 'user_message') {
                // User message confirmed
            }
            break;

        case 'thread.item.added':
            if (event.item.type === 'assistant_message') {
                currentStreamingMessage = addAssistantMessage('');
                setStatus('AI is responding...');
            }
            break;

        case 'thread.item.updated':
            if (event.update.type === 'assistant_message.content_part.text_delta') {
                if (currentStreamingMessage) {
                    const content = currentStreamingMessage.querySelector('.message-text');
                    content.textContent += event.update.delta;
                    scrollToBottom();
                }
            } else if (event.update.type === 'assistant_message.content_part.done') {
                if (currentStreamingMessage) {
                    currentStreamingMessage.classList.remove('message-streaming');
                }
            }
            break;
    }
}

// UI Functions
function addUserMessage(text) {
    const messageEl = document.createElement('div');
    messageEl.className = 'message user';
    messageEl.innerHTML = `
        <div class="message-avatar">👤</div>
        <div class="message-content">
            <div class="message-text">${escapeHtml(text)}</div>
        </div>
    `;
    chatMessages.appendChild(messageEl);
    scrollToBottom();
    return messageEl;
}

function addAssistantMessage(text) {
    const messageEl = document.createElement('div');
    messageEl.className = 'message assistant message-streaming';
    messageEl.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <div class="message-text">${escapeHtml(text)}</div>
        </div>
    `;
    chatMessages.appendChild(messageEl);
    scrollToBottom();
    return messageEl;
}

function addSystemMessage(text) {
    const messageEl = document.createElement('div');
    messageEl.className = 'message system';
    messageEl.innerHTML = `
        <div class="message-content">
            <div class="message-text">${escapeHtml(text)}</div>
        </div>
    `;
    chatMessages.appendChild(messageEl);
    scrollToBottom();
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function setLoading(loading) {
    sendBtn.disabled = loading;
    messageInput.disabled = loading;

    if (loading) {
        sendBtnText.style.display = 'none';
        sendBtnLoader.style.display = 'block';
    } else {
        sendBtnText.style.display = 'block';
        sendBtnLoader.style.display = 'none';
    }
}

function setStatus(text) {
    statusText.textContent = text;
}

// Thread list management
async function loadThreads() {
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-User-ID': USER_ID
            },
            body: JSON.stringify({
                type: 'threads.list',
                params: {}
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        threads = data.data || [];
        updateThreadList();
    } catch (error) {
        console.error('Error loading threads:', error);
    }
}

function addThreadToList(thread) {
    const existingIndex = threads.findIndex(t => t.id === thread.id);
    if (existingIndex >= 0) {
        threads[existingIndex] = thread;
    } else {
        threads.unshift(thread);
    }
    updateThreadList();
}

function updateThreadList() {
    if (threads.length === 0) {
        threadList.innerHTML = `
            <div class="empty-state">
                <p>No conversations yet</p>
                <p class="empty-hint">Start a new chat to begin</p>
            </div>
        `;
        return;
    }

    threadList.innerHTML = threads.map(thread => `
        <div class="thread-item ${thread.id === currentThreadId ? 'active' : ''}"
             data-thread-id="${thread.id}">
            <div class="thread-title">${escapeHtml(thread.title || 'New Conversation')}</div>
            <div class="thread-preview">${escapeHtml(thread.preview || 'Click to view')}</div>
        </div>
    `).join('');

    // Add click handlers
    document.querySelectorAll('.thread-item').forEach(item => {
        item.addEventListener('click', () => {
            const threadId = item.dataset.threadId;
            loadThread(threadId);
        });
    });
}

async function loadThread(threadId) {
    try {
        setStatus('Loading conversation...');

        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-User-ID': USER_ID
            },
            body: JSON.stringify({
                type: 'threads.get_by_id',
                params: {
                    thread_id: threadId
                }
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const thread = await response.json();
        currentThreadId = threadId;

        // Clear and populate messages
        chatMessages.innerHTML = '';
        welcomeScreen.style.display = 'none';
        chatMessages.style.display = 'flex';

        // Load items
        const itemsResponse = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-User-ID': USER_ID
            },
            body: JSON.stringify({
                type: 'items.list',
                params: {
                    thread_id: threadId
                }
            })
        });

        const items = await itemsResponse.json();

        // Display messages
        for (const item of items.data.reverse()) {
            if (item.type === 'user_message') {
                const text = item.content.map(c => c.text).join(' ');
                addUserMessage(text);
            } else if (item.type === 'assistant_message') {
                const text = item.content.map(c => c.text).join(' ');
                const msg = addAssistantMessage(text);
                msg.classList.remove('message-streaming');
            }
        }

        updateThreadList();
        setStatus('Ready');
    } catch (error) {
        console.error('Error loading thread:', error);
        setStatus('Error loading conversation');
    }
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
