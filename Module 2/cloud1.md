# Setting up the cloud and connecting a IoT device

## IoT Hub

Create an IoT hub on Azure following this tutorial and register a demo device: https://learn.microsoft.com/en-us/azure/iot-hub/iot-hub-create-through-portal

Use the IoT Hub free tier.

## Create as sample device on your laptop

Create a simulated device running on your laptop similar to this example and run it. https://github.com/Azure/azure-iot-sdk-python/blob/main/samples/async-hub-scenarios/send_message.py
You just have to insert your connection string found on device properties found on the IoT Hub.

Using the IoT hub VSCode extension you can start monitoring the build in event endpoint and check that your messages are received by the IoT Hub. You have to make sure you are login to Azure in VSCode.

## Connect the RevPi as a IoT device to the IoT Hub

Using the setup from yesterday connect the RevPi to the IoT Hub and send messages with all the values read from the PLC.
For example you can read the values of the plc every second and send the data to the IoT hub every 20 seconds (this avoids hitting the daily message limit of 8000 of the free tier). Make sure you are sending the data in a format that can easily be used for further processing like json.

Again check that the messages are received by the IoT Hub.

## Create a Database

We are now receiving message on the IoT Hub and they are only stored temporarily until they are processed for up to 24 hours, so to store them permanently we need some kind of storage.
We are going to utilize a PostgreSQL database to store the recorded values. 
