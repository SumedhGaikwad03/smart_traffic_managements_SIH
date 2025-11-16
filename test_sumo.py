import traci
import time

SUMO_BINARY = "sumo-gui"   # GUI version for visualization
SUMO_CONFIG = "sumo_network/myconfig.sumocfg"

try:
    # Start SUMO with TraCI
    traci.start([SUMO_BINARY, "-c", SUMO_CONFIG])
    
    print("SUMO started successfully ✅")
    print("Traffic lights:", traci.trafficlight.getIDList())
    print("Vehicles:", traci.vehicle.getIDList())
    
    # Step simulation many times to see cars move
    for step in range(300):
        try:
            traci.simulationStep()
            vehicle_count = traci.vehicle.getIDCount()
            print(f"Step {step}: {vehicle_count} vehicles active")
        except Exception as e:
            print(f"Error at step {step}: {e}")
            break
    
    print("Simulation finished ✅")

except traci.FatalTraCIError as e:
    print(f"TraCI Error: {e}")
    print("Closing simulation...")

except KeyboardInterrupt:
    print("\nSimulation interrupted by user")

finally:
    try:
        if traci.isLoaded():
            traci.close()
            print("TraCI connection closed")
    except:
        pass
    print("Done!")

