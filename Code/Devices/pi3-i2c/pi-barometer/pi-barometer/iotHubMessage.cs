using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace pi_barometer
{
    class iotHubMessage
    {
        public class Message
        {
            public string deviceid { get; set; }
            public double temperatureC { get; set; }
            public double humidity { get; set; }
            public double pressure { get; set; }
        }
    }
}
