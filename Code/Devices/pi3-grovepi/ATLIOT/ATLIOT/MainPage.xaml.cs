// Copyright (c) Microsoft. All rights reserved.

using System;
using System.Text;
using Windows.UI.Xaml.Controls;
using Microsoft.Azure.Devices.Client;
using GrovePi;
using GrovePi.Sensors;
using System.Threading;
using Newtonsoft.Json;


namespace ATLIOT
{
    public sealed partial class MainPage : Page
    {
        // Connect DHT Temperature and humidity Sensor to port D5
        IDHTTemperatureAndHumiditySensor sensor = DeviceFactory.Build.DHTTemperatureAndHumiditySensor(Pin.DigitalPin7, DHTModel.Dht11);

        // IOT Hub Device
        static DeviceClient deviceClient;

        private Timer periodicTimer;

        public MainPage()
        {
            InitializeComponent();

            deviceClient = DeviceClient.CreateFromConnectionString(deviceCS, TransportType.Http1);
            periodicTimer = new Timer(this.TimerCallBack, null, 0, 60000);
        
        }

        private void TimerCallBack(object state)
        {
            try
            {
                // Check the value of the Sensor.
                // Temperature in Celsius is returned as a double type.  Convert it to string so we can print it.
                sensor.Measure();
                string sensortemp = sensor.TemperatureInFahrenheit.ToString();
                // Same for Humidity.  
                string sensorhum = sensor.Humidity.ToString();
                
                // Print all of the values to the debug window.  
                System.Diagnostics.Debug.WriteLine("Temp is " + sensortemp + " F.  And the Humidity is " + sensorhum + "%. ");

                /* UI updates must be invoked on the UI thread */
                var task = this.Dispatcher.RunAsync(Windows.UI.Core.CoreDispatcherPriority.Normal, () =>
                {
                    Text_Temperature.Text = "Temperature: " + sensortemp + "F";
                    Text_Humidity.Text = "Humidity: " + sensorhum + "%";
                });
                
                SendDeviceToCloudMessageAsync( Convert.ToInt32(sensor.Humidity), Convert.ToInt32(sensor.TemperatureInCelsius));
                
            }
            catch (Exception ex) 
            {
                
                // If you want to see the exceptions uncomment the following:
                System.Diagnostics.Debug.WriteLine(ex.ToString());
            }
        }       

        static async void SendDeviceToCloudMessageAsync(int humidity, int temperature)
        {
            var telemetryDataPoint = new
            {
                deviceId = deviceId,
                humidity = humidity,
                temperature = temperature
            };
            var messageString = JsonConvert.SerializeObject(telemetryDataPoint);
            var message = new Message(Encoding.ASCII.GetBytes(messageString));

            await deviceClient.SendEventAsync(message);
        }
    }
}
