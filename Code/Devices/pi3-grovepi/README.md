# Pi 3 - Windows IoT Core GrovePi
This folder contains the sample code used to capture the temperature and humidity using a GrovePi and Seeed DHT sensor with C# and Azure IoT Hub.

## How to run the sample
In order to run the device samples you will first need the following prerequisites:
* Visual Studio 2015 or higher on Windows 10
* [Setup your development environment][devbox-setup]
* [Create an Azure IoT Hub instance][lnk-setup-iot-hub]
* [Create a device identity for your device][lnk-manage-iot-hub] and retreive the primary connection string for this device

Once you have a device identity for your sample,
* Clone this repo
* Navigate to the folder **device/pi3-grovepi/ATLIOT**
* Open the solution and replace **<DeviceIOTHubConnectionStringCHANGEME>** and **<DeviceNameCHANGEME>** with the one generated previously
* Update the target architecture
    * If you’re building for Minnowboard Max, select x86 in the Visual Studio toolbar architecture dropdown. If you’re building for Raspberry Pi 2 or 3 or the DragonBoard, select ARM.
* Navigate to the project properties (select ‘Properties’ in the Solution Explorer) and choose the ‘Debug’ tab on the left:
![alt text][proj-properties]
* Press F5 to start debugging the application.
* You should see the app come up on the IoT Core device screen

## Helpful links
* [Hello IoT Core][hello-world]

## Credits
* [Dexter Industries - Windows IoT and GrovePi][grovepi-ref]

[lnk-setup-iot-hub]: https://aka.ms/howtocreateazureiothub
[lnk-manage-iot-hub]: https://aka.ms/manageiothub
[devbox-setup]: https://developer.microsoft.com/en-us/windows/iot/getstarted
[proj-properties]: https://az835927.vo.msecnd.net/sites/iot/Resources/images/HelloWorld/cs-debug-project-properties.PNG
[hello-world]: https://developer.microsoft.com/en-us/windows/iot/samples/helloworld
[grovepi-ref]: https://www.dexterindustries.com/GrovePi/programming/getting-started-with-windows-iot-and-the-grovepi-winiot/