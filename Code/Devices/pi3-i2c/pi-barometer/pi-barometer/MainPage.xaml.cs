using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Linq;
using System.Runtime.InteropServices.WindowsRuntime;
using Windows.Foundation;
using Windows.Foundation.Collections;
using Windows.UI.Xaml;
using Windows.UI.Xaml.Controls;
using Windows.UI.Xaml.Controls.Primitives;
using Windows.UI.Xaml.Data;
using Windows.UI.Xaml.Input;
using Windows.UI.Xaml.Media;
using Windows.UI.Xaml.Navigation;
using Windows.UI.Core;
using Microsoft.Azure.Devices.Client;
using Newtonsoft.Json;

// The Blank Page item template is documented at http://go.microsoft.com/fwlink/?LinkId=402352&clcid=0x409

namespace pi_barometer
{
    /// <summary>
    /// An empty page that can be used on its own or navigated to within a Frame.
    /// </summary>
    public sealed partial class MainPage : Page
    {
        private Bmp180Sensor _bmp180;
        private Timer _periodicTimer;

        private const string _deviceId = "pi3i2c";
        private DeviceClient _deviceClient = null;
        private const string _deviceConnectionString = "{IoTHub-ConnectionString-Here}";

        public MainPage()
        {
            this.InitializeComponent();
            // Register for the unloaded event so we can clean up upon exit
            Unloaded += MainPage_Unloaded;

            // Initialize the Sensors
            InitializeSensors();

            // create device client for iot hub
            _deviceClient = DeviceClient.CreateFromConnectionString(_deviceConnectionString, TransportType.Mqtt);

            // start the timer
            _periodicTimer = new Timer(this.TimerCallback, null, 0, 60000);
            var task = this.Dispatcher.RunAsync(CoreDispatcherPriority.Normal, () =>
            {
                button.Content = "Stop Reading Sensor";
            });
        }

        private void MainPage_Unloaded(object sender, object args)
        {
            /* Cleanup */
            _bmp180.Dispose();
        }

        private async void InitializeSensors()
        {
            string calibrationData;

            // Initialize the BMP180 Sensor
            try
            {
                _bmp180 = new Bmp180Sensor();
                await _bmp180.InitializeAsync();
                calibrationData = _bmp180.CalibrationData.ToString();
            }
            catch (Exception ex)
            {
                calibrationData = "Device Error! " + ex.Message;
            }

            var task = this.Dispatcher.RunAsync(CoreDispatcherPriority.Normal, () =>
            {
                calibrationDataTextBlock.Text = calibrationData;
            });
        }

        private void button_Click(object sender, RoutedEventArgs e)
        {
            if (_bmp180 == null)
                return;


            if (_periodicTimer == null)
            {
                _periodicTimer = new Timer(this.TimerCallback, null, 0, 60000);
                var task = this.Dispatcher.RunAsync(CoreDispatcherPriority.Normal, () =>
                {
                    button.Content = "Stop Reading Sensor";
                });
            }
            else
            {
                _periodicTimer.Dispose();
                var task = this.Dispatcher.RunAsync(CoreDispatcherPriority.Normal, () =>
                {
                    button.Content = "Get Sensor Readings";
                });
                _periodicTimer = null;
            }
        }

        private async void TimerCallback(object state)
        {
            string temperatureText, pressureText;

            // Read and format Sensor data
            try
            {
                var sensorData = await _bmp180.GetSensorDataAsync(Bmp180AccuracyMode.UltraHighResolution);
                temperatureText = sensorData.Temperature.ToString("F1");
                pressureText = sensorData.Pressure.ToString("F2");
                temperatureText += "C - hex:" + BitConverter.ToString(sensorData.UncompestatedTemperature);
                pressureText += "hPa - hex:" + BitConverter.ToString(sensorData.UncompestatedPressure);

                // build the message object for the iot hub
                iotHubMessage.Message msg = new iotHubMessage.Message();
                msg.deviceid = _deviceId;
                msg.temperatureC = sensorData.Temperature;
                msg.humidity = 0.0;
                msg.pressure = sensorData.Pressure * 0.02952998751;

                // prepare the message
                string sensordata = JsonConvert.SerializeObject(msg);
                Message iotmsg = new Message(System.Text.Encoding.UTF8.GetBytes(sensordata));

                // send the message
                await _deviceClient.SendEventAsync(iotmsg);
            }
            catch (Exception ex)
            {
                temperatureText = "Sensor Error: " + ex.Message;
                pressureText = "Sensor Error: " + ex.Message;
            }

            // UI updates must be invoked on the UI thread
            var task = this.Dispatcher.RunAsync(CoreDispatcherPriority.Normal, () =>
            {
                temperatureTextBlock.Text = temperatureText;
                pressureTextBlock.Text = pressureText;
            });
        }
    }
}
