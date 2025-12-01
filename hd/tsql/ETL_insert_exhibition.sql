USE MuseumDB
GO

IF OBJECT_ID('tempdb..#StockCSV') IS NOT NULL
    DROP TABLE #StockCSV;

CREATE TABLE #StockCSV (
    exhibit_id INT,
    name VARCHAR(200),
    author VARCHAR(200),
    creation_year INT,
    acquisition_year INT,
    type VARCHAR(200),
    value DECIMAL(10,2)
);

-- potrzebne do avg value w exhibition
BULK INSERT #StockCSV
FROM 'c:\Users\jakub\Documents\Code\University\hd\hd\bulk\StockCSV.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK
);
GO


WITH vETLDimExhibition AS (
    SELECT
        e.exhibition_id,
        e.name,
        ds.date_id AS start_date_id,
        de.date_id AS end_date_id,
        CASE 
            WHEN AVG(csv.value) < 10000 THEN '<10 000'
            WHEN AVG(csv.value) < 100000 THEN '<100 000'
            WHEN AVG(csv.value) < 1000000 THEN '<1 000 000'
            ELSE '>1 000 000'
        END AS average_value
    FROM VisitorTrack.dbo.Exhibitions e
    INNER JOIN MuseumDB.dbo.Date ds ON YEAR(e.exhibition_start) = ds.year 
        AND MONTH(e.exhibition_start) = ds.month 
        AND DAY(e.exhibition_start) = ds.day
    INNER JOIN MuseumDB.dbo.Date de ON YEAR(e.exhibition_end) = de.year 
        AND MONTH(e.exhibition_end) = de.month 
        AND DAY(e.exhibition_end) = de.day
    LEFT JOIN VisitorTrack.dbo.Exhibit_Exhibitions ee ON e.exhibition_id = ee.fk_exhibition_id
    LEFT JOIN VisitorTrack.dbo.Exhibits exs ON ee.fk_exhibit_id = exs.exhibit_id
    LEFT JOIN #StockCSV csv ON exs.exhibit_id = csv.exhibit_id
    GROUP BY e.exhibition_id, e.name, e.exhibition_start, e.exhibition_end, ds.date_id, de.date_id
)
MERGE INTO Exhibition AS TT 
    USING vETLDimExhibition AS ST
        ON TT.name = ST.name
            WHEN NOT MATCHED
                THEN
                    INSERT VALUES (
                        ST.name,
                        ST.start_date_id,
                        ST.end_date_id,
                        ST.average_value
                    )
            WHEN NOT MATCHED BY SOURCE
                THEN
                    DELETE;
            -- to usuwa rekordy w docelowej tabeli, których już nie ma w źródle. Upewnij się, że to zamierzone (może powodować niechciane kasowanie).
GO

DROP TABLE #StockCSV;
GO