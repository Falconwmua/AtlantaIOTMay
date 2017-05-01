using Windows.UI.Xaml.Controls;

namespace ATLIOT
{
    public sealed partial class MainPage : Page
    {
        //
        // Note: this connection string is specific to the device "willpi". To configure other devices,
        // see information on iothub-explorer at http://aka.ms/iothubgetstartedVSCS
        //
        static string deviceCS = "<DeviceIOTHubConnectionStringCHANGEME>";
        static string deviceId = "<DeviceNameCHANGEME>";
        //
        // To monitor messages sent to device "willpi" use iothub-explorer as follows:
        //    iothub-explorer HostName=cedemo01ioth3ljkhlkg.azure-devices.net;SharedAccessKeyName=service;SharedAccessKey=+0aK10DNVaGceGgCGNR3WVuygbI0euCmv83WrxSDZt4= monitor-events "willpi"
        //

        // Refer to http://aka.ms/azure-iot-hub-vs-cs-wiki for more information on Connected Service for Azure IoT Hub


    }
}
