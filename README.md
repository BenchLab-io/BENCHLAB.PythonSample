# BENCHLAB.PythonSample
A python-based script to communicate with the BENCHLAB hardware. 
This script is provided as-is and there is no guaranteee it will work at all.

Report bug and improvment request in Github at : https://github.com/BenchLab-io/BENCHLAB.PythonSample

For profesionnal partners, Labs and Benchmark-automation groups, feel free to contact us at contact@benchlab.io for premium & dedicated support as well as way to communicate with the Benchlab hardware.


# Benchlab
ILLUMINATE YOUR INSIGHTS | REAL-TIME SYSTEM TELEMETRY SOLUTION

BENCHLAB is a cutting-edge, compact, real-time system telemetry solution engineered for PC DIY enthusiasts.
It allows you to effortlessly monitor critical system metrics, including temperature, power usage, and voltage levels.
You can also manage system fan speeds. The telemetry data is displayed in the BENCHLAB software, and you can log and export data to a file or to HWiNFO.

Monitoring is available for:
- Power
- Voltage
- Temperature
- Humidity

BENCHLAB is available for purchase starting from December 29th, 2023 at benchlab.io.
![image](https://github.com/BenchLab-io/benchlab/assets/2151317/6aa9c95a-c936-4c4b-9b91-a81a62c2ebf7)

# Benchlab Software
The script/element available on this page is made to exclusively work with the Benchlab Hardware.

For a user-friendly software, please check : https://github.com/BenchLab-io/BENCHLAB 

# How to use this script with your BENCHLAB hardware 
Read the detailed blog post at : https://benchlab.io/blogs/technical/using-the-benchlab-python-example-code


## Run on MacOS (with Python from HomeBrew)
Once in the Benchlab folder of the script

If python was installed from Homebrew, a virtual environment is required
```
python3 -m venv venv
source venv/bin/activate
python3 -m pip install pyserial
```

Then run the python script

```
python3 benchlab.py
```


# FAQ
- How to report a bug?
> Use the Issue tab on this repo and provide as many information incl. computer OS + version / USB Port used on your computer / BENCHLAB and the command line you are trying to use.

# Changelog
All changelog will be available on the release page.

# Disclaimer
The Benchlab Team's goals are to provide a reliable and good user experience, keep in mind that bugs & limitations can still be present.
If you encounter a bug in the software, you can report it in the "issue" tab on github. If you need support 

To download the latest version, check the Releases tab.

## Benchlab is brought to you by The OpenBenchtable Project & ElmorLabs
