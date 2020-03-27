CREATE TABLE `routes` (
	`rid`	INTEGER NOT NULL UNIQUE,
	`route_name`	TEXT NOT NULL,
	`route_from`	TEXT,
	`route_to`	TEXT,
	`type`	TEXT,
	`length`	INTEGER,
	PRIMARY KEY(`rid`)
);