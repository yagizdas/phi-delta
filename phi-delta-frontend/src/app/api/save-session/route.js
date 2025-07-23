// src/app/api/save-session/route.js
import { NextResponse } from 'next/server';

export async function POST() {
  try {
    const res = await fetch('http://localhost:8001/save-session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    
    if (!res.ok) {
      return NextResponse.json({ status: 'error', message: 'Failed to save session' }, { status: 500 });
    }
    
    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error saving session:', error);
    return NextResponse.json({ status: 'error', message: 'Failed to save session' }, { status: 500 });
  }
}
