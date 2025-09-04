"use client";

import React, { useState, useEffect } from 'react';
import { Logo } from '@/components/ui/logo';
import { BrandButton } from '@/components/ui/brand-button';
import { Card, CardContent } from '@/components/ui/card';
import { ArrowLeft, Star, MapPin, Phone, Mail, Calendar, CheckCircle, Loader2, AlertCircle, Users, Shield } from 'lucide-react';

interface StepFourProps {
  onBack: () => void;
}

interface Doctor {
  id: string;
  name: string;
  specialty: string;
  institution: string;
  location: string;
  rating: number;
  experience: number;
  email: string;
  phone: string;
  matchScore: number;
  reasons: string[];
  publications: number;
  availability: string;
}

export function StepFour({ onBack }: StepFourProps) {
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [conciergeSelected, setConciergeSelected] = useState(false);
  const [isProcessingConcierge, setIsProcessingConcierge] = useState(false);
  const [error, setError] = useState('');
  const [copiedItem, setCopiedItem] = useState<string | null>(null);

  useEffect(() => {
    fetchRecommendedDoctors();
  }, []);

  const fetchRecommendedDoctors = async () => {
    setIsLoading(true);
    
    try {
      // Simulate API call to get recommended doctors
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const mockDoctors: Doctor[] = [
        {
          id: '1',
          name: 'Dr. Sarah Chen',
          specialty: 'Oncology',
          institution: 'Stanford Medical Center',
          location: 'Palo Alto, CA',
          rating: 4.9,
          experience: 15,
          email: 'schen@stanford.edu',
          phone: '(650) 498-4000',
          matchScore: 95,
          reasons: [
            'Specialist in rare oncological conditions',
            '120+ publications in relevant field',
            'Leading clinical trial researcher',
            'Excellent patient outcomes'
          ],
          publications: 120,
          availability: 'Next available: 2 weeks'
        },
        {
          id: '2',
          name: 'Dr. Michael Rodriguez',
          specialty: 'Internal Medicine & Oncology',
          institution: 'Mayo Clinic',
          location: 'Rochester, MN',
          rating: 4.8,
          experience: 22,
          email: 'rodriguez.michael@mayo.edu',
          phone: '(507) 284-2511',
          matchScore: 92,
          reasons: [
            'Dual board certification',
            'Internationally recognized expert',
            '200+ peer-reviewed publications',
            'Head of oncology department'
          ],
          publications: 200,
          availability: 'Next available: 3 weeks'
        },
        {
          id: '3',
          name: 'Dr. Emily Watson',
          specialty: 'Radiation Oncology',
          institution: 'MD Anderson Cancer Center',
          location: 'Houston, TX',
          rating: 4.7,
          experience: 18,
          email: 'ewatson@mdanderson.org',
          phone: '(713) 792-2121',
          matchScore: 88,
          reasons: [
            'Pioneer in precision radiation therapy',
            'Active in clinical research',
            'Excellent bedside manner',
            'Advanced treatment protocols'
          ],
          publications: 85,
          availability: 'Next available: 1 week'
        }
      ];
      
      setDoctors(mockDoctors);
    } catch (err) {
      setError('Failed to load doctor recommendations. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const isMobile = () => {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  };

  const copyToClipboard = async (text: string, type: 'phone' | 'email') => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedItem(`${type}-${text}`);
      setTimeout(() => setCopiedItem(null), 2000); // Clear after 2 seconds
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const handlePhoneClick = (phone: string) => {
    if (isMobile()) {
      window.open(`tel:${phone}`, '_self');
    } else {
      copyToClipboard(phone, 'phone');
    }
  };

  const handleEmailClick = (email: string) => {
    copyToClipboard(email, 'email');
  };

  const handleConciergeService = async () => {
    setIsProcessingConcierge(true);
    
    try {
      // Simulate payment processing for concierge service
      await new Promise(resolve => setTimeout(resolve, 2000));
      setConciergeSelected(true);
    } catch (err) {
      setError('Failed to process concierge service. Please try again.');
    } finally {
      setIsProcessingConcierge(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-brand-gradient-from to-brand-gradient-to">
      {/* Header with Logo */}
      <header className="p-4 lg:p-8">
        <div className="container max-w-6xl">
          <Logo variant="hero" className="mb-4" />
          <div className="flex items-center gap-2 text-sm text-text-gray">
            <span className="px-2 py-1 bg-brand-teal text-white rounded-full text-xs font-medium">
              Step 4 of 4
            </span>
            <span>Specialist Recommendations</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 p-4 lg:p-8">
        <div className="container max-w-6xl">
          <div className="text-center mb-8">
            <h1 className="text-2xl lg:text-3xl font-bold text-text-dark mb-2">
              Your Recommended Specialists
            </h1>
            <p className="text-text-gray text-lg">
              Based on your diagnosis, we&apos;ve found the top specialists who can help you.
            </p>
          </div>

          {error && (
            <div className="flex items-center gap-2 text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg p-4 mb-6" role="alert">
              <AlertCircle className="h-4 w-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {isLoading ? (
            <div className="text-center py-12">
              <Loader2 className="h-12 w-12 text-brand-teal animate-spin mx-auto mb-4" />
              <h3 className="text-lg font-medium text-text-dark mb-2">Finding Your Perfect Match</h3>
              <p className="text-text-gray">Analyzing thousands of specialists to find the best fit for your condition...</p>
            </div>
          ) : (
            <>
              {/* Doctor Cards */}
              <div className="grid gap-6 mb-8">
                {doctors.map((doctor, index) => (
                  <Card key={doctor.id} className="border-0 shadow-lg bg-white/95 backdrop-blur-sm">
                    <CardContent className="p-6">
                      <div className="flex flex-col lg:flex-row gap-6">
                        {/* Doctor Info */}
                        <div className="flex-1">
                          <div className="flex items-start justify-between mb-4">
                            <div>
                              <div className="flex items-center gap-2 mb-1">
                                <h3 className="text-xl font-bold text-text-dark">{doctor.name}</h3>
                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                  index === 0 ? 'bg-green-100 text-green-800' :
                                  index === 1 ? 'bg-coral-100 text-coral-800' :
                                  'bg-orange-100 text-orange-800'
                                }`}>
                                  {index === 0 ? 'Top Match' : index === 1 ? 'Excellent Match' : 'Great Match'}
                                </span>
                              </div>
                              <p className="text-brand-teal font-medium">{doctor.specialty}</p>
                              <p className="text-text-gray">{doctor.institution}</p>
                            </div>
                            <div className="text-right">
                              <div className="text-2xl font-bold text-brand-teal mb-1">{doctor.matchScore}%</div>
                              <div className="text-sm text-text-gray">Match Score</div>
                            </div>
                          </div>

                          <div className="grid md:grid-cols-2 gap-4 mb-4">
                            <div className="flex items-center gap-2 text-sm text-text-gray">
                              <MapPin className="h-4 w-4" />
                              <span>{doctor.location}</span>
                            </div>
                            <div className="flex items-center gap-2 text-sm text-text-gray">
                              <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                              <span>{doctor.rating}/5.0 • {doctor.experience} years experience</span>
                            </div>
                            <div className="flex items-center gap-2 text-sm text-text-gray">
                              <Calendar className="h-4 w-4" />
                              <span>{doctor.availability}</span>
                            </div>
                            <div className="flex items-center gap-2 text-sm text-text-gray">
                              <CheckCircle className="h-4 w-4" />
                              <span>{doctor.publications} publications</span>
                            </div>
                          </div>

                          <div className="mb-4">
                            <h4 className="font-medium text-text-dark mb-2">Why this specialist is perfect for you:</h4>
                            <ul className="space-y-1">
                              {doctor.reasons.map((reason, idx) => (
                                <li key={idx} className="flex items-start gap-2 text-sm text-text-gray">
                                  <CheckCircle className="h-4 w-4 text-green-600 flex-shrink-0 mt-0.5" />
                                  <span>{reason}</span>
                                </li>
                              ))}
                            </ul>
                          </div>

                          <div className="flex flex-col sm:flex-row gap-3">
                            <BrandButton 
                              onClick={() => handlePhoneClick(doctor.phone)}
                              variant="ghost-filled"
                              className="flex-1"
                            >
                              <Phone className="mr-2 h-4 w-4" />
                              {copiedItem === `phone-${doctor.phone}` ? 'Copied!' : 
                                isMobile() ? `Call ${doctor.phone}` : `Copy ${doctor.phone}`
                              }
                            </BrandButton>
                            <BrandButton 
                              onClick={() => handleEmailClick(doctor.email)}
                              variant="ghost-filled" 
                              className="flex-1"
                            >
                              <Mail className="mr-2 h-4 w-4" />
                              {copiedItem === `email-${doctor.email}` ? 'Copied!' : `Copy ${doctor.email}`}
                            </BrandButton>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* Privacy Notice */}
              <Card className="border-0 shadow-lg bg-green-50 border-green-200">
                <CardContent className="p-6">
                  <div className="flex items-start gap-4">
                    <div className="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                      <Shield className="h-6 w-6 text-green-600" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-green-900 mb-2">Your Privacy is Protected</h4>
                      <p className="text-sm text-green-700 mb-2">
                        <strong>Your medical data has been successfully and completely removed from our files.</strong> We maintain strict privacy standards to protect your sensitive information.
                      </p>
                      <p className="text-sm text-green-700">
                        We are keeping your specialist matches for another 7 days for your convenience, after which they will be automatically deleted from our systems.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Concierge Service */}
              <Card className="border-0 shadow-lg bg-gradient-to-r from-brand-coral to-brand-teal text-white">
                <CardContent className="p-8">
                  <div className="flex items-center gap-4 mb-6">
                    <div className="h-16 w-16 rounded-full bg-white/20 flex items-center justify-center">
                      <Users className="h-8 w-8" />
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold mb-2">Concierge Service</h3>
                      <p className="opacity-90">Let our team handle the appointments for you</p>
                    </div>
                    <div className="ml-auto text-right">
                      <div className="text-3xl font-bold">$199</div>
                      <div className="text-sm opacity-90">One-time fee</div>
                    </div>
                  </div>

                  {!conciergeSelected ? (
                    <>
                      <div className="grid md:grid-cols-2 gap-6 mb-6">
                        <div>
                          <h4 className="font-semibold mb-3">What&apos;s included:</h4>
                          <ul className="space-y-2 text-sm opacity-90">
                            <li className="flex items-center gap-2">
                              <CheckCircle className="h-4 w-4 flex-shrink-0" />
                              <span>We call hospitals and clinics for you</span>
                            </li>
                            <li className="flex items-center gap-2">
                              <CheckCircle className="h-4 w-4 flex-shrink-0" />
                              <span>Coordinate appointment scheduling</span>
                            </li>
                            <li className="flex items-center gap-2">
                              <CheckCircle className="h-4 w-4 flex-shrink-0" />
                              <span>Handle insurance verification</span>
                            </li>
                            <li className="flex items-center gap-2">
                              <CheckCircle className="h-4 w-4 flex-shrink-0" />
                              <span>Arrange medical record transfers</span>
                            </li>
                          </ul>
                        </div>
                        <div>
                          <h4 className="font-semibold mb-3">Transportation assistance:</h4>
                          <ul className="space-y-2 text-sm opacity-90">
                            <li className="flex items-center gap-2">
                              <CheckCircle className="h-4 w-4 flex-shrink-0" />
                              <span>Help find suitable transportation</span>
                            </li>
                            <li className="flex items-center gap-2">
                              <CheckCircle className="h-4 w-4 flex-shrink-0" />
                              <span>Medical transport coordination</span>
                            </li>
                            <li className="flex items-center gap-2">
                              <CheckCircle className="h-4 w-4 flex-shrink-0" />
                              <span>Travel planning for out-of-state specialists</span>
                            </li>
                            <li className="flex items-center gap-2">
                              <CheckCircle className="h-4 w-4 flex-shrink-0" />
                              <span>Accommodation recommendations</span>
                            </li>
                          </ul>
                        </div>
                      </div>

                      <BrandButton 
                        onClick={handleConciergeService}
                        disabled={isProcessingConcierge}
                        className="bg-white text-brand-teal hover:bg-white/90 w-full sm:w-auto"
                      >
                        {isProcessingConcierge ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Processing...
                          </>
                        ) : (
                          'Add Concierge Service - $199'
                        )}
                      </BrandButton>
                    </>
                  ) : (
                    <div className="text-center py-4">
                      <CheckCircle className="h-12 w-12 mx-auto mb-3" />
                      <h4 className="text-xl font-bold mb-2">Concierge Service Added!</h4>
                      <p className="opacity-90 mb-4">Our team will contact you within 24 hours to begin coordinating your appointments.</p>
                      <p className="text-sm opacity-75">You&apos;ll receive a confirmation email with your concierge coordinator&apos;s contact information.</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Back Button */}
              <div className="flex justify-center mt-8">
                <BrandButton 
                  variant="ghost-filled" 
                  onClick={onBack}
                  className="bg-white/90 text-text-dark hover:bg-white"
                >
                  <ArrowLeft className="mr-2 h-5 w-5" />
                  Start Over
                </BrandButton>
              </div>
            </>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="p-4 lg:p-8">
        <div className="container max-w-6xl">
          <div className="text-center text-sm text-text-gray">
            <p>Your specialist recommendations are valid for 30 days • Questions? Contact support@another.doctor</p>
          </div>
        </div>
      </footer>
    </div>
  );
}