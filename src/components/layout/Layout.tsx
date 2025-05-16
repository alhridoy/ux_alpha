
import React from 'react';
import Header from './Header';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col bg-uxagent-soft-gray">
      <Header />
      <main className="flex-1 container mx-auto p-4 md:p-6">
        {children}
      </main>
      <footer className="border-t bg-white py-4 text-center text-sm text-muted-foreground">
        <div className="container">
          UXAgent - Simulating Usability Testing with LLM Agents © {new Date().getFullYear()}
        </div>
      </footer>
    </div>
  );
};

export default Layout;
