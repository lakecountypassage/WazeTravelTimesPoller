CREATE TABLE `travel_times` (
	`rid`	INTEGER NOT NULL,
	`c_travel_time`	integer,
	`h_travel_time`	integer,
	`c_travel_time_min`	integer,
	`h_travel_time_min`	integer,
	`congested`	integer,
	`congested_percent`	integer,
	`jam_level`	integer,
	`date`	text,
	`time`	text,
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT
);