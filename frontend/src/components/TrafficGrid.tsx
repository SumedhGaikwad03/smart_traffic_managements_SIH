import React, { useMemo } from "react";
import { IntersectionData, VehicleState, EdgeShape } from "../services/api";
import { motion } from "framer-motion";

interface Props {
  intersections: IntersectionData[];
  vehicles?: VehicleState[];
  edges?: EdgeShape[];
  onIntersectionClick?: (i: IntersectionData) => void;
}

const TrafficGrid: React.FC<Props> = ({
  intersections,
  vehicles = [],
  edges = [],
  onIntersectionClick
}) => {
  const WIDTH = 900;
  const HEIGHT = 600;
  const PADDING = 40;

  const scaled = useMemo(() => {
    if (!intersections.length) return { ints: [], cars: [], roads: [] };

    const xs = [
      ...intersections.map(i => i.position[0]),
      ...edges.flatMap(e => e.shape.map(p => p[0]))
    ];

    const ys = [
      ...intersections.map(i => i.position[1]),
      ...edges.flatMap(e => e.shape.map(p => p[1]))
    ];

    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);

    const sx = (WIDTH - PADDING * 2) / (maxX - minX || 1);
    const sy = (HEIGHT - PADDING * 2) / (maxY - minY || 1);

    const scaleXf = (x: number) => PADDING + (x - minX) * sx;
    const scaleYf = (y: number) => HEIGHT - (PADDING + (y - minY) * sy);

    const ints = intersections.map(i => ({
      ...i,
      screenX: scaleXf(i.position[0]),
      screenY: scaleYf(i.position[1]),
    }));

    const cars = vehicles.map(v => ({
      ...v,
      screenX: scaleXf(v.x),
      screenY: scaleYf(v.y),
    }));

    const roads = edges.map(edge => ({
      id: edge.id,
      points: edge.shape
        .map(([x, y]) => `${scaleXf(x)},${scaleYf(y)}`)
        .join(" ")
    }));

    return { ints, cars, roads };

  }, [JSON.stringify(intersections), vehicles, edges]);

  const signalColor = (state: string) => {
    if (state === "GREEN") return "#22c55e";
    if (state === "YELLOW") return "#eab308";
    return "#ef4444";
  };

  const vehicleAngle = (v: VehicleState) => {
    const deg = Math.atan2(v.vy, v.vx) * (180 / Math.PI);
    return isFinite(deg) ? deg : 0;
  };

  const dirToPos = {
    NORTH: [0, -30],
    SOUTH: [0, 30],
    EAST: [30, 0],
    WEST: [-30, 0],
  } as const;

  return (
    <div className="relative bg-white w-full h-full rounded-lg shadow-lg overflow-hidden">
      <svg width="100%" height="100%" viewBox={`0 0 ${WIDTH} ${HEIGHT}`}>

        {/* Roads */}
        <g stroke="#cbd5e1" strokeWidth="6" strokeLinecap="round">
          {scaled.roads.map(r => (
            <polyline
              key={r.id}
              points={r.points}
              fill="none"
            />
          ))}
        </g>

        {/* Vehicles */}
        {scaled.cars.map(car => (
          <motion.rect
            key={car.id}
            x={car.screenX - 4}
            y={car.screenY - 4}
            width={9}
            height={9}
            fill="#2563eb"
            transform={`rotate(${vehicleAngle(car)}, ${car.screenX}, ${car.screenY})`}
            animate={{ x: 0, y: 0 }}
            transition={{ duration: 0.14 }}
          />
        ))}

        {/* Intersections & Signals */}
        {scaled.ints.map(int => {
          const totalQ = Object.values(int.queues).reduce((a, b) => a + b, 0);

          return (
            <g key={int.id} transform={`translate(${int.screenX}, ${int.screenY})`}>

              {/* Node */}
              <motion.circle
                r={22}
                fill="white"
                stroke={totalQ > 20 ? "#ef4444" : totalQ > 10 ? "#eab308" : "#22c55e"}
                strokeWidth="4"
                whileHover={{ scale: 1.1 }}
                onClick={() => onIntersectionClick?.(int)}
                style={{ cursor: "pointer" }}
              />

              {/* Traffic Lights */}
              {(Object.keys(dirToPos) as Array<keyof typeof dirToPos>).map(dir => {
                const [x, y] = dirToPos[dir];

                return (
                  <circle
                    key={dir}
                    cx={x}
                    cy={y}
                    r={6}
                    fill={signalColor(int.signals?.[dir] ?? "RED")}
                  />
                );
              })}

              {/* Queue Count */}
              <text
                x={0}
                y={4}
                textAnchor="middle"
                className="font-bold text-sm"
                fill="#374151"
              >
                {totalQ}
              </text>

              {/* Intersection ID */}
              <text
                x={0}
                y={38}
                textAnchor="middle"
                className="text-xs"
                fill="#6b7280"
              >
                {int.id}
              </text>

              {/* Debug: Signal state */}
              <text
  x={0}
  y={52}
  textAnchor="middle"
  className="text-[10px]"
  fill="#9ca3af"
>
  Phase: {int.phase}
</text>

            </g>
          );
        })}
      </svg>
    </div>
  );
};

export default TrafficGrid;
