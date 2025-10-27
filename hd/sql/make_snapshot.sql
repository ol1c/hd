USE master
GO
/*
CREATE DATABASE VisitorTrack_Snapshot_1
ON
(
    NAME = VisitorTrack,
    FILENAME = 'C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\DATA\VisitorTrack_Snapshot_1.ss'
)
AS SNAPSHOT OF VisitorTrack;
GO
*/
USE VisitorTrack
GO

UPDATE Rooms
SET name = 'Best Room'
WHERE room_id = 3;