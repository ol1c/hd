USE VisitorTrack

BULK INSERT Rooms
FROM 'C:\Users\jakub\Documents\Code\University\hd\hd\bulk\rooms.bulk' 
WITH
(
    FIELDTERMINATOR = '|',
    ROWTERMINATOR = '0x0a', --bez tego nie dziala :< \n bo pisane \n tez nie dziala
    FIRSTROW = 2 
);

BULK INSERT Exhibitions
FROM 'C:\Users\jakub\Documents\Code\University\hd\hd\bulk\exhibitions.bulk' 
WITH
(
    FIELDTERMINATOR = '|',
    ROWTERMINATOR = '0x0a',
    FIRSTROW = 2 
);

BULK INSERT Exhibits
FROM 'C:\Users\jakub\Documents\Code\University\hd\hd\bulk\exhibits.bulk' 
WITH
(
    FIELDTERMINATOR = '|',
    ROWTERMINATOR = '0x0a',
    FIRSTROW = 2 
);

BULK INSERT Exhibit_Exhibitions
FROM 'C:\Users\jakub\Documents\Code\University\hd\hd\bulk\exhibit_exhibitions.bulk' 
WITH
(
    FIELDTERMINATOR = '|',
    ROWTERMINATOR = '0x0a',
    FIRSTROW = 2 
);

BULK INSERT Visitors
FROM 'C:\Users\jakub\Documents\Code\University\hd\hd\bulk\visitors.bulk' 
WITH
(
    FIELDTERMINATOR = '|',
    ROWTERMINATOR = '0x0a',
    FIRSTROW = 2 
);

BULK INSERT Exhibition_visits
FROM 'C:\Users\jakub\Documents\Code\University\hd\hd\bulk\exhibition_visits.bulk' 
WITH
(
    FIELDTERMINATOR = '|',
    ROWTERMINATOR = '0x0a',
    FIRSTROW = 2 
);