import React from 'react';
import { Header } from '@/components/layout/header';
import { Footer } from '@/components/layout/footer';
import { cn } from '@/lib/utils';

interface MainLayoutProps {
  children: React.ReactNode;
  className?: string;
  headerVariant?: 'default' | 'transparent';
  showFooter?: boolean;
}

export function MainLayout({ 
  children, 
  className,
  headerVariant = 'default',
  showFooter = true 
}: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-white">
      <Header variant={headerVariant} />
      
      <main className={cn('flex-1', className)}>
        {children}
      </main>
      
      {showFooter && <Footer />}
    </div>
  );
}