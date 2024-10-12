3-Axis Vibrometer Data Reader

options:
  -h, --help           show this help message and exit
  --port PORT          Serial port location (e.g., /dev/ttyUSB0 or COM3)
  --baudrate BAUDRATE  Baud rate for the serial port (default: 230400)
  --max MAX            Number of messages to show min/max after processing (default: 500)
  --live               Show live decoded AX, AY, AZ, and CRC data
  --plot               Plot min/max AX, AY, AZ values after processing max messages
  --debug              Enable debug mode
  --line LINE          Draw a horizontal line at this value and its negative (e.g., --line 6.1)


Works in linux.
Check requirements.txt
