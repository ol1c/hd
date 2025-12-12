CREATE DATABASE MuseumDB
GO

USE MuseumDB
GO

CREATE TABLE Date (
	date_id INT IDENTITY(1,1) PRIMARY KEY,
	year INT,
	quater INT,
	month INT,
	day INT,
	day_name VARCHAR(20)
);

CREATE TABLE Time (
	time_id INT IDENTITY(1,1) PRIMARY KEY,
	hour INT,
	minute INT,
	second INT
);

CREATE TABLE Room (
	room_id INT IDENTITY(1,1) PRIMARY KEY,
	name VARCHAR(200),
	number INT,
	flor INT,
	effective_start_date DATE,
	effective_end_date DATE
);

CREATE TABLE Visitor (
	visitor_id INT IDENTITY(1,1) PRIMARY KEY,
	name VARCHAR(200)
);

CREATE TABLE Exhibition (
	exhibition_id INT IDENTITY(1,1) PRIMARY KEY,
	name VARCHAR(200) UNIQUE,
	start_date INT FOREIGN KEY REFERENCES Date(date_id),
	end_date INT FOREIGN KEY REFERENCES Date(date_id),
	avarage_value VARCHAR(200)
);

CREATE TABLE Exhibit (
	exhibit_id INT IDENTITY(1,1) PRIMARY KEY,
	number INT,
	name VARCHAR(200),
	author VARCHAR(200),
	creation_era VARCHAR(200),
	acquisition_duration VARCHAR(200),
	type VARCHAR(200),
	value VARCHAR(200),
	effective_start_date DATE,
	effective_end_date DATE
);

CREATE TABLE Visit (
	visit_id INT IDENTITY(1,1) PRIMARY KEY,
	date_id INT FOREIGN KEY REFERENCES Date(date_id),
	entry_time INT FOREIGN KEY REFERENCES Time(time_id),
	exit_time INT FOREIGN KEY REFERENCES Time(time_id),
	exhibition_id INT FOREIGN KEY REFERENCES Exhibition(exhibition_id),
	room_id INT FOREIGN KEY REFERENCES Room(room_id),
	visitor_id INT FOREIGN KEY REFERENCES Visitor(visitor_id),
	visit_duration INT,
	exhibits_total_value DECIMAL(10,2),
	exhibits_count INT
);

CREATE TABLE IsVisited (
	visit_id INT FOREIGN KEY REFERENCES Visit(visit_id),
	exhibit_id INT FOREIGN KEY REFERENCES Exhibit(exhibit_id)
);