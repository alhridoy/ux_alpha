import React, { useState, useEffect } from 'react';
import { Laptop, RefreshCw } from 'lucide-react';
import { backendService } from '@/services/backendService';

interface LiveBrowserViewProps {
  simulationId: string;
  isActive: boolean;
}

interface LiveUpdate {
  success: boolean;
  progress: number;
  screenshot: string;
  currentAction: string;
  timestamp: number;
  reflections?: string[];
  wonderings?: string[];
  actions?: any[];
}

const LiveBrowserView: React.FC<LiveBrowserViewProps> = ({ simulationId, isActive }) => {
  const [liveUpdate, setLiveUpdate] = useState<LiveUpdate | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch live updates at regular intervals
  useEffect(() => {
    if (!isActive || !simulationId) return;

    const fetchLiveUpdate = async () => {
      try {
        setLoading(true);

        // Use the backend service to handle CORS issues
        const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const response = await fetch(`${baseUrl}/api/stagehand/live/${simulationId}`, {
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        });

        if (!response.ok) {
          throw new Error(`Failed to fetch live update: ${response.statusText}`);
        }

        const data = await response.json();
        setLiveUpdate(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching live update:', err);
        setError('Failed to fetch live browser update');
      } finally {
        setLoading(false);
      }
    };

    // Fetch immediately
    fetchLiveUpdate();

    // Then set up interval for updates
    const intervalId = setInterval(fetchLiveUpdate, 1000);

    // Clean up interval on unmount or when simulation is no longer active
    return () => {
      clearInterval(intervalId);
    };
  }, [simulationId, isActive]);

  if (!isActive) {
    return (
      <div className="bg-white border rounded-md h-[250px] flex items-center justify-center">
        <div className="text-center text-muted-foreground">
          <Laptop className="h-12 w-12 mx-auto mb-2 text-muted-foreground/50" />
          <p>Browser view will appear here during live simulations</p>
          <p className="text-sm">Using Stagehand AI-powered browser automation</p>
        </div>
      </div>
    );
  }

  if (loading && !liveUpdate) {
    return (
      <div className="bg-white border rounded-md h-[250px] flex items-center justify-center">
        <div className="text-center text-muted-foreground">
          <RefreshCw className="h-12 w-12 mx-auto mb-2 text-muted-foreground/50 animate-spin" />
          <p>Loading browser view...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white border rounded-md h-[250px] flex items-center justify-center">
        <div className="text-center text-muted-foreground">
          <p className="text-red-500">{error}</p>
          <p className="text-sm mt-2">Please try refreshing the page</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border rounded-md h-[250px] relative">
      {liveUpdate && (
        <>
          {/* Progress indicator */}
          <div className="absolute top-0 left-0 right-0 h-1 bg-gray-200">
            <div
              className="h-full bg-uxagent-purple transition-all duration-300 ease-in-out"
              style={{ width: `${liveUpdate.progress}%` }}
            />
          </div>

          {/* Current action indicator */}
          <div className="absolute top-2 left-2 right-2 bg-black/70 text-white text-xs p-2 rounded">
            {liveUpdate.currentAction}
          </div>

          {/* Screenshot */}
          <div className="h-full w-full flex items-center justify-center pt-8">
            {liveUpdate.screenshot ? (
              <img
                src={liveUpdate.screenshot}
                alt="Browser view"
                className="max-h-[200px] max-w-full object-contain"
              />
            ) : (
              <div className="text-center text-muted-foreground">
                <p>No screenshot available</p>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default LiveBrowserView;
