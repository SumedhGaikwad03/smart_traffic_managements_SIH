// src/App.tsx
import React, { useState, useEffect, useCallback } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import TrafficGrid from "./components/TrafficGrid";
import MetricsDashboard from "./components/MetricsDashboard";
import ControlPanel from "./components/ControlPanel";

import api, {
  MetricsResponse,
  IntersectionData,
  TrafficState,
  DashboardSummary,
} from "./services/api";

import {
  MapIcon,
  ChartBarIcon,
  InformationCircleIcon,
} from "@heroicons/react/24/outline";

const queryClient = new QueryClient();

function AppContent() {
  const [activeTab, setActiveTab] = useState<"map" | "metrics">("map");

  const [state, setState] = useState<TrafficState | null>(null);
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);
  const [dashboard, setDashboard] = useState<DashboardSummary | null>(null);

  const [selectedIntersection, setSelectedIntersection] =
    useState<IntersectionData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const [aiEnabled, setAiEnabled] = useState<boolean>(false);
  const [settingsLoading, setSettingsLoading] = useState<boolean>(false);

  const fetchState = useCallback(async () => {
  try {
    const data = await api.getState();
    setState(data);
    setError(null);   // ← ADD THIS
  } catch (err: any) {
    console.error("Failed to fetch state:", err);
    setError("Failed to fetch traffic state. Is backend running?");
  }
}, []);


  const fetchMetrics = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await api.getMetrics();
      setMetrics(data);
    } catch (err: any) {
      console.error("Failed to fetch metrics:", err);
      setError("Failed to fetch metrics.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchDashboard = useCallback(async () => {
    try {
      const data = await api.getDashboard();
      setDashboard(data);
    } catch (err: any) {
      console.error("Failed to fetch dashboard summary:", err);
    }
  }, []);

  const fetchSettings = useCallback(async () => {
    setSettingsLoading(true);
    try {
      const s: any = await api.getSettings();
      const rawStrategy =
        s?.optimization_strategy ??
        s?.active_strategy ??
        s?.activeStrategy ??
        (s?.optimizationStrategy ?? null) ??
        (s?.strategy ?? null);

      const strategyStr =
        rawStrategy !== null && rawStrategy !== undefined
          ? String(rawStrategy).toLowerCase()
          : "";

      const aiFlag = s?.ai_mode === true || s?.aiMode === true;

      setAiEnabled(strategyStr.startsWith("ai") || aiFlag);
    } catch (err) {
      console.warn("Failed to fetch settings:", err);
    } finally {
      setSettingsLoading(false);
    }
  }, []);

  const toggleAi = async (enabled: boolean) => {
    setSettingsLoading(true);
    const strategy = enabled ? "ai" : "manual";
    try {
      await api.updateSettings({ optimization_strategy: strategy });
      setAiEnabled(enabled);
      fetchDashboard();
      fetchMetrics();
      fetchState();
    } catch (err: any) {
      console.error("Failed to update settings:", err);
      setError("Failed to switch AI mode. Check backend.");
    } finally {
      setSettingsLoading(false);
    }
  };

  useEffect(() => {
  // Initial one-time fetch
  fetchState();
  fetchMetrics();
  fetchDashboard();
  fetchSettings();

  // Fast loop: ONLY simulation state (cars + signals)
  const stateInterval = setInterval(() => {
    fetchState();
  }, 400);   // ~2.5 updates per second

  // Slow loop: heavy stuff (metrics + dashboard)
  const metricsInterval = setInterval(() => {
    fetchMetrics();
    fetchDashboard();
  }, 2000);  // every 2 seconds

  return () => {
    clearInterval(stateInterval);
    clearInterval(metricsInterval);
  };
}, [fetchState, fetchMetrics, fetchDashboard, fetchSettings]);


  const intersectionsForGrid = Array.isArray(state)
    ? state
    : (state && (state as any).intersections) || [];

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-6">
              <h1 className="text-2xl font-bold text-gray-900">
                🚦 Smart Traffic Management
              </h1>

              <div className="flex bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => setActiveTab("map")}
                  className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors ${activeTab === "map"
                    ? "bg-white text-blue-600 shadow-sm"
                    : "text-gray-600 hover:text-gray-900"
                    }`}
                >
                  <MapIcon className="w-5 h-5" />
                  Map View
                </button>

                <button
                  onClick={() => setActiveTab("metrics")}
                  className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors ${activeTab === "metrics"
                    ? "bg-white text-blue-600 shadow-sm"
                    : "text-gray-600 hover:text-gray-900"
                    }`}
                >
                  <ChartBarIcon className="w-5 h-5" />
                  Metrics
                </button>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-sm">
                <span className="text-gray-600">AI Optimization</span>
                <button
                  onClick={() => toggleAi(!aiEnabled)}
                  disabled={settingsLoading}
                  className={`relative inline-flex items-center h-6 rounded-full w-12 transition-colors ${aiEnabled ? "bg-blue-600" : "bg-gray-300"
                    }`}
                >
                  <span
                    className={`inline-block w-4 h-4 transform bg-white rounded-full transition-transform ${aiEnabled ? "translate-x-6" : "translate-x-1"
                      }`}
                  />
                </button>
              </div>

              <div className="flex items-center gap-2 text-sm">
                <span
                  className={`w-2 h-2 rounded-full ${dashboard?.status === "running"
                    ? "bg-green-600 animate-pulse"
                    : "bg-gray-400"
                    }`}
                />
                <span className="text-gray-600">
                  {dashboard?.status === "running" ? "Active" : "Idle"}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4 m-4">
          <div className="flex items-center">
            <InformationCircleIcon className="h-5 w-5 text-red-400" />
            <p className="ml-3 text-sm text-red-700">{error}</p>
          </div>
        </div>
      )}

      <div className="flex flex-col lg:flex-row gap-6 p-6">
        <div className="w-full lg:w-80">
          {!aiEnabled && (
            <ControlPanel
  onSendControl={api.sendControl}
  lastControl={api.getLastControl}
  selectedIntersection={selectedIntersection}
/>

          )}

          {selectedIntersection && (
            <div className="mt-4 bg-white rounded-lg shadow-lg p-4">
              <h3 className="font-semibold mb-2">
                {selectedIntersection.id}
              </h3>
              <div className="grid grid-cols-2 gap-2 text-sm">
                {Object.entries(selectedIntersection.queues).map(
                  ([direction, val]) => (
                    <div key={direction} className="flex justify-between">
                      <span className="text-gray-600">{direction}</span>
                      <span className="font-medium">{val}</span>
                    </div>
                  )
                )}
              </div>
              <div className="border-t mt-2 pt-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Processed</span>
                  <span className="font-medium">
                    {selectedIntersection.processed}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Avg Wait</span>
                  <span className="font-medium">
                    {selectedIntersection.avg_wait.toFixed(1)}s
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* FIX APPLIED HERE */}
        <div className="flex-1 min-h-[600px]">
          {activeTab === "map" ? (
            <TrafficGrid
              intersections={intersectionsForGrid}
              vehicles={state?.vehicles || []}
              edges={state?.edges || []}         // ← ADD THIS
              onIntersectionClick={setSelectedIntersection}
            />


          ) : (
            <MetricsDashboard
              metrics={metrics}
              isLoading={isLoading}
            />
          )}
        </div>
      </div>

      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-6 py-4 text-sm text-gray-600 flex justify-between">
          <div>Smart Traffic Management System (MVP)</div>
          <div className="flex items-center gap-2">
            <span
              className={`w-2 h-2 rounded-full ${dashboard?.status === "running"
                ? "bg-green-600 animate-pulse"
                : "bg-gray-400"
                }`}
            />
            <span>
              {dashboard?.status === "running" ? "Active" : "Idle"}
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  );
}
