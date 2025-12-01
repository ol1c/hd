USE VisitorTrack

INSERT INTO Exhibitions
(name, exhibition_start, exhibition_end, room_id) VALUES
('Nice expo', '2026-03-01', '2026-03-31', 4)
GO

USE VisitorTrack

UPDATE Rooms
SET name = 'Mega giga nice room'
WHERE room_id = 3
GO

USE VisitorTrack

INSERT INTO Exhibition_visits
(visitor_id, exhibition_id, entry_time, exit_time) VALUES
(1, 3, '2025-11-16T11:19:32', '2025-11-16T11:19:35')
GO