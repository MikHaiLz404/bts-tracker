/**
 * React ChatKit Integration Example
 *
 * Install: npm install @openai/chatkit-react
 *
 * Your workflow: wf_68ede44222f88190a40adde9470d356c0357b9e0e6a723a9
 */

import { ChatKit, useChatKit } from '@openai/chatkit-react';

export function BTSTrainChat() {
  const { control } = useChatKit({
    api: {
      async getClientSecret(existing) {
        // If there's an existing session, you could refresh it here
        if (existing) {
          // Optional: implement session refresh logic
          // For now, we'll just create a new session
        }

        // Fetch client secret from your backend
        const res = await fetch('/api/chatkit/session', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          // Optional: pass user info
          // body: JSON.stringify({ user_id: 'some-user-id' })
        });

        const { client_secret } = await res.json();
        return client_secret;
      },
    },
  });

  return (
    <div className="bts-chat-container">
      <h1>🚇 BTS Train Assistant</h1>
      <p>Ask about Bangkok Skytrain schedules, routes, and status</p>

      <ChatKit
        control={control}
        className="h-[600px] w-[400px]"
      />
    </div>
  );
}

/**
 * Alternative: Full page chat
 */
export function BTSTrainChatFullPage() {
  const { control } = useChatKit({
    api: {
      async getClientSecret(existing) {
        const res = await fetch('/api/chatkit/session', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        });
        const { client_secret } = await res.json();
        return client_secret;
      },
    },
  });

  return <ChatKit control={control} className="w-full h-screen" />;
}
