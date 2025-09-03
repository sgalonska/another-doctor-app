import React from 'react';
import { Button, ButtonProps } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { Loader2 } from 'lucide-react';

interface BrandButtonProps extends Omit<ButtonProps, 'variant'> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  loading?: boolean;
  loadingText?: string;
}

export function BrandButton({ 
  className, 
  children, 
  variant = 'primary',
  loading = false,
  loadingText,
  disabled,
  ...props 
}: BrandButtonProps) {
  const brandVariants = {
    primary: 'bg-brand-teal text-white hover:bg-brand-teal-dark focus:ring-brand-teal/20',
    secondary: 'bg-brand-coral text-white hover:bg-brand-coral-dark focus:ring-brand-coral/20',
    outline: 'border-2 border-brand-teal text-brand-teal hover:bg-brand-teal hover:text-white focus:ring-brand-teal/20',
    ghost: 'text-brand-teal hover:bg-brand-teal/10 focus:ring-brand-teal/20',
  };

  return (
    <Button
      className={cn(
        'font-medium transition-all duration-200',
        brandVariants[variant],
        'focus:ring-2 focus:ring-offset-2',
        loading && 'cursor-not-allowed',
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
      )}
      {loading ? (loadingText || 'Loading...') : children}
    </Button>
  );
}

// Specialized CTA button with enhanced styling
export function CTAButton({ 
  className, 
  children, 
  ...props 
}: BrandButtonProps) {
  return (
    <BrandButton
      className={cn(
        'px-8 py-3 text-base font-semibold shadow-lg hover:shadow-xl',
        'transform hover:scale-105 transition-all duration-200',
        className
      )}
      {...props}
    >
      {children}
    </BrandButton>
  );
}