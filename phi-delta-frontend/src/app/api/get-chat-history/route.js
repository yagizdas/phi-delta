// src/app/api/get-chat-history/route.js
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    console.log('Fetching thinking steps from Python server...');
    const res = await fetch('http://localhost:8001/get-chat-history');
    
    if (!res.ok) {
      console.log('Python server responded with error:', res.status);
      return NextResponse.json([], { status: 200 }); // Return empty array if not available
    }
    
    const text = await res.text();
    console.log('Raw response from Python server:', text);
    
    let steps;
    try {
      steps = JSON.parse(text);
      console.log('Parsed steps:', steps);
    } catch (parseError) {
      console.error('Failed to parse JSON:', parseError);
      return NextResponse.json([], { status: 200 });
    }
    
    return NextResponse.json(steps);
  } catch (error) {
    console.error('Error fetching thinking steps:', error);
    return NextResponse.json([], { status: 200 }); // Return empty array on error
  }
}
