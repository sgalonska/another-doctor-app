import { MainLayout } from "@/components/layout/main-layout";
import { Hero } from "@/components/sections/hero";
import { BrandButton } from "@/components/ui/brand-button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";
import { CheckCircle, Shield, Zap, Users, Database, BarChart } from "lucide-react";

export default function Home() {
  return (
    <MainLayout headerVariant="transparent">
      {/* Hero Section */}
      <Hero />

      {/* How It Works Section */}
      <section className="py-16 lg:py-24">
        <div className="container">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-text-dark mb-4">
              How Another Doctor Works
            </h2>
            <p className="text-lg text-text-gray max-w-2xl mx-auto">
              Our evidence-based platform connects you with the right specialists through 
              advanced AI analysis and transparent scoring.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <ProcessCard
              step="1"
              title="Upload & Analyze"
              description="Securely upload patient cases with automatic PHI de-identification and medical entity extraction using advanced NLP."
              icon={<Shield className="h-6 w-6" />}
            />
            <ProcessCard
              step="2"
              title="Smart Matching"
              description="AI-powered specialist matching using hybrid vector search, publication analysis, and clinical trial data."
              icon={<Zap className="h-6 w-6" />}
            />
            <ProcessCard
              step="3"
              title="Expert Connection"
              description="Connect with verified specialists backed by research publications, grant funding, and institutional affiliations."
              icon={<Users className="h-6 w-6" />}
            />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 lg:py-24 bg-bg-light">
        <div className="container">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-text-dark mb-4">
              Powered by Evidence-Based Medicine
            </h2>
            <p className="text-lg text-text-gray max-w-2xl mx-auto">
              Our platform integrates multiple data sources to provide transparent, 
              reliable specialist recommendations.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard
              title="HIPAA Compliant"
              description="Enterprise-grade security with automatic PHI de-identification and encryption."
              icon={<Shield className="h-8 w-8 text-brand-teal" />}
            />
            <FeatureCard
              title="Real-Time Analysis"
              description="Instant case processing with medical entity extraction and condition classification."
              icon={<Zap className="h-8 w-8 text-brand-coral" />}
            />
            <FeatureCard
              title="Global Network"
              description="Access to specialists worldwide with verified expertise and institutional affiliations."
              icon={<Users className="h-8 w-8 text-brand-teal" />}
            />
            <FeatureCard
              title="Data Integration"
              description="PubMed, ClinicalTrials.gov, NIH RePORTER, and OpenAlex data sources."
              icon={<Database className="h-8 w-8 text-brand-coral" />}
            />
            <FeatureCard
              title="Outcome Tracking"
              description="Monitor consultation outcomes and improve matching accuracy over time."
              icon={<BarChart className="h-8 w-8 text-brand-teal" />}
            />
            <FeatureCard
              title="Quality Assurance"
              description="Evidence-based scoring with transparent methodology and audit trails."
              icon={<CheckCircle className="h-8 w-8 text-brand-coral" />}
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 lg:py-24">
        <div className="container">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-text-dark mb-4">
              Ready to Find the Right Specialist?
            </h2>
            <p className="text-lg text-text-gray mb-8 max-w-2xl mx-auto">
              Join healthcare professionals worldwide who trust Another Doctor 
              for evidence-based specialist matching.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/get-started">
                <BrandButton size="lg">Start Free Trial</BrandButton>
              </Link>
              <Link href="/contact">
                <BrandButton variant="outline" size="lg">Contact Sales</BrandButton>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </MainLayout>
  );
}

interface ProcessCardProps {
  step: string;
  title: string;
  description: string;
  icon: React.ReactNode;
}

function ProcessCard({ step, title, description, icon }: ProcessCardProps) {
  return (
    <div className="text-center">
      <div className="relative mb-6">
        <div className="mx-auto h-16 w-16 rounded-full bg-brand-teal text-white flex items-center justify-center text-xl font-bold">
          {step}
        </div>
        <div className="absolute -top-2 -right-2 h-8 w-8 rounded-full bg-white shadow-sm flex items-center justify-center text-brand-teal">
          {icon}
        </div>
      </div>
      <h3 className="text-xl font-semibold text-text-dark mb-3">{title}</h3>
      <p className="text-text-gray">{description}</p>
    </div>
  );
}

interface FeatureCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
}

function FeatureCard({ title, description, icon }: FeatureCardProps) {
  return (
    <Card className="border-0 shadow-sm hover:shadow-md transition-shadow">
      <CardContent className="p-6">
        <div className="mb-4">{icon}</div>
        <h3 className="text-lg font-semibold text-text-dark mb-2">{title}</h3>
        <p className="text-text-gray">{description}</p>
      </CardContent>
    </Card>
  );
}