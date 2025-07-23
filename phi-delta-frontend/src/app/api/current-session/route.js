// src/app/api/current-session/route.js
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const res = await fetch('http://localhost:8001/current-session', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    
    if (!res.ok) {
      return NextResponse.json({ session_id: null, has_session: false }, { status: 500 });
    }
    
    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching current session:', error);
    return NextResponse.json({ session_id: null, has_session: false }, { status: 500 });
  }
}
