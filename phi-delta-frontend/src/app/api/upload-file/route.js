// src/app/api/upload-file/route.js
import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    // Get the form data from the request
    const formData = await request.formData();
    
    // Forward the form data to the FastAPI backend
    const res = await fetch('http://localhost:8001/upload-file', {
      method: 'POST',
      body: formData, // Forward the FormData directly
    });
    
    if (!res.ok) {
      const errorText = await res.text();
      console.error('Backend upload error:', errorText);
      return NextResponse.json(
        { status: 'error', message: 'Backend upload failed' }, 
        { status: 500 }
      );
    }
    
    const result = await res.json();
    return NextResponse.json(result);
    
  } catch (error) {
    console.error('Upload API error:', error);
    return NextResponse.json(
      { status: 'error', message: 'Upload failed' }, 
      { status: 500 }
    );
  }
}
