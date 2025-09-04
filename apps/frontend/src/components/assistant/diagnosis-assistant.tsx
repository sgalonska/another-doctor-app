"use client";

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { StepOne } from './steps/step-one';
import { StepTwo } from './steps/step-two';
import { StepThree } from './steps/step-three';
import { StepFour } from './steps/step-four';

export interface DiagnosisData {
  diagnosis: string;
  processedDiagnosis?: string;
  pdfGenerated?: boolean;
  paymentCompleted?: boolean;
  stripeSessionId?: string;
}

export function DiagnosisAssistant() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [currentStep, setCurrentStep] = useState<1 | 2 | 3 | 4>(1);
  const [diagnosisData, setDiagnosisData] = useState<DiagnosisData>({
    diagnosis: '',
  });

  // Initialize step from URL params
  useEffect(() => {
    const step = searchParams.get('step');
    const paymentSuccess = searchParams.get('payment_success');
    const sessionId = searchParams.get('session_id');
    
    if (paymentSuccess === 'true' && sessionId) {
      // Coming back from successful Stripe payment
      setCurrentStep(4);
      updateDiagnosisData({ 
        paymentCompleted: true, 
        stripeSessionId: sessionId 
      });
    } else if (step) {
      const stepNumber = parseInt(step) as 1 | 2 | 3 | 4;
      if (stepNumber >= 1 && stepNumber <= 4) {
        // Validate step progression
        const savedData = localStorage.getItem('diagnosis-data');
        let canAccessStep = stepNumber === 1;
        
        if (savedData) {
          try {
            const data = JSON.parse(savedData);
            // Allow step 2 if diagnosis exists
            if (stepNumber === 2 && data.diagnosis) canAccessStep = true;
            // Allow step 3 if processed diagnosis exists
            if (stepNumber === 3 && data.processedDiagnosis) canAccessStep = true;
            // Allow step 4 if payment completed
            if (stepNumber === 4 && data.paymentCompleted) canAccessStep = true;
          } catch (e) {
            // Invalid data, stay on step 1
          }
        }
        
        setCurrentStep(canAccessStep ? stepNumber : 1);
      }
    }

    // Load data from localStorage if available
    const savedData = localStorage.getItem('diagnosis-data');
    if (savedData) {
      try {
        setDiagnosisData(JSON.parse(savedData));
      } catch (e) {
        // Invalid data, clear it
        localStorage.removeItem('diagnosis-data');
      }
    }
  }, [searchParams]);

  // Update URL and localStorage when step changes
  const goToStep = (step: 1 | 2 | 3 | 4) => {
    setCurrentStep(step);
    router.push(`/?step=${step}`, { scroll: false });
  };

  const updateDiagnosisData = (data: Partial<DiagnosisData>) => {
    setDiagnosisData(prev => {
      const newData = { ...prev, ...data };
      // Save to localStorage for persistence
      localStorage.setItem('diagnosis-data', JSON.stringify(newData));
      return newData;
    });
  };

  return (
    <div className="min-h-screen bg-bg-light">
      {currentStep === 1 && (
        <StepOne
          diagnosisData={diagnosisData}
          updateDiagnosisData={updateDiagnosisData}
          onNext={() => goToStep(2)}
        />
      )}
      {currentStep === 2 && (
        <StepTwo
          diagnosisData={diagnosisData}
          updateDiagnosisData={updateDiagnosisData}
          onNext={() => goToStep(3)}
          onBack={() => goToStep(1)}
        />
      )}
      {currentStep === 3 && (
        <StepThree
          diagnosisData={diagnosisData}
          updateDiagnosisData={updateDiagnosisData}
          onNext={() => goToStep(4)}
          onBack={() => goToStep(2)}
        />
      )}
      {currentStep === 4 && (
        <StepFour
          onBack={() => goToStep(3)}
        />
      )}
    </div>
  );
}