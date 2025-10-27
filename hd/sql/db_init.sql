CREATE DATABASE VisitorTrack
GO

USE VisitorTrack
GO

CREATE TABLE Visitors (
    visitor_id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    visit_date DATE NOT NULL,
    entry_time DATETIME2 NOT NULL,
    exit_time DATETIME2 NOT NULL,

    CONSTRAINT ck_visitors_time_order CHECK (exit_time > entry_time),
    CONSTRAINT ck_visitors_same_day_entry CHECK (CAST(entry_time AS DATE) = visit_date),
    CONSTRAINT ck_visitors_same_day_exit CHECK (CAST(exit_time AS DATE) = visit_date)
);

CREATE TABLE Rooms (
    room_id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    floor INT NOT NULL
);

CREATE TABLE Exhibitions (
    exhibition_id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    exhibition_start DATE NOT NULL,
    exhibition_end DATE NOT NULL,
    room_id INT NOT NULL FOREIGN KEY REFERENCES Rooms(room_id),

    CONSTRAINT ck_exhibitions_dates CHECK (exhibition_end >= exhibition_start)
);

CREATE TABLE Exhibits (
    exhibit_id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    author VARCHAR(200)
);

CREATE TABLE Exhibit_Exhibitions (
    fk_exhibit_id INT NOT NULL,
    fk_exhibition_id INT NOT NULL,
    PRIMARY KEY (fk_exhibit_id, fk_exhibition_id),

    CONSTRAINT fk_exh_exhs_exhibit FOREIGN KEY (fk_exhibit_id) REFERENCES Exhibits(exhibit_id) ON DELETE CASCADE,
    CONSTRAINT fk_exh_exhs_exhibition FOREIGN KEY (fk_exhibition_id) REFERENCES Exhibitions(exhibition_id) ON DELETE CASCADE
);

CREATE TABLE Exhibition_visits (
    visit_id INT IDENTITY(1,1) PRIMARY KEY,
    visitor_id INT NOT NULL,
    exhibition_id INT NOT NULL,
    entry_time DATETIME2 NOT NULL,
    exit_time DATETIME2 NOT NULL,

    CONSTRAINT ck_exh_visits_time_order CHECK (exit_time > entry_time),
    CONSTRAINT fk_exh_visits_visitor FOREIGN KEY (visitor_id) REFERENCES Visitors(visitor_id) ON DELETE CASCADE,
    CONSTRAINT fk_exh_visits_exhibition FOREIGN KEY (exhibition_id) REFERENCES Exhibitions(exhibition_id) ON DELETE CASCADE
);