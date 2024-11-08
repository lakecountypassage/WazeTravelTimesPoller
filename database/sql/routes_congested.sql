CREATE TABLE `routes_congested` (
	`route_id`	INTEGER NOT NULL,
	`route_name`    TEXT,
	`route_from`	TEXT,
	`route_to`	TEXT,
	`congested_date_time`	TEXT,
	`current_tt_min`	INTEGER,
	`historical_tt_min`	INTEGER,
	`waze_irregular`	INTEGER,
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT
);