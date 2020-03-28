CREATE TABLE "travel_times" (
	"route_id"	INTEGER NOT NULL,
	"current_tt"	integer,
	"historical_tt"	integer,
	"current_tt_min"	integer,
	"historical_tt_min"	integer,
	"congested_bool"	integer,
	"congested_percent"	integer,
	"jam_level"	integer,
	"tt_date"	text,
	"tt_time"	text,
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT
);