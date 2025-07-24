// src/app/api/get-chat-title/[sessionId]/route.js
import { NextResponse } from 'next/server';

export async function GET(request, { params }) {
  try {
    const { sessionId } = await params;
    
    const res = await fetch(`http://localhost:8001/get-chat-title/${sessionId}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    
    if (!res.ok) {
      return NextResponse.json({ 
        status: 'error', 
        message: 'Failed to generate title' 
      }, { status: 500 });
    }
    
    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error generating chat title:', error);
    return NextResponse.json({ 
      status: 'error', 
      message: 'Internal server error' 
    }, { status: 500 });
  }
}
