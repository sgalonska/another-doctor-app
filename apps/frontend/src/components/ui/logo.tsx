import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import { brand } from '@/config/brand';

interface LogoProps {
  variant?: 'nav' | 'hero' | 'footer';
  className?: string;
  href?: string;
  priority?: boolean;
}

export function Logo({ 
  variant = 'nav', 
  className, 
  href = '/',
  priority = false 
}: LogoProps) {
  const logoElement = (
    <Image
      src={brand.assets.logo.primary}
      alt="Another Doctor"
      width={200} // Base width, will be controlled by CSS
      height={45} // Base height
      className={cn(
        'object-contain',
        variant === 'nav' && 'h-[45px] w-auto',
        variant === 'hero' && 'h-[60px] w-auto',
        variant === 'footer' && 'h-[36px] w-auto',
        className
      )}
      priority={priority}
    />
  );

  if (href) {
    return (
      <Link 
        href={href}
        className={cn(
          'inline-block transition-opacity hover:opacity-80',
          className
        )}
      >
        {logoElement}
      </Link>
    );
  }

  return logoElement;
}

// Text-based logo fallback for when image isn't available
export function TextLogo({ 
  variant = 'nav',
  className,
  href = '/' 
}: Omit<LogoProps, 'priority'>) {
  const textElement = (
    <div className={cn(
      'font-bold text-brand-teal transition-colors hover:text-brand-teal-dark',
      variant === 'nav' && 'text-xl',
      variant === 'hero' && 'text-3xl',
      variant === 'footer' && 'text-lg',
      className
    )}>
      Another Doctor
    </div>
  );

  if (href) {
    return (
      <Link href={href} className="inline-block">
        {textElement}
      </Link>
    );
  }

  return textElement;
}