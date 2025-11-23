import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, CircleMarker } from 'react-leaflet';
import L from 'leaflet';
import { IntersectionData } from '../services/api';
import 'leaflet/dist/leaflet.css';

// Fix for default markers in React-Leaflet
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

interface TrafficMapProps {
  intersections: IntersectionData[];
  onIntersectionClick?: (intersection: IntersectionData) => void;
}

const TrafficMapOSM: React.FC<TrafficMapProps> = ({ intersections, onIntersectionClick }) => {
  
  // Center map on a default city location (you can change this)
  const center: [number, number] = [40.7128, -74.006]; // New York City
  const zoom = 14;

  // Convert grid position to lat/lng
  const getLatLng = (position: [number, number]): [number, number] => {
    const lng = -74.006 + (position[0] / 10000);
    const lat = 40.7128 + (position[1] / 10000);
    return [lat, lng];
  };

  // Get color based on congestion
  const getCongestionColor = (queueLength: number): string => {
    if (queueLength > 20) return '#ef4444'; // Red
    if (queueLength > 10) return '#eab308'; // Yellow
    return '#22c55e'; // Green
  };

  // Get signal color
  const getSignalColor = (state: string): string => {
    switch(state) {
      case 'GREEN': return '#22c55e';
      case 'YELLOW': return '#eab308';
      case 'RED': return '#ef4444';
      default: return '#gray';
    }
  };

  // Create custom icon for intersections
  const createIntersectionIcon = (intersection: IntersectionData) => {
    const totalQueue = Object.values(intersection.queues).reduce((a, b) => a + b, 0);
    const color = getCongestionColor(totalQueue);
    
    return L.divIcon({
      className: 'custom-intersection-marker',
      html: `
        <div style="
          width: 48px;
          height: 48px;
          background: white;
          border: 3px solid ${color};
          border-radius: 50%;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          box-shadow: 0 2px 8px rgba(0,0,0,0.2);
          cursor: pointer;
        ">
          <div style="display: flex; gap: 2px; margin-bottom: 2px;">
            ${['NORTH', 'SOUTH', 'EAST', 'WEST'].map(dir => `
              <div style="
                width: 8px;
                height: 8px;
                background: ${getSignalColor(intersection.signals[dir])};
                border-radius: 50%;
              "></div>
            `).join('')}
          </div>
          <div style="
            font-size: 12px;
            font-weight: bold;
            color: ${color};
          ">${totalQueue}</div>
        </div>
      `,
      iconSize: [48, 48],
      iconAnchor: [24, 24],
    });
  };

  // Calculate traffic flow lines between intersections
  const getTrafficFlowLines = () => {
    const lines = [];
    
    for (let i = 0; i < intersections.length - 1; i++) {
      for (let j = i + 1; j < intersections.length; j++) {
        const int1 = intersections[i];
        const int2 = intersections[j];
        
        // Only connect adjacent intersections
        if (Math.abs(int1.position[0] - int2.position[0]) <= 100 || 
            Math.abs(int1.position[1] - int2.position[1]) <= 100) {
          
          const congestion1 = Object.values(int1.queues).reduce((a, b) => a + b, 0);
          const congestion2 = Object.values(int2.queues).reduce((a, b) => a + b, 0);
          const avgCongestion = (congestion1 + congestion2) / 2;
          
          lines.push({
            positions: [getLatLng(int1.position), getLatLng(int2.position)],
            color: getCongestionColor(avgCongestion),
            weight: 4,
            opacity: 0.6,
          });
        }
      }
    }
    
    return lines;
  };

  return (
    <div className="relative w-full h-full">
      <MapContainer
        center={center}
        zoom={zoom}
        className="w-full h-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {/* Traffic flow lines */}
        {getTrafficFlowLines().map((line, index) => (
          <Polyline
            key={index}
            positions={line.positions}
            color={line.color}
            weight={line.weight}
            opacity={line.opacity}
          />
        ))}
        
        {/* Intersection markers */}
        {intersections.map((intersection) => {
          const position = getLatLng(intersection.position);
          const totalQueue = Object.values(intersection.queues).reduce((a, b) => a + b, 0);
          
          return (
            <Marker
              key={intersection.id}
              position={position}
              icon={createIntersectionIcon(intersection)}
              eventHandlers={{
                click: () => {
                  if (onIntersectionClick) {
                    onIntersectionClick(intersection);
                  }
                },
              }}
            >
              <Popup>
                <div className="p-2">
                  <h3 className="font-bold text-sm">{intersection.id}</h3>
                  <div className="mt-2 space-y-1 text-xs">
                    <div>Queue: {totalQueue} vehicles</div>
                    <div>Processed: {intersection.processed}</div>
                    <div>Avg Wait: {intersection.avg_wait.toFixed(1)}s</div>
                  </div>
                  <div className="mt-2">
                    <div className="text-xs font-semibold mb-1">Signals:</div>
                    <div className="grid grid-cols-2 gap-1 text-xs">
                      {Object.entries(intersection.signals).map(([dir, state]) => (
                        <div key={dir} className="flex items-center gap-1">
                          <div 
                            className="w-2 h-2 rounded-full"
                            style={{ backgroundColor: getSignalColor(state) }}
                          />
                          <span>{dir}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}
        
        {/* Add animated vehicles */}
        {intersections.map((intersection) => {
          const position = getLatLng(intersection.position);
          const queueLength = Object.values(intersection.queues).reduce((a, b) => a + b, 0);
          
          return Array.from({ length: Math.min(queueLength, 5) }).map((_, i) => (
            <CircleMarker
              key={`${intersection.id}-vehicle-${i}`}
              center={[
                position[0] + (Math.random() - 0.5) * 0.001,
                position[1] + (Math.random() - 0.5) * 0.001,
              ]}
              radius={3}
              pathOptions={{
                fillColor: '#3b82f6',
                fillOpacity: 0.8,
                color: '#1e40af',
                weight: 1,
              }}
            />
          ));
        })}
      </MapContainer>
      
      {/* Legend */}
      <div className="absolute top-4 left-4 bg-white/90 backdrop-blur p-3 rounded-lg shadow-lg z-[1000]">
        <h3 className="text-sm font-semibold mb-2">Traffic Legend</h3>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-4 h-1 bg-traffic-green"></div>
            <span className="text-xs">Low Traffic (0-10 vehicles)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-1 bg-traffic-yellow"></div>
            <span className="text-xs">Medium Traffic (11-20 vehicles)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-1 bg-traffic-red"></div>
            <span className="text-xs">High Traffic (20+ vehicles)</span>
          </div>
        </div>
        <div className="mt-3 pt-2 border-t">
          <div className="text-xs font-semibold mb-1">Signal States</div>
          <div className="flex gap-3">
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-traffic-green"></div>
              <span className="text-xs">Green</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-traffic-yellow"></div>
              <span className="text-xs">Yellow</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-traffic-red"></div>
              <span className="text-xs">Red</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Info Box */}
      <div className="absolute bottom-4 right-4 bg-white/90 backdrop-blur p-2 rounded-lg shadow-lg z-[1000]">
        <div className="text-xs text-gray-600">
          Powered by OpenStreetMap
        </div>
      </div>
    </div>
  );
};

export default TrafficMapOSM;
