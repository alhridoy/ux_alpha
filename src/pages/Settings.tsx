
import React from 'react';
import Layout from '@/components/layout/Layout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Laptop, Server } from 'lucide-react';
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
        
        <Tabs defaultValue="api-keys">
          <TabsList className="mb-6">
            <TabsTrigger value="api-keys">API Keys</TabsTrigger>
            <TabsTrigger value="automation">Browser Automation</TabsTrigger>
          </TabsList>
          
          <TabsContent value="api-keys">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <ApiKeyConfig />
            </div>
          </TabsContent>
          
          <TabsContent value="automation">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <Laptop className="h-5 w-5 text-uxagent-purple" />
                    <CardTitle>Browser Automation</CardTitle>
                  </div>
                  <CardDescription>
                    Configure browser automation for UX testing
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between space-x-2">
                    <Label htmlFor="automation-enabled" className="flex flex-col space-y-1">
                      <span>Enable Browser Automation</span>
                      <span className="font-normal text-xs text-muted-foreground">
                        Allow UXAgent to control browsers for simulations
                      </span>
                    </Label>
                    <Switch id="automation-enabled" />
                  </div>
                  
                  <div className="flex items-center justify-between space-x-2">
                    <Label htmlFor="headless-mode" className="flex flex-col space-y-1">
                      <span>Headless Mode</span>
                      <span className="font-normal text-xs text-muted-foreground">
                        Run browsers in the background without UI
                      </span>
                    </Label>
                    <Switch id="headless-mode" />
                  </div>
                  
                  <div className="flex items-center justify-between space-x-2">
                    <Label htmlFor="record-screenshots" className="flex flex-col space-y-1">
                      <span>Record Screenshots</span>
                      <span className="font-normal text-xs text-muted-foreground">
                        Capture screenshots at each step
                      </span>
                    </Label>
                    <Switch id="record-screenshots" />
                  </div>
                </CardContent>
                <CardFooter>
                  <p className="text-sm text-muted-foreground">
                    Browser automation requires Puppeteer or Playwright to be installed on your server.
                  </p>
                </CardFooter>
              </Card>
              
              <Card>
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <Server className="h-5 w-5 text-uxagent-purple" />
                    <CardTitle>Automation Server</CardTitle>
                  </div>
                  <CardDescription>
                    Connect to a server that can run browser automation
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid w-full items-center gap-1.5">
                    <Label htmlFor="server-url">Server URL</Label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        id="server-url"
                        placeholder="https://your-automation-server.com"
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                      />
                    </div>
                  </div>
                  
                  <div className="grid w-full items-center gap-1.5">
                    <Label htmlFor="api-key">API Key (if required)</Label>
                    <div className="flex gap-2">
                      <input
                        type="password"
                        id="api-key"
                        placeholder="••••••••••••••••"
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                      />
                    </div>
                  </div>
                </CardContent>
                <CardFooter className="flex justify-between">
                  <Button variant="outline">Test Connection</Button>
                  <Button className="bg-uxagent-purple hover:bg-uxagent-dark-purple">Save Configuration</Button>
                </CardFooter>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  );
};

export default Settings;
