// src/app/api/get-model-files/route.js
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    console.log('🔗 API Route: Fetching model files from server at http://localhost:8001/get-model-files');
    
    const res = await fetch('http://localhost:8001/get-model-files');
    console.log('📡 Server response status:', res.status, res.statusText);
    
    if (!res.ok) {
      console.error('❌ API Route: Failed to fetch model files from server');
      console.error('❌ Server response:', await res.text());
      return NextResponse.json([]);
    }
    
    const files = await res.json();
    console.log('📁 API Route: Received files from server:', files);
    console.log('📁 API Route: Files type:', typeof files);
    console.log('📁 API Route: Files array?', Array.isArray(files));
    console.log('📁 API Route: Files length:', files?.length);
    
    console.log('✅ API Route: Returning files to frontend');
    return NextResponse.json(files);
  } catch (error) {
    console.error('💥 API Route: Error fetching model files:', error);
    return NextResponse.json([]);
  }
}
