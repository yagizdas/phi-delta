// src/app/api/chat/route.js
import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    const { message } = await request.json();
    
    const res = await fetch('http://localhost:8001/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });

    if (!res.ok) {
      throw new Error(`Backend responded with status: ${res.status}`);
    }

    // Check if response is streaming (text/plain) or JSON
    const contentType = res.headers.get('content-type');
    
    if (contentType && contentType.includes('text/plain')) {
      // Handle streaming response
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      console.log('💭 Streaming response from backend...');
      return new Response(
        new ReadableStream({
          async start(controller) {
            try {
              while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                const chunk = decoder.decode(value, { stream: true });
                console.log('💭 Streaming response from backend:', chunk);
                controller.enqueue(new TextEncoder().encode(chunk));
              }
              controller.close();
            } catch (error) {
              controller.error(error);
            }
          }
        }),
        {
          headers: {
            'Content-Type': 'text/plain',
            'Transfer-Encoding': 'chunked',
          }
        }
      );
    } else {
      // Handle JSON response (for agentic tasks)
      const { reply } = await res.json();
      return Response.json({ reply });
    }
  } catch (error) {
    console.error('Chat API error:', error);
    return Response.json(
      { error: 'Failed to get response from chat service' },
      { status: 500 }
    );
  }
}
