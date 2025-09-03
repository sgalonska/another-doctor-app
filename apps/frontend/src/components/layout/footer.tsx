import React from 'react';
import Link from 'next/link';
import { Logo } from '@/components/ui/logo';
import { cn } from '@/lib/utils';
import { Mail, Phone, MapPin, Github, Twitter, Linkedin } from 'lucide-react';

interface FooterProps {
  className?: string;
}

export function Footer({ className }: FooterProps) {
  return (
    <footer className={cn(
      'border-t border-gray-200 bg-bg-light',
      className
    )}>
      <div className="container py-12">
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          {/* Company info */}
          <div className="space-y-4">
            <Logo variant="footer" />
            <p className="text-sm text-text-gray">
              AI-powered medical specialist matching platform helping healthcare 
              professionals find the right experts for complex cases.
            </p>
            <div className="flex space-x-4">
              <SocialLink href="#" icon={<Twitter className="h-4 w-4" />} />
              <SocialLink href="#" icon={<Linkedin className="h-4 w-4" />} />
              <SocialLink href="#" icon={<Github className="h-4 w-4" />} />
            </div>
          </div>

          {/* Platform */}
          <div className="space-y-4">
            <h3 className="font-semibold text-text-dark">Platform</h3>
            <ul className="space-y-2 text-sm">
              <li><FooterLink href="/cases">Case Analysis</FooterLink></li>
              <li><FooterLink href="/specialists">Find Specialists</FooterLink></li>
              <li><FooterLink href="/dashboard">Dashboard</FooterLink></li>
              <li><FooterLink href="/analytics">Analytics</FooterLink></li>
              <li><FooterLink href="/api">API</FooterLink></li>
            </ul>
          </div>

          {/* Resources */}
          <div className="space-y-4">
            <h3 className="font-semibold text-text-dark">Resources</h3>
            <ul className="space-y-2 text-sm">
              <li><FooterLink href="/docs">Documentation</FooterLink></li>
              <li><FooterLink href="/blog">Blog</FooterLink></li>
              <li><FooterLink href="/help">Help Center</FooterLink></li>
              <li><FooterLink href="/security">Security</FooterLink></li>
              <li><FooterLink href="/compliance">HIPAA Compliance</FooterLink></li>
            </ul>
          </div>

          {/* Contact */}
          <div className="space-y-4">
            <h3 className="font-semibold text-text-dark">Contact</h3>
            <ul className="space-y-2 text-sm text-text-gray">
              <li className="flex items-center space-x-2">
                <Mail className="h-4 w-4" />
                <span>hello@another.doctor</span>
              </li>
              <li className="flex items-center space-x-2">
                <Phone className="h-4 w-4" />
                <span>+1 (555) 123-4567</span>
              </li>
              <li className="flex items-center space-x-2">
                <MapPin className="h-4 w-4" />
                <span>San Francisco, CA</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 border-t border-gray-300 pt-8">
          <div className="flex flex-col items-center justify-between space-y-4 md:flex-row md:space-y-0">
            <p className="text-sm text-text-gray">
              © 2024 Another Doctor. All rights reserved.
            </p>
            <div className="flex space-x-6 text-sm">
              <FooterLink href="/privacy">Privacy Policy</FooterLink>
              <FooterLink href="/terms">Terms of Service</FooterLink>
              <FooterLink href="/cookies">Cookie Policy</FooterLink>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

interface FooterLinkProps {
  href: string;
  children: React.ReactNode;
  className?: string;
}

function FooterLink({ href, children, className }: FooterLinkProps) {
  return (
    <Link 
      href={href}
      className={cn(
        'text-text-gray transition-colors hover:text-brand-teal',
        className
      )}
    >
      {children}
    </Link>
  );
}

interface SocialLinkProps {
  href: string;
  icon: React.ReactNode;
  className?: string;
}

function SocialLink({ href, icon, className }: SocialLinkProps) {
  return (
    <Link
      href={href}
      className={cn(
        'flex h-8 w-8 items-center justify-center rounded-full bg-white text-text-gray transition-colors hover:bg-brand-teal hover:text-white',
        className
      )}
    >
      {icon}
    </Link>
  );
}