# BENCHLAB Python Example 20240130
# https://benchlab.io

import serial
import serial.tools.list_ports
from ctypes import *
from enum import IntEnum

# Constants
BENCHLAB_VENDOR_ID = 0xEE
BENCHLAB_PRODUCT_ID = 0x10
BENCHLAB_FIRMWARE_VERSION = 0x01 # Launch firmware
SENSOR_VIN_NUM = 13
SENSOR_POWER_NUM = 11
FAN_NUM = 9

# Structures
class VendorDataStruct(Structure):
    _fields_ = [
        ('VendorId', c_uint8),
        ('ProductId', c_uint8),
        ('FwVersion', c_uint8)
    ]

    def __str__(self):
        return f'VendorId: {hex(self.VendorId)}, ProductId: {hex(self.ProductId)}, FwVersion: {hex(self.FwVersion)}'


class PowerSensor(Structure):
    _fields_ = [
        ('Voltage', c_int16),
        ('Current', c_int32),
        ('Power', c_int32)
    ]

    def __str__(self):
        return f'Voltage: {self.Voltage}, Current: {self.Current}, Power: {self.Power}'


class FanSensor(Structure):
    _fields_ = [
        ('Enable', c_uint8),
        ('Duty', c_uint8),
        ('Tach', c_uint16)
    ]

    def __str__(self):
        return f'Enable: {self.Enable}, Tach: {self.Tach}, Duty: {self.Duty}'


class SensorStruct(Structure):
    _fields_ = [
        ('Vin', c_int16 * SENSOR_VIN_NUM),
        ('Vdd', c_uint16),
        ('Vref', c_uint16),
        ('Tchip', c_int16),
        ('Ts', c_int16 * 4),
        ('Tamb', c_int16),
        ('Hum', c_int16),
        ('FanSwitchStatus', c_uint8),
        ('RGBSwitchStatus', c_uint8),
        ('RGBExtStatus', c_uint8),
        ('FanExtDuty', c_uint8),
        ('PowerReadings', PowerSensor * SENSOR_POWER_NUM),
        ('Fans', FanSensor * FAN_NUM),
    ]

    def __str__(self):
        vin = ', '.join(str(v) for v in self.Vin)
        ts = ', '.join(str(t) for t in self.Ts)
        power_readings = ', '.join(str(p) for p in self.PowerReadings)
        fans = ', '.join(str(f) for f in self.Fans)
        return f'Vin: {vin}\nVdd: {self.Vdd}\nVref: {self.Vref}\nTchip: {self.Tchip}\nTs: {ts}\nTamb: {self.Tamb}\nHum: {self.Hum}\nFanExt: {self.FanExt}\nPowerReadings: {power_readings}\nFans: {fans}'

# Enums
class BENCHLAB_CMD(IntEnum):
    UART_CMD_WELCOME = 0
    UART_CMD_READ_SENSORS = 1
    UART_CMD_ACTION = 2
    UART_CMD_READ_NAME = 3
    UART_CMD_WRITE_NAME = 4
    UART_CMD_READ_FAN_PROFILE = 5
    UART_CMD_WRITE_FAN_PROFILE = 6
    UART_CMD_READ_RGB = 7
    UART_CMD_WRITE_RGB = 8
    UART_CMD_READ_CALIBRATION = 9
    UART_CMD_WRITE_CALIBRATION = 10
    UART_CMD_LOAD_CALIBRATION = 11
    UART_CMD_STORE_CALIBRATION = 12
    UART_CMD_READ_UID = 13
    UART_CMD_READ_VENDOR_DATA = 14

    # Function to get byte value
    def toByte(self):
        return self.value.to_bytes(1, byteorder='little')


# Find BENCHLAB Serial Port
print("\nFinding potential BENCHLAB Serial Ports...\n")
benchlab_ports = []
ports = serial.tools.list_ports.comports()

for port, desc, hwid in sorted(ports):
        # Check for VID=0483 and PID=5740
        if hwid.startswith('USB VID:PID=0483:5740'):
            print("{} - {}: {} [{}]".format(len(benchlab_ports), port, desc, hwid))
            benchlab_ports.append(port)
print("\n")

benchlab_port = 0
if len(benchlab_ports) == 0:
    print("No BENCHLAB Serial Ports found.")
    exit()

if len(benchlab_ports) > 1:
    print("Multiple BENCHLAB Serial Ports found. Input which port to use:")
    benchlab_port = int(input())
    if benchlab_port >= len(benchlab_ports):
        print("Invalid port index.")
        exit()

print(f"Using port index {benchlab_port} ({benchlab_ports[benchlab_port]})\n")

ser = serial.Serial(benchlab_ports[benchlab_port], 115200, timeout=1)

