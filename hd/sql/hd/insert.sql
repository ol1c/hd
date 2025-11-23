USE MuseumDB

BULK INSERT Date
FROM 'C:\Users\jakub\Documents\Code\University\hd\hd\bulk_dw\date.bulk' 
WITH
(
    FIELDTERMINATOR = '|',
    ROWTERMINATOR = '0x0a' --bez tego nie dziala :< "\n" bo pisane \n tez nie dziala
);

BULK INSERT Time
FROM 'C:\Users\jakub\Documents\Code\University\hd\hd\bulk_dw\time.bulk' 
WITH
(
    FIELDTERMINATOR = '|',
    ROWTERMINATOR = '0x0a'
);

BULK INSERT Room
FROM 'C:\Users\jakub\Documents\Code\University\hd\hd\bulk_dw\room.bulk' 
WITH
(
    FIELDTERMINATOR = '|',
    ROWTERMINATOR = '0x0a'
);

BULK INSERT Visitor
FROM 'C:\Users\jakub\Documents\Code\University\hd\hd\bulk_dw\visitor.bulk' 
WITH
(
    FIELDTERMINATOR = '|',
    ROWTERMINATOR = '0x0a'
);

BULK INSERT Exhibition
FROM 'C:\Users\jakub\Documents\Code\University\hd\hd\bulk_dw\exhibition.bulk' 
WITH
(
    FIELDTERMINATOR = '|',
    ROWTERMINATOR = '0x0a'
);

BULK INSERT Exhibit
FROM 'C:\Users\jakub\Documents\Code\University\hd\hd\bulk_dw\exhibit.bulk' 
WITH
(
    FIELDTERMINATOR = '|',
    ROWTERMINATOR = '0x0a'
);


BULK INSERT Visit
FROM 'C:\Users\jakub\Documents\Code\University\hd\hd\bulk_dw\visit.bulk' 
WITH
(
    FIELDTERMINATOR = '|',
    ROWTERMINATOR = '0x0a'
);


BULK INSERT IsVisited
FROM 'C:\Users\jakub\Documents\Code\University\hd\hd\bulk_dw\is_visited.bulk' 
WITH
(
    FIELDTERMINATOR = '|',
    ROWTERMINATOR = '0x0a'
);