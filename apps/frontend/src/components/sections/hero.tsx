import React from 'react';
import Link from 'next/link';
import { ArrowRight, Upload, Search, Users } from 'lucide-react';
import { CTAButton, BrandButton } from '@/components/ui/brand-button';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface HeroProps {
  className?: string;
}

export function Hero({ className }: HeroProps) {
  return (
    <section className={cn(
      'relative overflow-hidden bg-brand-gradient py-20 lg:py-32',
      className
    )}>
      {/* Background decoration */}
      <div className="absolute inset-0 bg-grid-white/[0.02] bg-grid-16" />
      <div className="absolute inset-0 bg-gradient-to-t from-white/80 via-transparent to-transparent" />
      
      <div className="container relative">
        <div className="mx-auto max-w-4xl text-center">
          {/* Main heading */}
          <h1 className="mb-6 text-4xl font-bold leading-tight text-text-dark sm:text-5xl lg:text-6xl">
            AI-Powered{' '}
            <span className="text-brand-teal">Specialist Matching</span>{' '}
            for Complex Medical Cases
          </h1>
          
          {/* Subtitle */}
          <p className="mb-8 text-lg text-text-gray sm:text-xl lg:text-2xl">
            Connect healthcare professionals with the right specialists using evidence-based 
            scoring and intelligent case analysis. Improve patient outcomes with data-driven recommendations.
          </p>

          {/* CTA buttons */}
          <div className="mb-12 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <CTAButton asChild>
              <Link href="/get-started">
                Get Started Free
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </CTAButton>
            
            <BrandButton variant="outline" asChild>
              <Link href="/demo">
                Watch Demo
              </Link>
            </BrandButton>
          </div>

          {/* Trust indicators */}
          <div className="mb-16 text-sm text-text-gray">
            <p>Trusted by healthcare professionals worldwide</p>
          </div>
        </div>

        {/* Feature cards */}
        <div className="mx-auto max-w-6xl">
          <div className="grid gap-8 md:grid-cols-3">
            <FeatureCard
              icon={<Upload className="h-8 w-8 text-brand-teal" />}
              title="Upload & Analyze"
              description="Securely upload patient cases with automatic PHI de-identification and medical entity extraction."
            />
            <FeatureCard
              icon={<Search className="h-8 w-8 text-brand-coral" />}
              title="Smart Matching"
              description="AI-powered specialist matching using hybrid vector search and evidence-based scoring algorithms."
            />
            <FeatureCard
              icon={<Users className="h-8 w-8 text-brand-teal" />}
              title="Expert Network"
              description="Connect with verified specialists worldwide, backed by publication history and clinical expertise."
            />
          </div>
        </div>
      </div>
    </section>
  );
}

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  className?: string;
}

function FeatureCard({ icon, title, description, className }: FeatureCardProps) {
  return (
    <Card className={cn(
      'border-0 bg-white/60 backdrop-blur-sm transition-all duration-300 hover:bg-white/80 hover:shadow-lg',
      className
    )}>
      <CardContent className="p-6 text-center">
        <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-full bg-white shadow-sm">
          {icon}
        </div>
        <h3 className="mb-2 text-lg font-semibold text-text-dark">{title}</h3>
        <p className="text-text-gray">{description}</p>
      </CardContent>
    </Card>
  );
}