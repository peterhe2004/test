from ncclient import manager

# Replace these with your switch's IP, username, and password
switch_ip = "10.0.0.1"
username = "admin"
password = "password"

# Establish a NETCONF session
with manager.connect(
    host=switch_ip,
    port=830,
    username=username,
    password=password,
    hostkey_verify=False
) as m:
    # Get running configuration
    config = m.get_config(source="running")
    print(config.xml)
