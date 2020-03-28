CREATE TABLE "routes" (
	"route_id"	INTEGER NOT NULL UNIQUE,
	"route_name"	TEXT NOT NULL,
	"route_from"	TEXT,
	"route_to"	TEXT,
	"type"	TEXT,
	"length"	INTEGER,
	PRIMARY KEY("route_id")
);