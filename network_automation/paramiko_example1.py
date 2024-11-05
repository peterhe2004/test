import csv
import paramiko
import time

# Function to send commands to a device over SSH
def send_commands_to_device(hostname, ip, username, password, commands):
    try:
        # Set up SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password)

        # Start an interactive session
        shell = ssh.invoke_shell()
        for command in commands:
            shell.send(command + "\n")
            time.sleep(1)  # Wait for the command to execute
            output = shell.recv(65535).decode('utf-8')
            print(f"Output for {hostname} ({ip}):\n{output}")

        ssh.close()
    except Exception as e:
        print(f"Failed to connect to {hostname} ({ip}): {e}")

# Read devices from CSV
def read_devices_from_csv(filename):
    devices = []
    with open(filename, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            devices.append(row)
    return devices

# Main function to send commands to all devices
def main():
    devices = read_devices_from_csv('devices.csv')
    commands = [
        "show ip interface brief",
        "show version"
    ]

    for device in devices:
        send_commands_to_device(
            hostname=device['hostname'],
            ip=device['ip_address'],
            username=device['username'],
            password=device['password'],
            commands=commands
        )

if __name__ == "__main__":
    main()
