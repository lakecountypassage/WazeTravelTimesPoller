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

To use:
1. Download the program
2. Install Python3
    - Make sure you add Python to PATH
3. Update the values in the configs\config.ini file
    - Specifically, make sure you add in your travel times UID from Waze, 
    (see below for instructions on how to get this value)
4. Run the program
    - This can be done manually, Windows scheduled task, or Linux cron job
    
To get your Waze UID:
1. Signup for Waze for Cities (formerly Waze CCP)
2. Signup for access to the Waze Traffic View tool
3. Request your Traffic View Tool feed ID (BUID) from Waze

**## README UNDER CONSTRUCTION ##**