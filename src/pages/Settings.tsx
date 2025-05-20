
import React from 'react';
import Layout from '@/components/layout/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import ApiKeyConfig from '@/components/settings/ApiKeyConfig';

const Settings = () => {
  return (
    <Layout>
      <div className="animate-fade-in">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-uxagent-charcoal mb-2">Settings</h1>
          <p className="text-muted-foreground">
            Configure UXAgent to connect with external services
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <ApiKeyConfig />
          
          <Card>
            <CardHeader>
              <CardTitle>Browser Automation</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground mb-4">
                Browser automation requires server-side setup to connect with Puppeteer or Playwright.
              </p>
              <p className="text-sm">
                For a fully functional UXAgent implementation, you'll need to set up a server that can:
              </p>
              <ul className="list-disc pl-5 space-y-1 mt-2 text-sm">
                <li>Launch browser instances</li>
                <li>Execute commands from the LLM agent</li>
                <li>Record browser sessions</li>
                <li>Extract page content for the agent to analyze</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </Layout>
  );
};

export default Settings;
