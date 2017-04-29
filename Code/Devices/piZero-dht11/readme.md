# Pi Zero W - Python with DHT11
This folder contains the sample code used to capture the temperature and humidity using a DHT11 sensor with Python and Azure IoT Hub.

## How to run the sample
In order to run the device samples you will first need the following prerequisites:
* [Setup your development environment][devbox-setup]
> Note: On Windows, it is recommended to install the **iothub-client** module package using pip (see link above).
* [Create an Azure IoT Hub instance][lnk-setup-iot-hub]
* [Create a device identity for your device][lnk-manage-iot-hub] and retreive the primary connection string for this device

Once you have a device identity for your sample,
* Clone this repo
* Navigate to the folder **device/piZero-dht11**
* Run the sample application using the following command to run the simple sample (replacing `<device connection string>` with the one generated previously):
    ```
	python pizerodht11.py -c < device connection string > -p < mqtt|http|amqp >
    ```
> You can get details on the options for the sample command line typing:
> `python pizerodht11.py -h`

## Helpful links
* [Azure IoT SDK Python][python-sdk]

[lnk-setup-iot-hub]: https://aka.ms/howtocreateazureiothub
[lnk-manage-iot-hub]: https://aka.ms/manageiothub
[devbox-setup]: https://github.com/Azure/azure-iot-sdk-python/blob/master/doc/python-devbox-setup.md
[python-sdk]: https://github.com/Azure/azure-iot-sdk-python
