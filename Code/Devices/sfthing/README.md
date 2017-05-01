# SparkFun ESP8266 Thing Dev Kit
This folder contains the sample code used to capture the temperature and humidity using a DHT sensor with C\C++ and Azure IoT Hub.

## Getting started
We're going to use the Remote Monitoring code from the Microsoft Azure IoT Starter Kit - SparkFun ESP8266 Thing Dev Kit as a starting point.
[The following guide will get you started][sfthing-azure-iot-kit]

The **remote-monitoring** folder in this repo has been slightly modifed for the Atlanta IoT May meeting to reduce the send rate and disable some of the other Azure Remote Monitoring demo functionality.

In the **remote-monitoring/iot_configs.h** file replace the following strings
* <SSID-CHANGEME>
* <SSID-PASSWORD-CHANGEME>
* <IOTHUB-DEVICE-CONNECTION-STRING-CHANGEME>

[sfthing-azure-iot-kit]:https://github.com/Azure-Samples/iot-hub-c-thingdev-getstartedkit