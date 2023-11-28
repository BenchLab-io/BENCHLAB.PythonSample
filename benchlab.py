import serial
import time
from ctypes import *

# Constants
SENSOR_VIN_NUM = 13
SENSOR_POWER_NUM = 11
FAN_NUM = 9

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

ser = serial.Serial('COM8', 115200, timeout=1)

print("Test communication... ")

ser.write(b'\x00')
buffer = ser.read(13)
assert buffer == b'BENCHLAB\x00'

print("Read sensor values")
for i in range(0, 10000000):
    ser.write(b'\x01')
    buffer = ser.read(sizeof(SensorStruct))
    assert len(buffer) == sizeof(SensorStruct)

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

    print("       ", "Enable", "Duty", "Tach")

    for i in range(0, FAN_NUM):
        print("FAN"+str(i+1), fan_struct[i].Enable, fan_struct[i].Duty, fan_struct[i].Tach)

    print("\n")

    print("\n")

    time.sleep(1)

    '''ts1 = int.from_bytes(buffer[0:2], byteorder='little', signed='true')/10
    ts2 = int.from_bytes(buffer[2:4], byteorder='little', signed='true')/10
    tamb = int.from_bytes(buffer[4:6], byteorder='little', signed='true')/10
    hum = int.from_bytes(buffer[6:8], byteorder='little', signed='false')/10
    fext = int.from_bytes(buffer[8:9], byteorder='little', signed='false')
    vin = int.from_bytes(buffer[10:12], byteorder='little', signed='false')/100
    iin = int.from_bytes(buffer[12:14], byteorder='little', signed='false')/10

    fan_speeds = []
    for fan in range(0, 9):
        fan_speed = int.from_bytes(buffer[(14+fan*2):(16+fan*2)], byteorder='little', signed='false')
        fan_speeds.append(fan_speed)
    
    print(ts1, ts2, tamb, hum, fext, vin, iin, fan_speeds)'''

exit()

