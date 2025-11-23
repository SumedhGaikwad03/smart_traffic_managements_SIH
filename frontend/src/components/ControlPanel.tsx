import React, { useState } from "react";
import { motion } from "framer-motion";
import { BoltIcon } from "@heroicons/react/24/solid";
import { IntersectionData } from "../services/api";



import { ControlAction } from "../services/api";

interface ControlPanelProps {
  onSendControl: (payload: any) => void;
  lastControl: any;
  selectedIntersection: IntersectionData | null;
}

// replace any import of TrafficLightIcon with this inline component
// inline traffic-light SVG — zero dependency issues
const TrafficLightIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.2} strokeLinecap="round" strokeLinejoin="round" xmlns="http://www.w3.org/2000/svg">
    <rect x="8" y="3" width="8" height="18" rx="2" />
    <circle cx="12" cy="7.5" r="1.4" fill="currentColor" />
    <circle cx="12" cy="12" r="1.4" fill="currentColor" />
    <circle cx="12" cy="16.5" r="1.4" fill="currentColor" />
  </svg>
);


const ControlPanel: React.FC<ControlPanelProps> = ({
  onSendControl,
  lastControl,
  selectedIntersection
}) => {

  const [intersection, setIntersection] = useState("");
  const [signal, setSignal] = useState("GREEN");
  const [lastAction, setLastAction] = useState<ControlAction | null>(null);

  
  const fetchLast = async () => {
    const action = await lastControl();
    setLastAction(action);
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="bg-white rounded-lg shadow-lg p-6"
    >
      <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
        <BoltIcon className="w-6 h-6 text-blue-600" />
        Manual Control
      </h2>

      {/* Intersection Input */}
      <div className="mb-4">
        <label className="text-sm text-gray-700 font-medium">
          Intersection ID
        </label>
        <input
          className="mt-1 w-full border rounded-lg p-2 text-sm"
          placeholder="e.g. TLS1"
          value={intersection}
          onChange={(e) => setIntersection(e.target.value)}
        />
      </div>

      {/* Signal Selection */}
      <div className="mb-4">
  <label className="text-sm text-gray-700 font-medium">
    Signal State
  </label>

  <select
  className="mt-1 w-full border rounded-lg p-2 text-sm"
  value={signal}
  onChange={(e) => setSignal(e.target.value)}
>
  <option value="NS_GREEN">North–South Green</option>
  <option value="EW_GREEN">East–West Green</option>
  <option value="ALL_RED">All Red</option>
</select>

</div>

      {/* Send Button */}
      <button
  disabled={!selectedIntersection}
  onClick={() =>
    onSendControl({
      intersection: intersection || selectedIntersection?.id || "",

      action: signal
    })
  }
  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-2 rounded-lg"
>
  Apply Signal
</button>


      {/* Fetch Last Action */}
      <button
        onClick={fetchLast}
        className="w-full mt-3 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium py-2 rounded-lg"
      >
        Show Last Action
      </button>

      {/* Display Last Action */}
      {lastAction && (
        <div className="mt-4 p-3 bg-gray-100 rounded-lg text-sm">
          <p>
            <span className="font-medium">Intersection: </span>
            {lastAction.intersection}
          </p>
          <p>
            <span className="font-medium">Signal: </span>
            {lastAction.action}
          </p>
        </div>
      )}
    </motion.div>
  );
};

export default ControlPanel;
