# Waze Travel Times Poller
**Lake County Division of Transportation (Illinois)** - www.lakecountyil.gov/transportation

**Lake County PASSAGE** - www.lakecountypassage.com

Disclaimer: This program was created for the Lake County PASSAGE system. Please use at your own discretion.

The purpose of this program is to help Waze CCP members process raw travel times data
provided by Waze. The program will get data from the Waze TT feed, process the data, archive it,
and send email alerts for any segments that are "congested".

This was originally built to work on Linux + Postgres, but we scaled it back to use SQLite, 
so it could be easily deployed on Windows or Linux. The plan is to add support back for Postgres soon.

**Note: LCDOT welcomes any modifications or enhancements that can benefit the system and code will be 
periodically reviewed and merged.**

You will need to get a Waze Traffic View BUID for use with this program.
To get your Waze UID:
1. Signup for Waze for Cities (formerly Waze CCP)
2. Signup for access to the Waze Traffic View tool
3. Add routes through the Waze Traffic View website
4. Request your Traffic View Tool feed ID (BUID) from Waze (Contact support for your API UID)

---

To use this program there are several options:

On Windows:
1. Download the Zip file from here: https://github.com/lakecountypassage/WazeTravelTimesPoller/releases/download/0.1/WazeTravelTimesPoller.zip
2. Unzip the package
3. Update the values in the configs\config.ini file
    - Specifically, make sure you add in your travel times BUID from Waze, 
        (see above for instructions on how to get this value)
4. Run the 'WazeTravelTimesPoller.exe' or 'run.bat' (this is a one-time pull of travel times)
5. (Optionally) Set a Windows Scheduled Task to run the program as often as you want travel times

-OR-

1. Download and install Python3
    - Make sure you add Python to PATH
2. Download the program (source code)
3. Update the values in the configs\config.ini file
    - Specifically, make sure you add in your travel times BUID from Waze, 
        (see above for instructions on how to get this value)
4. Run 'run.bat' or \src\main.py (this is a one-time pull of travel times)
5. (Optionally) Set a Windows Scheduled Task to run the program as often as you want travel times

---


On Linux:
1. Download and install Python3
    - Make sure you add Python to PATH
2. Download the program (source code)
3. Update the values in the configs\config.ini file
    - Specifically, make sure you add in your travel times BUID from Waze, 
        (see above for instructions on how to get this value)
4. Run 'start.bat' or \src\main.py
5. (Optionally) Set a Cron job to run the program as often as you want travel times, below is 2 min interval

`*/2 * * * * cd /opt/waze/ && /opt/bin/python /opt/waze/src/main.py`

---

To browse the data:
1. Download and install 'DB Browser for SQLite' https://sqlitebrowser.org/
2. Open the database \database\waze_travel_times.db
3. Choose 'Browse data' and navigate to the table you want to look at

---

TODO:
1. Add user interface for updating configs
2. Add built-in configurable scheduler (Windows limits to 5 minute minimum, may not be enough)
3. Add back support for Postgres and MSSQL

---

**## README UNDER CONSTRUCTION ##**