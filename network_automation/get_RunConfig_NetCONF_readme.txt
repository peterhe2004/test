Using ncclient (Python Library for NetConf)
The ncclient Python library is a popular choice for calling NetConf on Cisco devices, as it provides a simple interface to send NetConf commands.

Steps:
Install ncclient: You can install it with:

bash
Copy code
pip install ncclient
Enable NetConf on the Cisco 3850 Switch: Make sure NetConf is enabled on the switch:

plaintext
Copy code
enable
configure terminal
netconf-yang
end
Write a Python Script Using ncclient.