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

-- do wartości
BULK INSERT #StockCSV
FROM 'c:\Users\jakub\Documents\Code\University\hd\hd\bulk\StockCSV.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK
);
GO

WITH vETLDimExhibit AS (
    SELECT
        s.exhibit_id,
        s.name,
        s.author,
        CASE 
            WHEN s.creation_year < 476 THEN 'starożytność'
            WHEN s.creation_year < 1492 THEN 'średniowiecze'
            WHEN s.creation_year < 1789 THEN 'nowożytność'
            ELSE 'czasy współczesne'
        END AS creation_era,
        CASE 
            WHEN (YEAR(GETDATE()) - s.acquisition_year) < 1 THEN '<1'
            WHEN (YEAR(GETDATE()) - s.acquisition_year) < 5 THEN '<5'
            WHEN (YEAR(GETDATE()) - s.acquisition_year) < 10 THEN '<10'
            ELSE '>=10'
        END AS acquisition_duration,
        s.type,
        CASE 
            WHEN s.value < 10000 THEN '<10 000'
            WHEN s.value < 100000 THEN '<100 000'
            WHEN s.value < 1000000 THEN '<1 000 000'
            ELSE '>1 000 000'
        END AS value
    FROM #StockCSV s
)
MERGE INTO Exhibit AS TT 
    USING vETLDimExhibit AS ST
        ON TT.number = ST.exhibit_id
            WHEN NOT MATCHED
                THEN
                    INSERT VALUES (
                        ST.exhibit_id,
                        ST.name,
                        ST.author,
                        ST.creation_era,
                        ST.acquisition_duration,
                        ST.type,
                        ST.value,
                        GETDATE(), -- data dzisiaj
                        NULL -- data zmiany
                    )
            WHEN NOT MATCHED BY SOURCE
                THEN
                    DELETE;
GO

-- Clean up staging table
DROP TABLE #StockCSV;
GO