CREATE TABLE `routes_congested` (
	`rid`	INTEGER NOT NULL,
	`ddate`	TEXT,
	`ttime`	TEXT,
	`c_travel_time_min`	INTEGER,
	`h_travel_time_min`	INTEGER,
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT
);