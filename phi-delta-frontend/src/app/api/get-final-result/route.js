// src/app/api/get-final-result/route.js
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const res = await fetch('http://localhost:8001/get-final-result');
    if (!res.ok) {
      return NextResponse.json({ result: null });
    }

    // Check if response is streaming (text/plain) or JSON
    const contentType = res.headers.get('content-type');
    
    if (contentType && contentType.includes('text/plain')) {
      // Handle streaming response - pass it through
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      console.log('💭 Streaming final result from backend...');
      
      return new Response(
        new ReadableStream({
          async start(controller) {
            try {
              while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                const chunk = decoder.decode(value, { stream: true });
                console.log('💭 Final result chunk:', chunk);
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
      // Handle JSON response (fallback)
      const result = await res.json();
      return NextResponse.json(result);
    }
  } catch (error) {
    console.error('Error fetching final result:', error);
    return NextResponse.json({ result: null });
  }
}
