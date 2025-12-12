USE VisitorTrack

UPDATE Rooms
SET name = 'Mega giga nice room'
WHERE room_id = 3
GO

USE VisitorTrack

BULK INSERT Exhibitions
FROM 'C:\Users\jakub\Documents\Code\University\hd\hd\bulk\exhs2.bulk' 
WITH
(
    FIELDTERMINATOR = '|',
    ROWTERMINATOR = '0x0a'
);

BULK INSERT Exhibit_Exhibitions
FROM 'C:\Users\jakub\Documents\Code\University\hd\hd\bulk\exs_exhs2.bulk' 
WITH
(
    FIELDTERMINATOR = '|',
    ROWTERMINATOR = '0x0a'
);

BULK INSERT Visitors
FROM 'C:\Users\jakub\Documents\Code\University\hd\hd\bulk\vis2.bulk' 
WITH
(
    FIELDTERMINATOR = '|',
    ROWTERMINATOR = '0x0a'
);

BULK INSERT Exhibition_visits
FROM 'C:\Users\jakub\Documents\Code\University\hd\hd\bulk\exhs_vis2.bulk' 
WITH
(
    FIELDTERMINATOR = '|',
    ROWTERMINATOR = '0x0a'
);
