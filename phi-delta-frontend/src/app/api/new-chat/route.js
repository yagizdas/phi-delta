// src/app/api/chat/route.js
import { NextResponse } from 'next/server';

export async function POST() {
  try {
    // Use environment variable for backend URL
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8001';

    // Send POST request to the backend
    const res = await fetch(`${backendUrl}/new-chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });

    // Check if the response is OK
    if (!res.ok) {
      const errorMessage = await res.text(); // Get error message from backend
      console.error('Backend error:', errorMessage);
      return NextResponse.json({ reply: `Backend error: ${errorMessage}` }, { status: res.status });
    }

    // Parse backend response
    const data = await res.json();
    return NextResponse.json({ reply: data.reply || 'Success, new chat started!' });
  } catch (error) {
    // Handle unexpected errors (e.g., network issues)
    console.error('Error communicating with backend:', error);
    return NextResponse.json({ reply: 'Unexpected error occurred' }, { status: 500 });
  }
}