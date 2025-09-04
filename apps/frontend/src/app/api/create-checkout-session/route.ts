import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || '', {
  apiVersion: '2023-10-16',
});

export async function POST(request: NextRequest) {
  try {
    const { diagnosis, amount } = await request.json();

    if (!diagnosis) {
      return NextResponse.json({ error: 'Diagnosis is required' }, { status: 400 });
    }

    const session = await stripe.checkout.sessions.create({
      mode: 'payment',
      payment_method_types: ['card'],
      line_items: [
        {
          price_data: {
            currency: 'usd',
            product_data: {
              name: 'Another Doctor - Specialist Matching Service',
              description: 'AI-powered specialist matching for your medical condition',
            },
            unit_amount: amount || 9900, // Default $99.00
          },
          quantity: 1,
        },
      ],
      success_url: `${request.nextUrl.origin}/?step=4&payment_success=true&session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${request.nextUrl.origin}/?step=3&payment_canceled=true`,
      metadata: {
        diagnosis: diagnosis.substring(0, 500), // Stripe metadata limit
      },
    });

    return NextResponse.json({ sessionId: session.id });
  } catch (error: unknown) {
    console.error('Stripe error:', error);
    return NextResponse.json(
      { error: 'Failed to create checkout session' },
      { status: 500 }
    );
  }
}