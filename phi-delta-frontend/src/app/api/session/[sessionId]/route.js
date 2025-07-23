// src/app/api/session/[sessionId]/route.js
import { NextResponse } from 'next/server';

export async function DELETE(request, { params }) {
  try {
    const { sessionId } = params;
    
    const res = await fetch(`http://localhost:8001/session/${sessionId}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
    });
    
    if (!res.ok) {
      return NextResponse.json({ status: 'error', message: 'Failed to delete session' }, { status: 500 });
    }
    
    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error deleting session:', error);
    return NextResponse.json({ status: 'error', message: 'Failed to delete session' }, { status: 500 });
  }
}
