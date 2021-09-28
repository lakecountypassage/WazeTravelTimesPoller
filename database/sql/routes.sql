CREATE TABLE "routes" (
	"route_id"	INTEGER NOT NULL UNIQUE,
	"route_name"	TEXT NOT NULL,
	"route_from"	TEXT,
	"route_to"	TEXT,
	"type"	TEXT,
	"length"	INTEGER,
	`feed_id`	TEXT,
	`feed_name`	TEXT,
	`deleted`	INTEGER,
	`lines`	TEXT,
	PRIMARY KEY("route_id")
);