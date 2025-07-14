// src/app/api/get-final-result/route.js
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const res = await fetch('http://localhost:8001/get-final-result');
    if (!res.ok) {
      return NextResponse.json({ result: null });
    }
    const result = await res.json();
    return NextResponse.json(result);
  } catch (error) {
    console.error('Error fetching final result:', error);
    return NextResponse.json({ result: null });
  }
}
