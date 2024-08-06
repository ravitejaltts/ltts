# Introduction 
The IoT Service handles communication to/from the cloud, enabling command&control and passing telemetry data.

# Getting Started

This IOT Service now expects to have two json files in ../data
 this is planned to be sent from the platform eventually along with the pfx certs and other device information

`Telemetry_Config.json`

`Device_Config.json`

# Create the certs
Start with a .pfx file for the device  -

Conversion to separate PEM files
The naming the convention used is 
<device_id>_cert.pem   - this is the public cert
<device_id>_key.pem   - this is the private key and a pass phrase is created when it is extracted

Note: the current pfx files do not have a pass phrase to open

We can extract the private key from a PFX to a PEM file with this command:

    openssl pkcs12 -in filename.pfx -nocerts -out key.pem

Note: After asking for the password for the pfx which is blank for now  you will be asked to enter
A pass phrase for the key ( currently ‘1234’  in the Device_Config.json )
Enter the same pass phrase twice and the  key.pem created will use the one entered


Next:
Exporting the certificate only:   - we need this too

    openssl pkcs12 -in filename.pfx -clcerts -nokeys -out cert.pem



# Build and Test
TODO: Describe and show how to build your code and run the tests. 

# Contribute
