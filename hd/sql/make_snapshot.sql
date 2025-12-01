USE master
GO

IF EXISTS (SELECT 1 FROM sys.databases WHERE name = 'VisitorTrack_Snapshot_1')
    DROP DATABASE VisitorTrack_Snapshot_1;
GO

IF EXISTS (SELECT 1 FROM sys.databases WHERE name = 'VisitorTrack_Snapshot_2')
    DROP DATABASE VisitorTrack_Snapshot_2;
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

INSERT INTO Exhibitions
(name, exhibition_start, exhibition_end, room_id) VALUES
('Nice expo', '2026-03-01', '2026-03-31', 4)

UPDATE Rooms
SET name = 'Mega giga nice room'
WHERE room_id = 3
GO

INSERT INTO Exhibition_visits
(visitor_id, exhibition_id, entry_time, exit_time) VALUES
(1, 3, '2025-11-16T11:19:32', '2025-11-16T11:19:35')
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