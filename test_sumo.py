import traci

SUMO_BINARY = "sumo"   # or "sumo-gui" if you want GUI
SUMO_CONFIG = "sumo_network/myconfig.sumocfg"
# update with your config file path

# Start SUMO with TraCI
traci.start([SUMO_BINARY, "-c", SUMO_CONFIG])

print("SUMO started successfully ✅")
print("Traffic lights:", traci.trafficlight.getIDList())
print("Vehicles:", traci.vehicle.getIDList())

# Step simulation a few times
for step in range(5):
    traci.simulationStep()
    print(f"Step {step}: Vehicles -> {traci.vehicle.getIDList()}")

traci.close()
print("Simulation finished ✅")