# Read "BENCHLAB" string
print("Reading welcome string...")
ser.write(BENCHLAB_CMD.UART_CMD_WELCOME.toByte())
buffer = ser.read(13)
assert buffer == b'BENCHLAB\x00'
print(f"Result: {buffer.decode('ascii')}\n")

# Check if firmware version is compatible
print("Reading vendor data...")
ser.write(BENCHLAB_CMD.UART_CMD_READ_VENDOR_DATA.toByte())
buffer = ser.read(3)
assert len(buffer) == 3
vendor_data = VendorDataStruct.from_buffer_copy(buffer)
print(f"Result: {vendor_data}\n")
assert vendor_data.VendorId == BENCHLAB_VENDOR_ID and vendor_data.ProductId == BENCHLAB_PRODUCT_ID

if(vendor_data.FwVersion != BENCHLAB_FIRMWARE_VERSION):
    print(f"Warning: Firmware version {hex(vendor_data.FwVersion)} may not be compatible with this script (for version {hex(BENCHLAB_FIRMWARE_VERSION)}).\n")
    # Wait for user input
    input("Press Enter to continue...")

print("Reading sensor values...")
ser.write(BENCHLAB_CMD.UART_CMD_READ_SENSORS.toByte())
buffer = ser.read(sizeof(SensorStruct))
assert len(buffer) == sizeof(SensorStruct)
print(f"Result: {len(buffer) == sizeof(SensorStruct)}\n")

sensor_struct = SensorStruct.from_buffer_copy(buffer)

power_readings = sensor_struct.PowerReadings
print("ATX24  ", "12V", "5V", "5VSB", "3.3V")
print("Voltage", power_readings[5].Voltage/1000, power_readings[3].Voltage/1000, power_readings[4].Voltage/1000, power_readings[2].Voltage/1000)
print("Current", power_readings[5].Current/1000, power_readings[3].Current/1000, power_readings[4].Current/1000, power_readings[2].Current/1000)
print("Power  ", power_readings[5].Power/1000, power_readings[3].Power/1000, power_readings[4].Power/1000, power_readings[2].Power/1000)
print("\n")

print("       ", "EPS1", "EPS2")
print("Voltage", power_readings[0].Voltage/1000, power_readings[1].Voltage/1000)
print("Current", power_readings[0].Current/1000, power_readings[1].Current/1000)
print("Power  ", power_readings[0].Power/1000, power_readings[1].Power/1000)
print("\n")

print("       ", "PCIE8_1", "PCIE8_2", "PCIE8_3", "HPWR1", "HPWR2")
print("Voltage", power_readings[6].Voltage/1000, power_readings[7].Voltage/1000, power_readings[8].Voltage/1000, power_readings[9].Voltage/1000, power_readings[10].Voltage/1000)
print("Current", power_readings[6].Current/1000, power_readings[7].Current/1000, power_readings[8].Current/1000, power_readings[9].Current/1000, power_readings[10].Current/1000)
print("Power  ", power_readings[6].Power/1000, power_readings[7].Power/1000, power_readings[8].Power/1000, power_readings[9].Power/1000, power_readings[10].Power/1000)
print("\n")

power_cpu = (power_readings[0].Power + power_readings[1].Power)/1000
power_gpu = (power_readings[6].Power + power_readings[7].Power + power_readings[8].Power + power_readings[9].Power + power_readings[10].Power)/1000
power_mb = (power_readings[2].Power + power_readings[3].Power + power_readings[4].Power + power_readings[5].Power)/1000
power_system = power_cpu + power_gpu + power_mb

print("       ", "System\t", "CPU\t", "GPU\t", "MB\t")
print("Power  ", f"{power_system:.0f}\t", f"{power_cpu:.0f}\t", f"{power_gpu:.0f}\t", f"{power_mb:.0f}\t")
print("\n")

print("    ", "TS1", "TS2", "TS3", "TS4", "TAMB", "HUM")
print("TEMP", sensor_struct.Ts[0]/10, sensor_struct.Ts[1]/10, sensor_struct.Ts[2]/10, sensor_struct.Ts[3]/10, sensor_struct.Tamb/10, sensor_struct.Hum/10)
print("\n")

print("FanExtDuty", sensor_struct.FanExtDuty, "FanSwitch", sensor_struct.FanSwitchStatus, "RGBSwitch", sensor_struct.RGBSwitchStatus, "RGBExt", sensor_struct.RGBExtStatus)

str_vin = ""
for i in range(0, SENSOR_VIN_NUM):
    str_vin += "VIN" + str(i) + " " + str(sensor_struct.Vin[i]/1000) + " "

print(str_vin)
print("\n")

fan_struct = sensor_struct.Fans

print("  ", "Enable", "Duty", "Tach")

for i in range(0, FAN_NUM):
    print("FAN"+str(i+1), fan_struct[i].Enable, fan_struct[i].Duty, fan_struct[i].Tach)

print("\n")

exit()

