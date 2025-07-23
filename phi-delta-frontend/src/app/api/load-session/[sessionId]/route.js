// src/app/api/load-session/[sessionId]/route.js
import { NextResponse } from 'next/server';

export async function POST(request, { params }) {
  try {
    const { sessionId } = params;
    
    const res = await fetch(`http://localhost:8001/load-session/${sessionId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    
    if (!res.ok) {
      return NextResponse.json({ status: 'error', message: 'Failed to load session' }, { status: 500 });
    }
    
    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error loading session:', error);
    return NextResponse.json({ status: 'error', message: 'Failed to load session' }, { status: 500 });
  }
}
