# coding:UTF-8
import threading
import time
import serial
from serial import SerialException


# Serial Port Configuration
class SerialConfig:
    # Serial port number
    portName = ''

    # Baud rate
    baud = 9600


# Device instance
class DeviceModel:
    # region attributes

    # Device name
    deviceName = "My Device"

    # Device Modbus ID list
    addrLis = []

    # Device data dictionary
    deviceData = {}

    # Is the device open
    isOpen = False

    # Whether to loop read
    loop = False

    # Serial port
    serialPort = None

    # Serial port configuration
    serialConfig = SerialConfig()

    # Temporary array
    TempBytes = []

    # Start register
    statReg = None

    # endregion

    # region   Calculate CRC
    auchCRCHi = [
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
        0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
        0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01,
        0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81,
        0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
        0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01,
        0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
        0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
        0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01,
        0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
        0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
        0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01,
        0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
        0x40]

    auchCRCLo = [
        0x00, 0xC0, 0xC1, 0x01, 0xC3, 0x03, 0x02, 0xC2, 0xC6, 0x06, 0x07, 0xC7, 0x05, 0xC5, 0xC4,
        0x04, 0xCC, 0x0C, 0x0D, 0xCD, 0x0F, 0xCF, 0xCE, 0x0E, 0x0A, 0xCA, 0xCB, 0x0B, 0xC9, 0x09,
        0x08, 0xC8, 0xD8, 0x18, 0x19, 0xD9, 0x1B, 0xDB, 0xDA, 0x1A, 0x1E, 0xDE, 0xDF, 0x1F, 0xDD,
        0x1D, 0x1C, 0xDC, 0x14, 0xD4, 0xD5, 0x15, 0xD7, 0x17, 0x16, 0xD6, 0xD2, 0x12, 0x13, 0xD3,
        0x11, 0xD1, 0xD0, 0x10, 0xF0, 0x30, 0x31, 0xF1, 0x33, 0xF3, 0xF2, 0x32, 0x36, 0xF6, 0xF7,
        0x37, 0xF5, 0x35, 0x34, 0xF4, 0x3C, 0xFC, 0xFD, 0x3D, 0xFF, 0x3F, 0x3E, 0xFE, 0xFA, 0x3A,
        0x3B, 0xFB, 0x39, 0xF9, 0xF8, 0x38, 0x28, 0xE8, 0xE9, 0x29, 0xEB, 0x2B, 0x2A, 0xEA, 0xEE,
        0x2E, 0x2F, 0xEF, 0x2D, 0xED, 0xEC, 0x2C, 0xE4, 0x24, 0x25, 0xE5, 0x27, 0xE7, 0xE6, 0x26,
        0x22, 0xE2, 0xE3, 0x23, 0xE1, 0x21, 0x20, 0xE0, 0xA0, 0x60, 0x61, 0xA1, 0x63, 0xA3, 0xA2,
        0x62, 0x66, 0xA6, 0xA7, 0x67, 0xA5, 0x65, 0x64, 0xA4, 0x6C, 0xAC, 0xAD, 0x6D, 0xAF, 0x6F,
        0x6E, 0xAE, 0xAA, 0x6A, 0x6B, 0xAB, 0x69, 0xA9, 0xA8, 0x68, 0x78, 0xB8, 0xB9, 0x79, 0xBB,
        0x7B, 0x7A, 0xBA, 0xBE, 0x7E, 0x7F, 0xBF, 0x7D, 0xBD, 0xBC, 0x7C, 0xB4, 0x74, 0x75, 0xB5,
        0x77, 0xB7, 0xB6, 0x76, 0x72, 0xB2, 0xB3, 0x73, 0xB1, 0x71, 0x70, 0xB0, 0x50, 0x90, 0x91,
        0x51, 0x93, 0x53, 0x52, 0x92, 0x96, 0x56, 0x57, 0x97, 0x55, 0x95, 0x94, 0x54, 0x9C, 0x5C,
        0x5D, 0x9D, 0x5F, 0x9F, 0x9E, 0x5E, 0x5A, 0x9A, 0x9B, 0x5B, 0x99, 0x59, 0x58, 0x98, 0x88,
        0x48, 0x49, 0x89, 0x4B, 0x8B, 0x8A, 0x4A, 0x4E, 0x8E, 0x8F, 0x4F, 0x8D, 0x4D, 0x4C, 0x8C,
        0x44, 0x84, 0x85, 0x45, 0x87, 0x47, 0x46, 0x86, 0x82, 0x42, 0x43, 0x83, 0x41, 0x81, 0x80,
        0x40]

    # endregion  Calculate CRC

    def __init__(self, deviceName, portName, baud, addrLis, callback_method):
        print("Initializing device model")
        # Device name (customized)
        self.deviceName = deviceName
        # Serial port number
        self.serialConfig.portName = portName
        # Baud rate
        self.serialConfig.baud = baud
        # Modbus ID device address
        self.addrLis = addrLis
        self.deviceData = {}
        # Data callback method
        self.callback_method = callback_method
        # Initialize device data dictionary
        for addr in addrLis:
            self.deviceData[addr] = {}

    # Get CRC check
    def get_crc(self, datas, dlen):
        tempH = 0xff  # High CRC byte initialization
        tempL = 0xff  # Low CRC byte initialization
        for i in range(0, dlen):
            tempIndex = (tempH ^ datas[i]) & 0xff
            tempH = (tempL ^ self.auchCRCHi[tempIndex]) & 0xff
            tempL = self.auchCRCLo[tempIndex]
        return (tempH << 8) | tempL
        pass

    # region Obtain device data

    # Set device data
    def set(self, ADDR, key, value):
        # Save device data to key values
        self.deviceData[ADDR][key] = value

    # Obtain device data
    def get(self, ADDR, key):
        # Get data from key values, return None if not found
        if ADDR in self.deviceData:
            if key in self.deviceData[ADDR]:
                return self.deviceData[ADDR][key]
            else:
                return None
        else:
            return None

    # Delete device data
    def remove(self, ADDR, key):
        # Delete device key values
        if ADDR in self.deviceData:
            if key in self.deviceData[ADDR]:
                del self.deviceData[ADDR][key]

    # endregion

    # Open device
    def openDevice(self):
        # First close the port
        self.closeDevice()
        try:
            self.serialPort = serial.Serial(self.serialConfig.portName, self.serialConfig.baud, timeout=0.5)
            self.isOpen = True
            print("{} is open".format(self.serialConfig.portName))
            # Start a thread to continuously listen to serial port data
            t = threading.Thread(target=self.readDataTh, args=("Data-Received-Thread", 10,))
            t.start()
            print("Device opened successfully")
        except SerialException:
            print("Failed to open " + self.serialConfig.portName)

    # Listening to serial data threads
    def readDataTh(self, threadName, delay):
        print("Starting " + threadName)
        while True:
            # If the serial port is open
            if self.isOpen:
                try:
                    tLen = self.serialPort.inWaiting()
                    if tLen > 0:
                        data = self.serialPort.read(tLen)
                        self.onDataReceived(data)
                except Exception as ex:
                    print(ex)
            else:
                time.sleep(0.1)
                print("Serial port is not open")
                break

    # Close device
    def closeDevice(self):
        if self.serialPort is not None:
            self.serialPort.close()
            print("Port closed")
        self.isOpen = False
        print("Device closed")
    
    # region Data analysis

    # Serial port data processing
    def onDataReceived(self, data):
        
        hex_data = ' '.join(format(byte, '02X') for byte in data)
        print(f"Received data: {hex_data}")
        tempdata = bytes.fromhex(data.hex())
        for val in tempdata:
            self.TempBytes.append(val)
            # Determine if the ID is correct
            if self.TempBytes[0] not in self.addrLis:
                del self.TempBytes[0]
                continue
            # Determine whether it is 03 to read the function code
            if len(self.TempBytes) > 2:
                if not (self.TempBytes[1] == 0x03):
                    del self.TempBytes[0]
                    continue
                tLen = len(self.TempBytes)
                # Get a complete package of protocol data
                if tLen == self.TempBytes[2] + 5:
                    # CRC check
                    tempCrc = self.get_crc(self.TempBytes, tLen - 2)
                    if (tempCrc >> 8) == self.TempBytes[tLen - 2] and (tempCrc & 0xff) == self.TempBytes[tLen - 1]:
                        self.processData(self.TempBytes[2])
                    else:
                        del self.TempBytes[0]

    # Data analysis
    def processData(self, length):
        # Data parsing
        ADDR = self.TempBytes[0]
        if length == 24:
            AccX = self.getSignInt16(self.TempBytes[3] << 8 | self.TempBytes[4]) / 32768 * 16
            AccY = self.getSignInt16(self.TempBytes[5] << 8 | self.TempBytes[6]) / 32768 * 16
            AccZ = self.getSignInt16(self.TempBytes[7] << 8 | self.TempBytes[8]) / 32768 * 16
            self.set(ADDR, "AccX", round(AccX, 3))
            self.set(ADDR, "AccY", round(AccY, 3))
            self.set(ADDR, "AccZ", round(AccZ, 3))

            AsX = self.getSignInt16(self.TempBytes[9] << 8 | self.TempBytes[10]) / 32768 * 2000
            AsY = self.getSignInt16(self.TempBytes[11] << 8 | self.TempBytes[12]) / 32768 * 2000
            AsZ = self.getSignInt16(self.TempBytes[13] << 8 | self.TempBytes[14]) / 32768 * 2000
            self.set(ADDR, "AsX", round(AsX, 3))
            self.set(ADDR, "AsY", round(AsY, 3))
            self.set(ADDR, "AsZ", round(AsZ, 3))

            HX = self.getSignInt16(self.TempBytes[15] << 8 | self.TempBytes[16]) * 13 / 1000
            HY = self.getSignInt16(self.TempBytes[17] << 8 | self.TempBytes[18]) * 13 / 1000
            HZ = self.getSignInt16(self.TempBytes[19] << 8 | self.TempBytes[20]) * 13 / 1000
            self.set(ADDR, "HX", round(HX, 3))
            self.set(ADDR, "HY", round(HY, 3))
            self.set(ADDR, "HZ", round(HZ, 3))

            AngX = self.getSignInt16(self.TempBytes[21] << 8 | self.TempBytes[22]) / 32768 * 180
            AngY = self.getSignInt16(self.TempBytes[23] << 8 | self.TempBytes[24]) / 32768 * 180
            AngZ = self.getSignInt16(self.TempBytes[25] << 8 | self.TempBytes[26]) / 32768 * 180
            self.set(ADDR, "AngX", round(AngX, 3))
            self.set(ADDR, "AngY", round(AngY, 3))
            self.set(ADDR, "AngZ", round(AngZ, 3))
            self.callback_method(self)
        else:
            if self.statReg is not None:
                for i in range(int(length / 2)):
                    value = self.getSignInt16(self.TempBytes[2 * i + 3] << 8 | self.TempBytes[2 * i + 4])
                    value = value / 32768
                    self.set(ADDR, str(self.statReg), round(value, 3))
                    self.statReg += 1
        self.TempBytes.clear()

    # endregion

    @staticmethod
    def getSignInt16(num):
        if num >= pow(2, 15):
            num -= pow(2, 16)
        return num

    @staticmethod
    def getSignInt32(num):
        if num >= pow(2, 31):
            num -= pow(2, 32)
        return num

    # Sending serial port data
    def sendData(self, data):
        try:
            hex_data = ' '.join(format(byte, '02X') for byte in data)
            print(f"Transmitting data: {hex_data}")
            self.serialPort.write(data)
        except Exception as ex:
            print(ex)

    # Read register
    def readReg(self, ADDR, regAddr, regCount):
        # Get start register from instruction (used for handling returned data)
        self.statReg = regAddr
        # Encapsulate read instructions and send data to the serial port
        self.sendData(self.get_readBytes(ADDR, regAddr, regCount))

    # Write Register
    def writeReg(self, ADDR, regAddr, sValue):
        # Unlock
        self.unlock(ADDR)
        # Delay 100ms
        time.sleep(0.1)
        # Encapsulate write instructions and send data to the serial port
        self.sendData(self.get_writeBytes(ADDR, regAddr, sValue))
        # Delay 100ms
        time.sleep(0.1)
        # Save
        self.save(ADDR)

    # Send read instruction encapsulation
    def get_readBytes(self, devid, regAddr, regCount):
        # Initialization
        tempBytes = [None] * 8
        # Device modbus address
        tempBytes[0] = devid
        # Read function code
        tempBytes[1] = 0x03
        # High 8 bits of register
        tempBytes[2] = regAddr >> 8
        # Low 8 bits of register
        tempBytes[3] = regAddr & 0xff
        # High 8 bits of register count
        tempBytes[4] = regCount >> 8
        # Low 8 bits of register count
        tempBytes[5] = regCount & 0xff
        # Get CRC check
        tempCrc = self.get_crc(tempBytes, len(tempBytes) - 2)
        # High 8 bits of CRC check
        tempBytes[6] = tempCrc >> 8
        # Low 8 bits of CRC check
        tempBytes[7] = tempCrc & 0xff
        return tempBytes

    # Send write instruction encapsulation
    def get_writeBytes(self, devid, regAddr, sValue):
        # Initialization
        tempBytes = [None] * 8
        # Device modbus address
        tempBytes[0] = devid
        # Write function code
        tempBytes[1] = 0x06
        # High 8 bits of register
        tempBytes[2] = regAddr >> 8
        # Low 8 bits of register
        tempBytes[3] = regAddr & 0xff
        # High 8 bits of register value
        tempBytes[4] = sValue >> 8
        # Low 8 bits of register value
        tempBytes[5] = sValue & 0xff
        # Get CRC check
        tempCrc = self.get_crc(tempBytes, len(tempBytes) - 2)
        # High 8 bits of CRC check
        tempBytes[6] = tempCrc >> 8
        # Low 8 bits of CRC check
        tempBytes[7] = tempCrc & 0xff
        return tempBytes

    # Start loop reading
    def startLoopRead(self):
        # Loop read control
        self.loop = True
        # Enable read thread
        t = threading.Thread(target=self.loopRead, args=())
        t.start()

    # Loop reading thread
    def loopRead(self):
        print("Loop reading started")
        while self.loop:
            for addr in self.addrLis:
                self.readReg(addr, 0x34, 12) 
                time.sleep(0.2)
        print("Loop reading ended")

    # Stop loop reading
    def stopLoopRead(self):
        self.loop = False

    # Unlock
    def unlock(self, ADDR):
        cmd = self.get_writeBytes(ADDR, 0x69, 0xb588)
        self.sendData(cmd)

    # Save
    def save(self, ADDR):
        cmd = self.get_writeBytes(ADDR, 0x00, 0x0000)
        self.sendData(cmd)
