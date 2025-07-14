// src/app/api/get-processing-status/route.js
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const res = await fetch('http://localhost:8001/get-processing-status');
    if (!res.ok) {
      return NextResponse.json({ is_processing: false, has_result: false });
    }
    const status = await res.json();
    return NextResponse.json(status);
  } catch (error) {
    console.error('Error fetching processing status:', error);
    return NextResponse.json({ is_processing: false, has_result: false });
  }
}
