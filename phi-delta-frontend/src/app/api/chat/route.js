// src/app/api/chat/route.js
import { NextResponse } from 'next/server';

export async function POST(request) {
  const { message } = await request.json();
  const res = await fetch('http://localhost:8001/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) {
    return NextResponse.json({ reply: 'Backend error' }, { status: 500 });
  }
  const { reply } = await res.json();
  return NextResponse.json({ reply });
}
