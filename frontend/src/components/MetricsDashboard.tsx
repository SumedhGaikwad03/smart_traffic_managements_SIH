import React, { useMemo } from "react";
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { motion } from "framer-motion";
import {
  ClockIcon,
  TruckIcon,
  ChartBarIcon,
  BoltIcon,
} from "@heroicons/react/24/solid";

import { MetricsResponse } from "../services/api";

/**
 * Fancy, backend-synced MetricsDashboard
 *
 * Expects MetricsResponse:
 * {
 *   avg_wait_time,
 *   total_processed,
 *   throughput,
 *   congestion_index,
 *   optimization_strategy,
 *   wait_time_history?: number[],
 *   throughput_history?: number[]
 * }
 */

interface Props {
  metrics: MetricsResponse | null;
  isLoading?: boolean;
}

const StatCard: React.FC<{
  title: string;
  value: React.ReactNode;
  subtitle?: string;
  icon?: React.ReactNode;
  colorClass?: string;
}> = ({ title, value, subtitle, icon, colorClass = "border-l-blue-500" }) => (
  <motion.div
    initial={{ opacity: 0, y: 8 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.25 }}
    className={`bg-white rounded-lg shadow-lg p-5 border-l-4 ${colorClass}`}
  >
    <div className="flex justify-between items-start">
      <div>
        <p className="text-sm text-gray-500">{title}</p>
        <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
        {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
      </div>
      <div className="p-2 rounded-full bg-white/50">{icon}</div>
    </div>
  </motion.div>
);

export default function MetricsDashboard({ metrics, isLoading }: Props) {
  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // No metrics yet
  if (!metrics) {
    return (
      <div className="text-center text-gray-500 py-8">
        No metrics available. The backend might be mocked or simulation not running.
      </div>
    );
  }

    // Normalize history arrays into stable refs (useMemo prevents identity churn)
  const waitHistory = useMemo(() => metrics.wait_time_history ?? [], [metrics?.wait_time_history]);
  const throughputHistory = useMemo(() => metrics.throughput_history ?? [], [metrics?.throughput_history]);

  // Build chart points (align lengths; show last N points)
  const points = Math.max(waitHistory.length, throughputHistory.length, 1);
  const chartData = useMemo(() =>
    Array.from({ length: points }).map((_, idx) => ({
      time: `T-${points - idx}`,
      wait: waitHistory[idx] ?? null,
      throughput: throughputHistory[idx] ?? null,
    })), [points, waitHistory, throughputHistory]
  );

  // Compute improvement % from wait history (earliest -> latest)
  const improvement = useMemo(() => {
    if (waitHistory.length >= 2) {
      const first = waitHistory[0];
      const last = waitHistory[waitHistory.length - 1];
      if (first === 0) return null;
      const pct = ((first - last) / Math.max(1, first)) * 100;
      return pct;
    }
    return null;
  }, [waitHistory]);


  return (
    <div className="space-y-6">
      {/* Top KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Average Wait Time"
          value={`${metrics.avg_wait_time.toFixed(1)}s`}
          subtitle={
            improvement !== null
              ? `${improvement >= 0 ? "↓" : "↑"} ${Math.abs(improvement).toFixed(1)}% vs start`
              : "Improvement: N/A"
          }
          icon={<ClockIcon className="w-6 h-6 text-blue-600" />}
          colorClass="border-l-blue-500"
        />

        <StatCard
          title="Vehicles in System"
          value={metrics.total_processed}
          subtitle="Total processed (cumulative)"
          icon={<TruckIcon className="w-6 h-6 text-yellow-600" />}
          colorClass="border-l-yellow-500"
        />

        <StatCard
          title="Throughput"
          value={metrics.throughput}
          subtitle="Current throughput"
          icon={<ChartBarIcon className="w-6 h-6 text-green-600" />}
          colorClass="border-l-green-500"
        />

        <StatCard
          title="Optimization Mode"
          value={metrics.optimization_strategy?.toUpperCase() ?? "N/A"}
          subtitle={`Congestion: ${(metrics.congestion_index * 100).toFixed(0)}%`}
          icon={<BoltIcon className="w-6 h-6 text-purple-600" />}
          colorClass="border-l-purple-500"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Wait Time Area */}
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white rounded-lg shadow-lg p-6"
        >
          <h3 className="text-lg font-semibold mb-4">Wait Time Trend</h3>
          <ResponsiveContainer width="100%" height={260}>
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Area
                type="monotone"
                dataKey="wait"
                stroke="#3b82f6"
                fill="#bfdbfe"
                strokeWidth={2}
                isAnimationActive={true}
              />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Throughput Line */}
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.06 }}
          className="bg-white rounded-lg shadow-lg p-6"
        >
          <h3 className="text-lg font-semibold mb-4">Throughput Trend</h3>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="throughput"
                name="Throughput"
                stroke="#10b981"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Performance Summary */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.12 }}
        className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg shadow-lg p-6 text-white"
      >
        <h3 className="text-xl font-bold mb-2">System Performance</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-4">
          <div>
            <p className="text-sm opacity-90">Improvement</p>
            <p className="text-2xl font-bold">
              {improvement !== null ? `${improvement.toFixed(1)}%` : "N/A"}
            </p>
          </div>

          <div>
            <p className="text-sm opacity-90">Active Strategy</p>
            <p className="text-2xl font-bold">{metrics.optimization_strategy}</p>
          </div>

          <div>
            <p className="text-sm opacity-90">Congestion Index</p>
            <p className="text-2xl font-bold">{(metrics.congestion_index * 100).toFixed(0)}%</p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
