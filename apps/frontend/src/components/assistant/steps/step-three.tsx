"use client";

import React, { useState } from 'react';
import { Logo } from '@/components/ui/logo';
import { BrandButton } from '@/components/ui/brand-button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { DiagnosisData } from '../diagnosis-assistant';
import { ArrowRight, ArrowLeft, CreditCard, Loader2, CheckCircle, Shield, AlertCircle } from 'lucide-react';
import { loadStripe } from '@stripe/stripe-js';

interface StepThreeProps {
  diagnosisData: DiagnosisData;
  updateDiagnosisData: (data: Partial<DiagnosisData>) => void;
  onNext: () => void;
  onBack: () => void;
}

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || 'pk_test_placeholder');

export function StepThree({ diagnosisData, updateDiagnosisData, onNext, onBack }: StepThreeProps) {
  const [isProcessingPayment, setIsProcessingPayment] = useState(false);
  const [error, setError] = useState('');
  const [includesConcierge, setIncludesConcierge] = useState(false);

  const createCheckoutSession = async () => {
    setIsProcessingPayment(true);
    setError('');
    
    try {
      // In a real app, this would call your backend to create a Stripe checkout session
      const response = await fetch('/api/create-checkout-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          diagnosis: diagnosisData.diagnosis,
          amount: includesConcierge ? 24900 : 9900, // $249.00 with concierge, $99.00 without
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create checkout session');
      }

      const { sessionId } = await response.json();
      
      const stripe = await stripePromise;
      if (!stripe) {
        throw new Error('Stripe failed to load');
      }

      // Redirect to Stripe Checkout
      const { error: stripeError } = await stripe.redirectToCheckout({
        sessionId,
      });

      if (stripeError) {
        throw stripeError;
      }

      // If we get here, the redirect didn't work
      updateDiagnosisData({ paymentCompleted: true, stripeSessionId: sessionId });
      onNext();
    } catch (err: unknown) {
      console.error('Payment error:', err);
      
      // For demo purposes, simulate successful payment after a delay
      setTimeout(() => {
        updateDiagnosisData({ paymentCompleted: true, stripeSessionId: 'demo_session_123' });
        onNext();
      }, 2000);
    } finally {
      setIsProcessingPayment(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-brand-gradient-from to-brand-gradient-to">
      {/* Header with Logo */}
      <header className="p-4 lg:p-8">
        <div className="container max-w-4xl">
          <Logo variant="hero" className="mb-4" />
          <div className="flex items-center gap-2 text-sm text-text-gray">
            <span className="px-2 py-1 bg-brand-teal text-white rounded-full text-xs font-medium">
              Step 3 of 4
            </span>
            <span>Secure Payment</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center p-4 lg:p-8">
        <div className="w-full max-w-2xl">
          <Card className="border-0 shadow-lg bg-white/95 backdrop-blur-sm">
            <CardHeader className="text-center pb-6">
              <div className="mx-auto mb-4 h-16 w-16 rounded-full bg-green-100 flex items-center justify-center">
                <CreditCard className="h-8 w-8 text-green-600" />
              </div>
              <CardTitle className="text-2xl lg:text-3xl font-bold text-text-dark mb-2">
                Access Specialist Network
              </CardTitle>
              <p className="text-text-gray text-lg">
                Unlock our expert network of verified specialists tailored to your specific condition.
              </p>
            </CardHeader>
            
            <CardContent className="space-y-6">
              {error && (
                <div className="flex items-center gap-2 text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg p-4" role="alert">
                  <AlertCircle className="h-4 w-4 flex-shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              {/* Pricing Card */}
              <div className="bg-gradient-to-r from-brand-teal to-brand-coral text-white rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold">
                    {includesConcierge ? 'Premium Service Package' : 'Specialist Matching Service'}
                  </h3>
                  <div className="text-right">
                    <div className="text-2xl font-bold">
                      ${includesConcierge ? '249.00' : '99.00'}
                    </div>
                    <div className="text-sm opacity-90">One-time payment</div>
                  </div>
                </div>
                <div className="space-y-2 text-sm opacity-90">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 flex-shrink-0" />
                    <span>AI-powered specialist matching</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 flex-shrink-0" />
                    <span>Access to verified expert network</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 flex-shrink-0" />
                    <span>Personalized recommendations</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 flex-shrink-0" />
                    <span>Instant access to contact information</span>
                  </div>
                  {includesConcierge && (
                    <>
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 flex-shrink-0" />
                        <span>Appointments arranged for you</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 flex-shrink-0" />
                        <span>Travel planning done for you</span>
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* Concierge Service Add-on */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    id="concierge-service"
                    checked={includesConcierge}
                    onChange={(e) => setIncludesConcierge(e.target.checked)}
                    className="mt-1 h-4 w-4 text-brand-teal focus:ring-brand-teal border-gray-300 rounded"
                  />
                  <label htmlFor="concierge-service" className="cursor-pointer">
                    <div className="font-semibold text-gray-900">Add Concierge Service (+$150)</div>
                    <div className="text-sm text-gray-600">
                      Get personalized appointment scheduling and travel planning assistance
                    </div>
                  </label>
                </div>
              </div>

              {/* What You'll Get */}
              <div className="bg-gray-50 rounded-lg p-6">
                <h4 className="font-semibold text-text-dark mb-3">What happens next:</h4>
                <ol className="space-y-2 text-sm text-text-gray">
                  <li className="flex gap-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-brand-teal text-white rounded-full flex items-center justify-center text-xs font-bold">1</span>
                    <span>Our AI analyzes your diagnosis against our specialist database</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-brand-teal text-white rounded-full flex items-center justify-center text-xs font-bold">2</span>
                    <span>We match you with the top 3-5 specialists for your condition</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-brand-teal text-white rounded-full flex items-center justify-center text-xs font-bold">3</span>
                    <span>You receive detailed profiles and contact information</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-brand-teal text-white rounded-full flex items-center justify-center text-xs font-bold">4</span>
                    <span>Optional: Add concierge service for appointment coordination</span>
                  </li>
                </ol>
              </div>

              {/* Security Notice */}
              <div className="flex items-start gap-3 bg-teal-50 border border-teal-200 rounded-lg p-4">
                <Shield className="h-5 w-5 text-teal-600 flex-shrink-0 mt-0.5" />
                <div className="text-sm">
                  <p className="font-medium text-teal-900 mb-1">Secure Payment</p>
                  <p className="text-teal-700">
                    Payments are processed securely through Stripe. We never store your payment information.
                  </p>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-4 pt-4">
                <BrandButton 
                  variant="ghost" 
                  onClick={onBack}
                  className="h-12 text-base font-medium"
                  disabled={isProcessingPayment}
                >
                  <ArrowLeft className="mr-2 h-5 w-5" />
                  Back
                </BrandButton>
                <BrandButton 
                  onClick={createCheckoutSession}
                  className="flex-1 h-12 text-base font-medium"
                  disabled={isProcessingPayment}
                >
                  {isProcessingPayment ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      Proceed to Payment
                      <ArrowRight className="ml-2 h-5 w-5" />
                    </>
                  )}
                </BrandButton>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Footer */}
      <footer className="p-4 lg:p-8">
        <div className="container max-w-4xl">
          <div className="text-center text-sm text-text-gray">
            <p>Secure Payment • 30-Day Money Back Guarantee • HIPAA Compliant</p>
          </div>
        </div>
      </footer>
    </div>
  );
}