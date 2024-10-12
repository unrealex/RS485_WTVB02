import device_model
import time


# Data update event
def updateData(DeviceModel):
    print(DeviceModel.deviceData)
    # Get the value of acceleration X
    # print(DeviceModel.get("AccX"))


if __name__ == "__main__":
    # List of Modbus addresses to be read
    addrLis = [0x50]
    # Get the device model
    device = device_model.DeviceModel("Test Device 1", "/dev/ttyUSB0", 230400, addrLis, updateData)
    # Turn on the device
    device.openDevice()
    # Enable loop reading
    device.startLoopRead()
