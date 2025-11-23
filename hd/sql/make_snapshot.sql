USE master
GO

CREATE DATABASE VisitorTrack_Snapshot_1
ON
(
    NAME = VisitorTrack,
    FILENAME = 'C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\DATA\VisitorTrack_Snapshot_1.ss'
)
AS SNAPSHOT OF VisitorTrack;
GO

USE VisitorTrack
GO

INSERT INTO Exhibition_visits
("visitor_id", "exhibition_id", "entry_time", "exit_time") VALUES
(15, 4, '2025-10-27 12:12:34.0', '2025-10-27 12:20:27.0');

INSERT INTO Exhibitions
(name, exhibition_start, exhibition_end, room_id) VALUES
('Nice expo', '2025-12-01', '2025-12-31', 4)

UPDATE Rooms
SET name = 'Mega giga nice room'
WHERE room_id = 3
GO

USE master
GO

CREATE DATABASE VisitorTrack_Snapshot_2
ON
(
    NAME = VisitorTrack,
    FILENAME = 'C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\DATA\VisitorTrack_Snapshot_2.ss'
)
AS SNAPSHOT OF VisitorTrack;
GO

USE master

SELECT *
FROM VisitorTrack_Snapshot_1.dbo.Exhibition_visits AS a
RIGHT JOIN VisitorTrack_Snapshot_2.dbo.Exhibition_visits AS b
ON a.visit_id = b.visit_id
WHERE a.visit_id IS NULL;

SELECT *
FROM VisitorTrack_Snapshot_1.dbo.Exhibitions AS a
RIGHT JOIN VisitorTrack_Snapshot_2.dbo.Exhibitions AS b
ON a.exhibition_id = b.exhibition_id
WHERE a.room_id IS NULL;

SELECT a.room_id, a.name AS 'Old name', b.name AS 'New name', a.floor
FROM VisitorTrack_Snapshot_1.dbo.Rooms AS a
FULL OUTER JOIN VisitorTrack_Snapshot_2.dbo.Rooms AS b
ON a.room_id = b.room_id
WHERE a.name != b.name;
GO