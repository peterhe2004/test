import requests
import json
import os

# SolarWinds server information
solarwinds_server = "https://solarwinds-server/SolarWinds/InformationService/v3/Json/"
username = "your_username"
password = "your_password"

# Device list for which we want to export running configs
devices = ["switch1", "switch2", "switch3"]  # Replace with your device names or IDs

# Directory to save configurations
config_directory = "configs/"
os.makedirs(config_directory, exist_ok=True)

# Fetch configuration function
def fetch_running_config(node_name):
    query = f"SELECT LastRunConfig.Config FROM NCM.ConfigArchive AS LastRunConfig WHERE LastRunConfig.NodeID = (SELECT NodeID FROM NCM.Nodes WHERE NodeName = '{node_name}')"
    response = requests.post(
        solarwinds_server + "Query",
        auth=(username, password),
        headers={"Content-Type": "application/json"},
        data=json.dumps({"query": query}),
        verify=False  # Use verify=True if you have valid SSL certificates
    )

    if response.status_code == 200:
        config_data = response.json()
        if config_data["results"]:
            return config_data["results"][0]["Config"]
        else:
            print(f"No configuration found for {node_name}")
            return None
    else:
        print(f"Error fetching configuration for {node_name}: {response.status_code}")
        return None

# Main loop to retrieve and save configurations
for device in devices:
    config = fetch_running_config(device)
    if config:
        file_path = os.path.join(config_directory, f"{device}_running_config.txt")
        with open(file_path, "w") as file:
            file.write(config)
        print(f"Configuration saved for {device} at {file_path}")
    else:
        print(f"Failed to retrieve configuration for {device}")
