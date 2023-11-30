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

**LCDOT welcomes any modifications or enhancements that can benefit the system and code will be 
periodically reviewed and merged.**

Contacts:
- [Ryan Legare (TMC Manger, Developer)](mailto:rlegare@lakecountyil.gov?subject=[GitHub%20Waze%20TT%20Poller]) 
- [Jon Nelson P.E. (Engineer of Traffic, ITS/Signals)](mailto:jpnelson@lakecountyil.govsubject=[GitHub%20Waze%20TT%20Poller])

---

### Links and resources

Waze for Cities (including sign-up): https://www.waze.com/wazeforcities/ \
Partner hub: https://www.waze.com/partnerhub/ \
Waze Traffic View: https://www.waze.com/partnerhub/tools-center/traffic-view/ \
Waze Traffic View tool and feed webinar: https://youtu.be/mxRKiRpi0mI \
Waze Traffic View tool and feed (old) [instructions](https://github.com/lakecountypassage/WazeTravelTimesPoller/blob/master/docs/Traffic%20View%20Tool%20and%20Feed.pdf)

---

### Tutorial Video
https://youtu.be/KxE7lL_kQV0

---

### Geting the Waze UID:

**Updated 2/2/2023**

You will need to get a Waze Traffic View UID for use with this program.
To get your Waze UID:
1. Sign up for Waze for Cities (formerly Waze CCP) - [Waze for Cities](https://www.waze.com/wazeforcities/)
2. Create a polygon of your area - [instructions](https://support.google.com/waze/partners/answer/10454161?hl=en)
2. Request access to the Waze **Traffic View tool** through the partner hub - [instructions](https://support.google.com/waze/partners/answer/10618174?hl=en&ref_topic=10616686)
5. Add routes through the Waze Traffic View website - [instructions](https://support.google.com/waze/partners/answer/7246755?hl=en#zippy=%2Croute-watchlist-feed)
6. Get the **UID or Feed ID** and keep that for the next steps. 
   7. Take note of the **whole feed URL**, if that's changed from the configuration below you will need that as well.

Example: `https://www.waze.com/partnerhub-api/feeds-tvt/?id=12345678987`

**Save this UID for the next steps**

![waze_feed_url_1](https://github.com/lakecountypassage/WazeTravelTimesPoller/blob/master/docs/waze_feed_url_1.jpg)


![waze_feed_url_2](https://github.com/lakecountypassage/WazeTravelTimesPoller/blob/master/docs/waze_feed_url_2.jpg)

---

### Using the program: 

To use this program there are several options:

On Windows:
1. Download the latest Zip file from here: [https://github.com/lakecountypassage/WazeTravelTimesPoller/releases](https://github.com/lakecountypassage/WazeTravelTimesPoller/releases)
2. Unzip the package
3. Update the values in the configs\config.ini file [instructions](#updating-the-config-file-)
    - Specifically, make sure you add in your travel times UID from Waze [instructions](#geting-the-waze-uid-)
4. Run the 'WazeTravelTimesPoller.exe' or 'run.bat' (this is a one-time pull of travel times)
5. (Optionally) Set a Windows Scheduled Task to run the program as often as you want travel times

-OR-

1. Download and install Python3
    - Make sure you add Python to system or user PATH
2. Download the program from [here](https://github.com/lakecountypassage/WazeTravelTimesPoller/archive/refs/heads/master.zip)
3. Unzip the package
4. Update the values in the configs\config.ini file [instructions](#updating-the-config-file-)
    - Specifically, make sure you add in your travel times UID from Waze [instructions](#geting-the-waze-uid-)
4. Run 'run.bat' or \src\main.py (this is a one-time pull of travel times)
5. (Optionally) Set a Windows Scheduled Task to run the program as often as you want travel times

#### Note: Windows limits scheduled tasks to 5min intervals. Waze updates their travel times in ~2min intervals. LCDOT uses Linux (Cron). If there are enough requests we can add a scheduled interval task to the program. In this case, you'd run the program and just keep it running, it would pull at whatever interval you set. This feature may be added later and the documentation will be updated accordingly. 

---

On Linux:
1. Download and install Python3
    - Make sure you add Python to system or user PATH
2. Download the program from [here](https://github.com/lakecountypassage/WazeTravelTimesPoller/archive/refs/heads/master.zip)
3. Unzip the package
4. Update the values in the configs\config.ini file [instructions](#updating-the-config-file-)
    - Specifically, make sure you add in your travel times UID from Waze [instructions](#geting-the-waze-uid-)
4. Run \src\main.py
5. (Optionally) Set a Cron job to run the program as often as you want travel times, below is 2 min interval

`*/2 * * * * cd /opt/waze/ && /opt/bin/python /opt/waze/src/main.py`

---

### Updating the config file:

**Updated 11/30/2023**

For Gmail email notification, you can use App Passwords provided by Google: https://support.google.com/accounts/answer/185833?sjid=9420807878265006177-NC#. In the configuration file, you would just use the App Password for in the password field. Leave OAuth false.

---

1. Update the [WazeURLPrefix] as necessary -- **DO NOT** add the UID here
2. Add your Waze UID/s to the [WazeUIDS] section -- this is a list, so you can just keep adding

![waze_config](https://github.com/lakecountypassage/WazeTravelTimesPoller/blob/master/docs/waze_config.jpg)

---

### Browsing the data:
1. Download and install [DB Browser for SQLite](https://sqlitebrowser.org/)
2. Open the database \database\waze_travel_times.db
3. Choose 'Browse data' and navigate to the table you want to look at

---

### TODO:
1. Add user interface for updating configs
2. Add built-in configurable scheduler (Windows limits to 5 minute minimum, may not be enough)
3. Add support for MSSQL
4. Build some queries for users to more easily query their data
