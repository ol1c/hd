USE MuseumDB
GO

IF OBJECT_ID('tempdb..#StockCSV') IS NOT NULL
    DROP TABLE #StockCSV;

-- do total value
CREATE TABLE #StockCSV (
    exhibit_id INT,
    name VARCHAR(200),
    author VARCHAR(200),
    creation_year INT,
    acquisition_year INT,
    type VARCHAR(200),
    value DECIMAL(10,2)
);

BULK INSERT #StockCSV
FROM 'c:\Users\jakub\Documents\Code\University\hd\hd\bulk\StockCSV.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK
);
GO

WITH vETLFactVisit AS (
    SELECT
        d.date_id,
        t_entry.time_id AS entry_time_id,
        t_exit.time_id AS exit_time_id,
        ex.exhibition_id,
        r.room_id,
        v.visitor_id,
        DATEDIFF(SECOND, ev.entry_time, ev.exit_time) AS visit_duration,
        COUNT(DISTINCT ee.fk_exhibit_id) AS exhibits_count,
        SUM(csv.value) AS exhibits_total_value
    FROM VisitorTrack.dbo.Exhibition_visits ev
    INNER JOIN VisitorTrack.dbo.Visitors vis ON ev.visitor_id = vis.visitor_id
    INNER JOIN MuseumDB.dbo.Date d 
        ON YEAR(ev.entry_time) = d.year 
        AND MONTH(ev.entry_time) = d.month 
        AND DAY(ev.entry_time) = d.day
    INNER JOIN MuseumDB.dbo.Time t_entry 
        ON DATEPART(HOUR, ev.entry_time) = t_entry.hour 
        AND DATEPART(MINUTE, ev.entry_time) = t_entry.minute 
        AND DATEPART(SECOND, ev.entry_time) = t_entry.second
    INNER JOIN MuseumDB.dbo.Time t_exit 
        ON DATEPART(HOUR, ev.exit_time) = t_exit.hour 
        AND DATEPART(MINUTE, ev.exit_time) = t_exit.minute 
        AND DATEPART(SECOND, ev.exit_time) = t_exit.second
    INNER JOIN MuseumDB.dbo.Visitor v ON vis.name = v.name
    INNER JOIN VisitorTrack.dbo.Exhibitions e ON ev.exhibition_id = e.exhibition_id
    INNER JOIN MuseumDB.dbo.Exhibition ex ON e.name = ex.name --na patencie. Nie przenosimy ID ale nazwy są UNIQUE
    INNER JOIN MuseumDB.dbo.Room r ON e.room_id = r.number
    LEFT JOIN VisitorTrack.dbo.Exhibit_Exhibitions ee ON e.exhibition_id = ee.fk_exhibition_id
    LEFT JOIN #StockCSV csv ON ee.fk_exhibit_id = csv.exhibit_id
    GROUP BY ev.visit_id, ev.entry_time, ev.exit_time, d.date_id, t_entry.time_id, t_exit.time_id, ex.exhibition_id, r.room_id, v.visitor_id
)
MERGE INTO Visit AS TT 
    USING vETLFactVisit AS ST
        ON TT.date_id = ST.date_id 
        AND TT.entry_time = ST.entry_time_id 
        AND TT.exit_time = ST.exit_time_id
        AND TT.visitor_id = ST.visitor_id
        AND TT.exhibition_id = ST.exhibition_id
            WHEN NOT MATCHED
                THEN
                    INSERT VALUES (
                        ST.date_id,
                        ST.entry_time_id,
                        ST.exit_time_id,
                        ST.exhibition_id,
                        ST.room_id,
                        ST.visitor_id,
                        ST.visit_duration,
                        ST.exhibits_total_value,
                        ST.exhibits_count
                    )
            WHEN NOT MATCHED BY SOURCE
                THEN
                    DELETE;
GO

DROP TABLE #StockCSV;
GO