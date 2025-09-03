import { Router } from '@cloudflare/itty-router';

export interface Env {
  UPLOADS_BUCKET: R2Bucket;
  CACHE: KVNamespace;
  R2_ACCESS_KEY_ID: string;
  R2_SECRET_ACCESS_KEY: string;
  BACKEND_API_URL: string;
  STRIPE_WEBHOOK_SECRET: string;
  ENVIRONMENT: string;
}

const router = Router();

// Health check
router.get('/health', () => {
  return new Response(JSON.stringify({ status: 'healthy', timestamp: new Date().toISOString() }), {
    headers: { 'Content-Type': 'application/json' }
  });
});

// Generate presigned URL for R2 uploads
router.post('/upload/presigned-url', async (request, env: Env) => {
  try {
    const body = await request.json() as { filename: string; contentType: string };
    const { filename, contentType } = body;

    if (!filename || !contentType) {
      return new Response(JSON.stringify({ error: 'Filename and contentType required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Generate unique key for the file
    const key = `uploads/${crypto.randomUUID()}/${filename}`;
    const expiresIn = 3600; // 1 hour

    // Create presigned URL for PUT operation
    const url = await env.UPLOADS_BUCKET.createSignedUrl(key, {
      method: 'PUT',
      expires: Math.floor(Date.now() / 1000) + expiresIn,
      headers: {
        'Content-Type': contentType,
      }
    });

    return new Response(JSON.stringify({
      uploadUrl: url,
      key: key,
      expiresIn: expiresIn
    }), {
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('Error generating presigned URL:', error);
    return new Response(JSON.stringify({ error: 'Failed to generate presigned URL' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
});

// Handle Stripe webhooks
router.post('/webhooks/stripe', async (request, env: Env) => {
  try {
    const signature = request.headers.get('stripe-signature');
    if (!signature) {
      return new Response('Missing signature', { status: 400 });
    }

    const body = await request.text();
    
    // Verify webhook signature (simplified - use proper Stripe verification in production)
    // const event = stripe.webhooks.constructEvent(body, signature, env.STRIPE_WEBHOOK_SECRET);

    // Forward to backend for processing
    const response = await fetch(`${env.BACKEND_API_URL}/webhooks/stripe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Stripe-Signature': signature
      },
      body: body
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    return new Response('OK');
  } catch (error) {
    console.error('Stripe webhook error:', error);
    return new Response('Webhook error', { status: 400 });
  }
});

// CORS preflight
router.options('*', () => {
  return new Response(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Max-Age': '86400',
    }
  });
});

// Handle all other requests
router.all('*', () => {
  return new Response('Not Found', { status: 404 });
});

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const response = await router.handle(request, env, ctx);
    
    // Add CORS headers to all responses
    response.headers.set('Access-Control-Allow-Origin', '*');
    response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    
    return response;
  }
};