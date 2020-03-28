CREATE TABLE "routes_congested" (
	"route_id"	INTEGER NOT NULL,
	"congested_date"	TEXT,
	"congested_time"	TEXT,
	"current_tt_min"	INTEGER,
	"historical_tt_min"	INTEGER,
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT
);