"use client";

import React, { useState } from 'react';
import { Logo } from '@/components/ui/logo';
import { BrandButton } from '@/components/ui/brand-button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { DiagnosisData } from '../diagnosis-assistant';
import { ArrowRight, FileText, AlertCircle } from 'lucide-react';

interface StepOneProps {
  diagnosisData: DiagnosisData;
  updateDiagnosisData: (data: Partial<DiagnosisData>) => void;
  onNext: () => void;
}

export function StepOne({ diagnosisData, updateDiagnosisData, onNext }: StepOneProps) {
  const [diagnosis, setDiagnosis] = useState(diagnosisData.diagnosis || '');
  const [error, setError] = useState('');

  const handleContinue = () => {
    if (!diagnosis.trim()) {
      setError('Please enter your diagnosis before continuing.');
      return;
    }
    
    if (diagnosis.trim().length < 10) {
      setError('Please provide a more detailed diagnosis (at least 10 characters).');
      return;
    }

    setError('');
    updateDiagnosisData({ diagnosis: diagnosis.trim() });
    onNext();
  };

  const handleDiagnosisChange = (value: string) => {
    setDiagnosis(value);
    if (error) setError('');
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-brand-gradient-from to-brand-gradient-to">
      {/* Header with Logo */}
      <header className="p-4 lg:p-8">
        <div className="container max-w-4xl">
          <Logo variant="hero" className="mb-4" />
          <div className="flex items-center gap-2 text-sm text-text-gray">
            <span className="px-2 py-1 bg-brand-teal text-white rounded-full text-xs font-medium">
              Step 1 of 4
            </span>
            <span>Diagnosis Analysis</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center p-4 lg:p-8">
        <div className="w-full max-w-2xl">
          <Card className="border-0 shadow-lg bg-white/95 backdrop-blur-sm">
            <CardHeader className="text-center pb-6">
              <div className="mx-auto mb-4 h-16 w-16 rounded-full bg-brand-teal/10 flex items-center justify-center">
                <FileText className="h-8 w-8 text-brand-teal" />
              </div>
              <CardTitle className="text-2xl lg:text-3xl font-bold text-text-dark mb-2">
                Tell us about your diagnosis
              </CardTitle>
              <p className="text-text-gray text-lg">
                Paste your medical diagnosis or describe your condition. Our AI will analyze it and connect you with the right specialists.
              </p>
            </CardHeader>
            
            <CardContent className="space-y-6">
              <div>
                <label htmlFor="diagnosis" className="block text-sm font-medium text-text-dark mb-2">
                  Medical Diagnosis or Condition *
                </label>
                <textarea
                  id="diagnosis"
                  rows={6}
                  value={diagnosis}
                  onChange={(e) => handleDiagnosisChange(e.target.value)}
                  placeholder="Paste your diagnosis here or describe your medical condition in detail. Include any relevant symptoms, test results, or medical history..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-brand-teal focus:border-transparent transition-colors"
                  aria-describedby={error ? 'diagnosis-error' : undefined}
                />
                <div className="mt-2 text-sm text-text-gray">
                  {diagnosis.length}/500 characters
                </div>
              </div>

              {error && (
                <div id="diagnosis-error" className="flex items-center gap-2 text-red-600 text-sm" role="alert">
                  <AlertCircle className="h-4 w-4 flex-shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              <div className="bg-teal-50 border border-teal-200 rounded-lg p-4">
                <h4 className="font-medium text-teal-900 mb-2">Privacy & Security</h4>
                <p className="text-sm text-teal-700">
                  Your medical information is encrypted and HIPAA-compliant. We automatically remove personal identifiers while preserving medical context.
                </p>
              </div>

              <div className="flex flex-col sm:flex-row gap-4 pt-4">
                <BrandButton 
                  onClick={handleContinue}
                  className="flex-1 h-12 text-base font-medium"
                  disabled={!diagnosis.trim()}
                >
                  Continue to Analysis
                  <ArrowRight className="ml-2 h-5 w-5" />
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
            <p>Secure • HIPAA Compliant • AI-Powered Specialist Matching</p>
          </div>
        </div>
      </footer>
    </div>
  );
}