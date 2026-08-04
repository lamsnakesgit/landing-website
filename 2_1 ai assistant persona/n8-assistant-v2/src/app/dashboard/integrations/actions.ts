'use server'

import { redirect } from 'next/navigation'

export async function connectNango(provider: string, connectionId: string) {
  const publicKey = process.env.NEXT_PUBLIC_NANGO_PUBLIC_KEY || process.env.NANGO_PUBLIC_KEY || 'NANGO_PUBLIC_KEY_HERE';
  
  if (!publicKey || publicKey === 'NANGO_PUBLIC_KEY_HERE') {
    console.warn("Warning: NANGO_PUBLIC_KEY is not set in environment variables");
  }
  
  const url = `https://api.nango.dev/oauth/connect/${provider}?connection_id=${connectionId}&public_key=${publicKey}`;
  
  redirect(url);
}
