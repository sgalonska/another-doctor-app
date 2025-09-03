import React from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import { Logo } from '@/components/ui/logo';
import { Button } from '@/components/ui/button';
import { 
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from '@/components/ui/navigation-menu';

interface HeaderProps {
  className?: string;
  variant?: 'default' | 'transparent';
}

export function Header({ className, variant = 'default' }: HeaderProps) {
  return (
    <header className={cn(
      'sticky top-0 z-50 border-b transition-colors',
      variant === 'default' ? 'bg-white border-gray-200' : 'bg-white/80 backdrop-blur-md border-gray-200/50',
      className
    )}>
      <div className="container flex h-16 items-center justify-between">
        {/* Logo */}
        <div className="flex items-center">
          <Logo variant="nav" priority />
        </div>

        {/* Navigation */}
        <NavigationMenu className="hidden md:flex">
          <NavigationMenuList>
            <NavigationMenuItem>
              <NavigationMenuTrigger className="text-text-gray hover:text-text-dark">
                Platform
              </NavigationMenuTrigger>
              <NavigationMenuContent>
                <ul className="grid w-[400px] gap-3 p-4 md:w-[500px] md:grid-cols-2">
                  <li className="row-span-3">
                    <NavigationMenuLink asChild>
                      <Link
                        className="flex h-full w-full select-none flex-col justify-end rounded-md bg-brand-gradient p-6 no-underline outline-none focus:shadow-md"
                        href="/cases"
                      >
                        <div className="mb-2 mt-4 text-lg font-medium text-text-dark">
                          Case Analysis
                        </div>
                        <p className="text-sm leading-tight text-text-gray">
                          Upload patient cases and get AI-powered specialist matching recommendations.
                        </p>
                      </Link>
                    </NavigationMenuLink>
                  </li>
                  <ListItem href="/specialists" title="Find Specialists">
                    Search and connect with medical specialists worldwide.
                  </ListItem>
                  <ListItem href="/dashboard" title="Dashboard">
                    Manage your cases, consultations, and specialist network.
                  </ListItem>
                  <ListItem href="/analytics" title="Analytics">
                    Track outcomes and improve patient care decisions.
                  </ListItem>
                </ul>
              </NavigationMenuContent>
            </NavigationMenuItem>
            
            <NavigationMenuItem>
              <Link href="/specialists" legacyBehavior passHref>
                <NavigationMenuLink className="text-text-gray hover:text-text-dark px-4 py-2 text-sm font-medium transition-colors">
                  Specialists
                </NavigationMenuLink>
              </Link>
            </NavigationMenuItem>
            
            <NavigationMenuItem>
              <Link href="/about" legacyBehavior passHref>
                <NavigationMenuLink className="text-text-gray hover:text-text-dark px-4 py-2 text-sm font-medium transition-colors">
                  About
                </NavigationMenuLink>
              </Link>
            </NavigationMenuItem>
            
            <NavigationMenuItem>
              <Link href="/contact" legacyBehavior passHref>
                <NavigationMenuLink className="text-text-gray hover:text-text-dark px-4 py-2 text-sm font-medium transition-colors">
                  Contact
                </NavigationMenuLink>
              </Link>
            </NavigationMenuItem>
          </NavigationMenuList>
        </NavigationMenu>

        {/* Action buttons */}
        <div className="flex items-center space-x-4">
          <Button variant="ghost" asChild className="hidden md:inline-flex">
            <Link href="/login">Log in</Link>
          </Button>
          <Button asChild className="bg-brand-teal hover:bg-brand-teal-dark">
            <Link href="/signup">Get Started</Link>
          </Button>
        </div>
      </div>
    </header>
  );
}

const ListItem = React.forwardRef<
  React.ElementRef<'a'>,
  React.ComponentPropsWithoutRef<'a'> & { title: string }
>(({ className, title, children, ...props }, ref) => {
  return (
    <li>
      <NavigationMenuLink asChild>
        <a
          ref={ref}
          className={cn(
            'block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-bg-light focus:bg-bg-light',
            className
          )}
          {...props}
        >
          <div className="text-sm font-medium leading-none text-text-dark">{title}</div>
          <p className="line-clamp-2 text-sm leading-snug text-text-gray">
            {children}
          </p>
        </a>
      </NavigationMenuLink>
    </li>
  );
});
ListItem.displayName = 'ListItem';