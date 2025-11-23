// src/services/api.ts
import axios, { AxiosError } from "axios";

/**
 * API client for Smart Traffic Management frontend
 * - Uses typed methods (TS interfaces below)
 * - Adds timeout + basic error wrapping
 * - Provides a mock fallback helper (useful during backend dev)
 */

/* -------------------------
   Configuration
   ------------------------- */
const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";
const DEFAULT_TIMEOUT = 20000; // ms

export const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: DEFAULT_TIMEOUT,
  headers: { "Content-Type": "application/json" },
});

/* ===========================================================
   Types (match backend Pydantic models)
   =========================================================== */

export interface IntersectionData {
  id: string;
  queues: Record<string, number>;
  processed: number;
  avg_wait: number;
  signals: Record<string, "GREEN" | "YELLOW" | "RED">;
  phase: number;                  // ADD THIS
  position: [number, number];
}


export interface TrafficState {
  timestamp: number;
  intersections: IntersectionData[];
  vehicles: VehicleState[];
  edges: EdgeShape[];   // <--------- ADD THIS
}

export interface MetricsResponse {
  avg_wait_time: number;
  total_processed: number;
  throughput: number;
  congestion_index: number;
  optimization_strategy: string;
  wait_time_history?: number[];
  throughput_history?: number[];
}
export interface VehicleState {
  id: string;
  x: number;
  y: number;
  speed: number;
  lane: string;
}


export interface EdgeShape {
  id: string;
  shape: [number, number][];
}

export interface VehicleState {
  id: string;
  x: number;
  y: number;
  speed: number;
  lane: string;
  waiting_time: number;
  vx: number;
  vy: number;
}



export interface DashboardSummary {
  status: "running" | "idle";
  timestamp: number;
  intersections_total: number;
  active_strategy: string;
  last_optimized: number;
  alerts: {
    emergency_vehicles: number;
    high_congestion_nodes: string[];
  };
}

export interface ControlAction {
  intersection: string;
  action: string;
}

/* ===========================================================
   Small helpers: error wrapper + optional mock fallback
   =========================================================== */

/**
 * Safely parse errors from axios or generic errors.
 * Uses axios.isAxiosError to properly narrow types instead of unsafe casting.
 */
function parseAxiosError(err: unknown): string {
  if (err == null) return "Unknown error";

  // Prefer axios.isAxiosError for accurate narrowing
  if (axios.isAxiosError(err)) {
    const a = err as AxiosError;
    // Try multiple places where servers often put messages
    const data = a.response?.data as any;
    const candidate =
      (data && (data.message || data.error || data.detail)) ||
      a.message ||
      `${a.code ?? "NETWORK_ERROR"}`;
    return String(candidate);
  }

  // Non-axios Error objects
  if (err instanceof Error) return err.message;
  try {
    return String(err);
  } catch {
    return "Unknown non-error thrown";
  }
}

/**
 * Generic request wrapper
 * - returns data or throws an Error with a clear message
 */
async function request<T>(fn: () => Promise<{ data: T }>): Promise<T> {
  try {
    const res = await fn();
    return res.data;
  } catch (err) {
    const msg = parseAxiosError(err);
    throw new Error(msg);
  }
}

/* ===========================================================
   API class (concrete endpoints)
   =========================================================== */

class TrafficAPI {
  // Health-check / status
  async getStatus(): Promise<{ running: boolean; timestamp?: number; metrics?: MetricsResponse }>{
    return request(() => axiosInstance.get("/api/dashboard/status").catch(() => axiosInstance.get("/api/dashboard")));
    // backend may expose /api/dashboard or a more specific /api/dashboard/status; adjust as needed
  }

  async isAlive(): Promise<boolean> {
    try {
      await axiosInstance.get("/");
      return true;
    } catch {
      return false;
    }
  }

  async getState(): Promise<TrafficState> {
    return request(() => axiosInstance.get("/api/state"));
  }

  async getMetrics(): Promise<MetricsResponse> {
    return request(() => axiosInstance.get("/api/metrics"));
  }

  async getDashboard(): Promise<DashboardSummary> {
    return request(() => axiosInstance.get("/api/dashboard"));
  }

  async updateSettings(settings: { optimization_strategy: string }): Promise<any> {
    return request(() => axiosInstance.post("/api/settings", settings));
  }

  async getSettings(): Promise<{ optimization_strategy: string; last_updated: number }> {
    return request(() => axiosInstance.get("/api/settings"));
  }

  async sendControl(action: ControlAction): Promise<ControlAction> {
    return request(() => axiosInstance.post("/api/control", action));
  }

  async getLastControl(): Promise<any> {
    return request(() => axiosInstance.get("/api/control/last"));
  }

  // Optional convenience routes your frontend might need
  async startSimulation(): Promise<{ status: string; message?: string }> {
    return request(() => axiosInstance.post("/api/start"));
  }

  async stopSimulation(): Promise<{ status: string; message?: string }> {
    return request(() => axiosInstance.post("/api/stop"));
  }

  async triggerOptimization(): Promise<{ status: string }> {
    return request(() => axiosInstance.post("/api/optimize"));
  }

  async exportData(): Promise<Blob> {
    // For downloads: set responseType
    try {
      const res = await axiosInstance.get("/api/export", { responseType: "blob" });
      return res.data;
    } catch (err) {
      throw new Error(parseAxiosError(err));
    }
  }
}

export default new TrafficAPI();
