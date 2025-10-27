USE VisitorTrack
GO

DELETE FROM Exhibition_visits;
DELETE FROM Exhibit_Exhibitions;
DELETE FROM Exhibitions;
DELETE FROM Exhibits;
DELETE FROM Rooms;
DELETE FROM Visitors;

-- Wyzerowac klucze
DBCC CHECKIDENT ('Visitors', RESEED, 0);
DBCC CHECKIDENT ('Rooms', RESEED, 0);
DBCC CHECKIDENT ('Exhibitions', RESEED, 0);
DBCC CHECKIDENT ('Exhibits', RESEED, 0);
DBCC CHECKIDENT ('Exhibition_visits', RESEED, 0);