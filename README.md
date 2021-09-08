# Waze Travel Times Poller
**Lake County Division of Transportation (Illinois)** - [Lake County DOT](https://www.lakecountyil.gov/transportation)

**Lake County PASSAGE** - [Lake County PASSAGE](https://www.lakecountypassage.com)

Disclaimer: This program was created for the Lake County PASSAGE system. The program provided as-is. Please use at your own discretion.

**As of August 28th, 2020 -- there was a database schema change. If you update the code and not the database structure,
the program will fail. Specfically, the 'routes' table has new text columns 'feed_id' and 'feed_name'. This is for better tracking of
multiple feeds.**

The purpose of this program is to help Waze CCP members process raw travel times data
provided by Waze. The program will get data from the Waze TT feed, process the data, archive it,
and send email alerts for any segments that are "congested".

This was originally built to work on Linux + Postgres, but we added support for SQLite, 
so it could be easily deployed on Windows or Linux. You can use this program without intalling any other dependecies or programs and it does not require a SQL server.

**Note: LCDOT welcomes any modifications or enhancements that can benefit the system and code will be 
periodically reviewed and merged.**

Contacts:
- [Ryan Legare (TMC Manger, Developer)](mailto:rlegare@lakecountyil.gov?subject=[GitHub%20Waze%20TT%20Poller]) 
- [Jon Nelson P.E. (Engineer of Traffic, ITS/Signals)](mailto:jpnelson@lakecountyil.govsubject=[GitHub%20Waze%20TT%20Poller])

---

**Links and resources**

Waze for Cities (including sign-up): https://www.waze.com/wazeforcities/

Partner dashboard: https://partnerdash.google.com/waze

Waze Traffic View: https://www.waze.com/trafficview/

Waze Traffiv View tool and feed webinar: https://youtu.be/mxRKiRpi0mI

Waze Traffic View tool and feed instructions: https://github.com/lakecountypassage/WazeTravelTimesPoller/blob/master/docs/Traffic%20View%20Tool%20and%20Feed.pdf

---

You will need to get a Waze Traffic View BUID for use with this program.
To get your Waze UID:
1. Signup for Waze for Cities (formerly Waze CCP)
2. Request access to the Waze **Traffic View tool** through the partner dashboard - [instructions](https://github.com/lakecountypassage/WazeTravelTimesPoller/blob/master/docs/Traffic%20View%20Tool%20and%20Feed.pdf)
3. Request access to the Waze **Traffic View Feed** through the partner dashboard - [instructions](https://github.com/lakecountypassage/WazeTravelTimesPoller/blob/master/docs/Traffic%20View%20Tool%20and%20Feed.pdf)
4. Add routes through the Waze Traffic View website - [instructions](https://github.com/lakecountypassage/WazeTravelTimesPoller/blob/master/docs/Traffic%20View%20Tool%20and%20Feed.pdf)
6. Get the **broadcasterId (BUID)** from the Traffic View Feed (from step #3). You will need the ID for this program. Follow the instructions on [page 7](https://github.com/lakecountypassage/WazeTravelTimesPoller/blob/master/docs/Traffic%20View%20Tool%20and%20Feed.pdf) to open the JSON feed (Chrome works best for this but any browser will work). You can take the unique 18 character alpha-numeric string after "buid=" in the URL --OR-- you can find the "broadcasterId" and take the JSON feed from there.

**Save this buid for the next steps**

![buid](https://github.com/lakecountypassage/WazeTravelTimesPoller/blob/master/docs/buid.png)
![broadcasterId](https://github.com/lakecountypassage/WazeTravelTimesPoller/blob/master/docs/broadcasterId.png)

---

To use this program there are several options:

On Windows:
1. Download the Zip file from here: [Release v0.4](https://github.com/lakecountypassage/WazeTravelTimesPoller/releases/download/0.4/WazeTravelTimesPoller.zip)
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

Note: Windows limits scheduled tasks to 5min intervals. Waze updates their travel times in ~2min intervals. LCDOT uses Linux (Cron). If there are enough requests we can add a scheduled interval task to the program. In this case, you'd run the program and just keep it running, it would pull at whatever interval you set. This feature may be added later and the documentation will be updated accordingly. 

---

On Linux:
1. Download and install Python3
    - Make sure you add Python to PATH
2. Download the program (source code)
3. Update the values in the configs\config.ini file
    - Specifically, make sure you add in your travel times BUID from Waze, 
        (see above for instructions on how to get this value)
4. Run \src\main.py
5. (Optionally) Set a Cron job to run the program as often as you want travel times, below is 2 min interval

`*/2 * * * * cd /opt/waze/ && /opt/bin/python /opt/waze/src/main.py`

---

To browse the data:
1. Download and install [DB Browser for SQLite](https://sqlitebrowser.org/)
2. Open the database \database\waze_travel_times.db
3. Choose 'Browse data' and navigate to the table you want to look at

---

TODO:
1. Add user interface for updating configs
2. Add built-in configurable scheduler (Windows limits to 5 minute minimum, may not be enough)
3. Add support for MSSQL
4. Build some queries for users to more easily query their data

---

**## README UNDER CONSTRUCTION ##**
