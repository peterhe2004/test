Method 1: Use SNMP to Trigger a TFTP Copy of the Running Configuration
This approach works by instructing the Cisco switch, through SNMP, to copy its running configuration to a TFTP server that you control.

Requirements
TFTP Server: Set up a TFTP server on your network to receive the configuration files.
SNMP Write Access: Ensure you have SNMP write access on the switch, as this method requires setting values via SNMP.
Steps
Set Up the TFTP Server: Ensure your TFTP server is reachable by all switches and has permissions configured to allow file storage from them.

Identify the SNMP OIDs for the TFTP Copy:

Cisco switches use specific SNMP OIDs to trigger TFTP copies. The typical OID used is in the CISCO-CONFIG-COPY-MIB.
Common OIDs include:
ccCopyProtocol (1.3.6.1.4.1.9.9.96.1.1.1.1.2): Set this to 1 for TFTP.
ccCopySourceFileType (1.3.6.1.4.1.9.9.96.1.1.1.1.3): Set this to 4 for running-config.
ccCopyDestFileType (1.3.6.1.4.1.9.9.96.1.1.1.1.4): Set this to 1 for network file.
ccCopyServerAddress (1.3.6.1.4.1.9.9.96.1.1.1.1.5): The IP address of the TFTP server.
ccCopyFileName (1.3.6.1.4.1.9.9.96.1.1.1.1.6): The filename to save the configuration as.
ccCopyEntryRowStatus (1.3.6.1.4.1.9.9.96.1.1.1.1.14): Set to 1 to trigger the copy operation.
Write a Python Script to Trigger the Copy: Here’s a Python script using pysnmp to send the SNMP set commands:

python
Copy code
from pysnmp.hlapi import *

def snmp_set(target, community, oid, value, value_type):
    return next(
        setCmd(SnmpEngine(),
               CommunityData(community, mpModel=0),
               UdpTransportTarget((target, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid), value_type(value)))
    )

# Switch and TFTP settings
switch_ip = "10.0.0.1"
community = "private"
tftp_ip = "10.0.0.2"
file_name = "switch_running_config.cfg"

# SNMP OID values for TFTP copy
snmp_set(switch_ip, community, '1.3.6.1.4.1.9.9.96.1.1.1.1.2.100', 1, Integer)  # TFTP
snmp_set(switch_ip, community, '1.3.6.1.4.1.9.9.96.1.1.1.1.3.100', 4, Integer)  # Running-config
snmp_set(switch_ip, community, '1.3.6.1.4.1.9.9.96.1.1.1.1.4.100', 1, Integer)  # Network file
snmp_set(switch_ip, community, '1.3.6.1.4.1.9.9.96.1.1.1.1.5.100', tftp_ip, IpAddress)  # TFTP server IP
snmp_set(switch_ip, community, '1.3.6.1.4.1.9.9.96.1.1.1.1.6.100', file_name, OctetString)  # File name
snmp_set(switch_ip, community, '1.3.6.1.4.1.9.9.96.1.1.1.1.14.100', 1, Integer)  # Trigger copy

print("Triggered TFTP copy of running-config to the server.")
Run the Script: Running this script should initiate a TFTP transfer of the switch’s running configuration to the specified TFTP server and filename.