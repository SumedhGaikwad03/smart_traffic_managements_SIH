"""
env_sumo_rl.py - SUMO-based Traffic Environment for RL

This environment uses TraCI to interact with real SUMO simulations
using your actual network.net.xml and routes.rou.xml files.

State: Queue lengths on 4 incoming edges (n2c, s2c, e2c, w2c)
Action: 0 = NS green, 1 = EW green
Reward: -total_queue_length (minimize congestion)
"""

import os
import sys
import numpy as np
import traci
import traci.constants as tc


class SumoTrafficEnv:
    """
    Gym-like environment for SUMO traffic simulation
    
    Uses TraCI to control traffic lights and observe vehicle queues
    in real-time from actual SUMO network and route files.
    """
    
    def __init__(self, config_file: str, max_steps: int = 1000, 
                 gui: bool = False, delta_time: int = 5):
        """
        Initialize SUMO environment
        
        Args:
            config_file: Path to SUMO config file (e.g., 'myconfig.sumocfg')
            max_steps: Maximum simulation steps per episode
            gui: Whether to use SUMO GUI (True) or headless (False)
            delta_time: Simulation steps between RL decisions
        """
        # Check if SUMO is installed
        if 'SUMO_HOME' not in os.environ:
            raise EnvironmentError("SUMO_HOME environment variable not set. "
                                   "Please install SUMO and set SUMO_HOME.")
        
        self.config_file = config_file
        self.max_steps = max_steps
        self.gui = gui
        self.delta_time = delta_time
        
        # Traffic light ID from your network.net.xml
        self.tl_id = "center"
        
        # Incoming edges to the intersection (from your network)
        self.incoming_edges = ["n2c", "s2c", "e2c", "w2c"]
        
        # Action space: 2 phases
        # 0 = NS green (North-South), EW red
        # 1 = EW green (East-West), NS red
        self.n_actions = 2
        
        # State space: queue lengths on 4 edges
        self.n_states = 4
        
        # Phase definitions matching your network.net.xml tlLogic
        # Your network uses: "GGggrrrrGGggrrrr" for NS, "rrrrGGggrrrrGGgg" for EW
        # We'll use simplified 2-phase control
        self.phases = {
            0: 0,  # Phase index 0 in SUMO = NS green
            1: 2   # Phase index 2 in SUMO = EW green
        }
        
        # Simulation tracking
        self.current_step = 0
        self.sumo_running = False
        
        # Metrics
        self.total_waiting_time = 0
        self.total_queue_length = 0
        
    def reset(self):
        """
        Reset environment and start new SUMO simulation
        
        Returns:
            state: Initial state as numpy array
        """
        # Close existing SUMO instance if running
        if self.sumo_running:
            traci.close()
            self.sumo_running = False
        
        # Start SUMO - with proper path handling for Windows
        import subprocess
        
        # Try to find SUMO binary
        if 'SUMO_HOME' in os.environ:
            # Use SUMO_HOME if set
            sumo_home = os.environ['SUMO_HOME']
            if self.gui:
                sumo_binary = os.path.join(sumo_home, 'bin', 'sumo-gui')
            else:
                sumo_binary = os.path.join(sumo_home, 'bin', 'sumo')
            
            # Add .exe for Windows
            if sys.platform == "win32" and not sumo_binary.endswith('.exe'):
                sumo_binary += '.exe'
        else:
            # Fallback to PATH
            sumo_binary = "sumo-gui" if self.gui else "sumo"
        
        # Verify config file exists
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(
                f"Config file '{self.config_file}' not found in current directory.\n"
                f"Current directory: {os.getcwd()}\n"
                f"Make sure myconfig.sumocfg is in the same folder as your Python script."
            )
        
        # Build SUMO command
        sumo_cmd = [
            sumo_binary,
            "-c", self.config_file,
            "--waiting-time-memory", "1000",
            "--time-to-teleport", "-1",  # Disable teleporting
            "--no-step-log", "true",
            "--no-warnings", "true"
        ]
        
        # Try to start SUMO with better error handling
        try:
            print(f"Starting SUMO with command: {' '.join(sumo_cmd)}")
            traci.start(sumo_cmd)
            self.sumo_running = True
            print("SUMO started successfully!")
        except Exception as e:
            raise RuntimeError(
                f"Failed to start SUMO. Error: {e}\n\n"
                f"Troubleshooting:\n"
                f"1. Check SUMO is installed: Run 'sumo --version' in terminal\n"
                f"2. Check SUMO_HOME is set: {os.environ.get('SUMO_HOME', 'NOT SET')}\n"
                f"3. Check config file exists: {os.path.exists(self.config_file)}\n"
                f"4. Try running manually: sumo -c {self.config_file}\n"
            )
        
        # Initialize tracking variables
        self.current_step = 0
        self.total_waiting_time = 0
        self.total_queue_length = 0
        
        # Get initial state
        state = self._get_state()
        
        return state
    
    def step(self, action):
        """
        Execute action and advance simulation
        
        Args:
            action: 0 (NS green) or 1 (EW green)
        
        Returns:
            next_state: New state after action
            reward: Immediate reward
            done: Whether episode is finished
            info: Additional information dict
        """
        # Set traffic light phase based on action
        self._set_traffic_light_phase(action)
        
        # Run simulation for delta_time steps
        for _ in range(self.delta_time):
            traci.simulationStep()
            self.current_step += 1
        
        # Get new state
        next_state = self._get_state()
        
        # Calculate reward (negative queue length)
        queue_length = np.sum(next_state)
        self.total_queue_length += queue_length
        
        # Reward: negative total queue (lower is better)
        # Add penalty for very long queues (starvation prevention)
        reward = -float(queue_length)
        if queue_length > 15:
            reward -= 10  # Extra penalty for severe congestion
        
        # Calculate additional metrics
        waiting_time = self._get_total_waiting_time()
        self.total_waiting_time += waiting_time
        
        # Check if episode is done
        done = (self.current_step >= self.max_steps or 
                traci.simulation.getMinExpectedNumber() == 0)
        
        info = {
            'step': self.current_step,
            'queue_length': queue_length,
            'waiting_time': waiting_time,
            'total_queue': self.total_queue_length,
            'total_waiting': self.total_waiting_time
        }
        
        return next_state, reward, done, info
    
    def _get_state(self):
        """
        Get current state from SUMO
        
        Returns:
            state: Numpy array of queue lengths [n2c, s2c, e2c, w2c]
        """
        state = []
        for edge in self.incoming_edges:
            try:
                # Get number of halted vehicles on this edge
                halting = traci.edge.getLastStepHaltingNumber(edge)
                state.append(halting)
            except traci.exceptions.TraCIException:
                # Edge might not exist yet or no vehicles
                state.append(0)
        
        return np.array(state, dtype=np.float32)
    
    def _set_traffic_light_phase(self, action):
        """
        Set traffic light phase based on RL action
        
        Args:
            action: 0 (NS green) or 1 (EW green)
        """
        try:
            # Get SUMO phase index from action
            phase_index = self.phases[action]
            
            # Set the traffic light phase
            traci.trafficlight.setPhase(self.tl_id, phase_index)
            
            # Optional: set phase duration
            traci.trafficlight.setPhaseDuration(self.tl_id, self.delta_time)
            
        except traci.exceptions.TraCIException as e:
            print(f"Warning: Could not set traffic light phase: {e}")
    
    def _get_total_waiting_time(self):
        """
        Get total accumulated waiting time of all vehicles
        
        Returns:
            total_waiting_time: Sum of waiting times
        """
        waiting_time = 0
        for edge in self.incoming_edges:
            try:
                # Get all vehicles on this edge
                vehicles = traci.edge.getLastStepVehicleIDs(edge)
                for veh_id in vehicles:
                    waiting_time += traci.vehicle.getAccumulatedWaitingTime(veh_id)
            except traci.exceptions.TraCIException:
                pass
        
        return waiting_time
    
    def close(self):
        """Close SUMO simulation"""
        if self.sumo_running:
            traci.close()
            self.sumo_running = False
    
    def render(self):
        """Print current state (for debugging)"""
        if self.sumo_running:
            state = self._get_state()
            phase = traci.trafficlight.getPhase(self.tl_id)
            print(f"\nStep {self.current_step}")
            print(f"Queues - N: {state[0]:.0f}, S: {state[1]:.0f}, "
                  f"E: {state[2]:.0f}, W: {state[3]:.0f}")
            print(f"Current Phase: {phase}")
            print(f"Total Queue: {np.sum(state):.0f}")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.close()