USE MuseumDB
GO

IF OBJECT_ID('StockCSV_Staging') IS NOT NULL
    DROP TABLE StockCSV_Staging;

CREATE TABLE StockCSV_Staging (
    exhibit_id INT,
    name VARCHAR(200),
    author VARCHAR(200),
    creation_year INT,
    acquisition_year INT,
    type VARCHAR(200),
    value DECIMAL(10,2)
);

-- do wartości
BULK INSERT StockCSV_Staging
FROM 'c:\Users\jakub\Documents\Code\University\hd\hd\bulk\StockCSV.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK
);
GO

If (object_id('vETLDimExhibit') is not null) Drop View vETLDimExhibit;
go
CREATE VIEW vETLDimExhibit AS
SELECT
    s.exhibit_id,
    s.name,
    s.author,
    CASE 
        WHEN s.creation_year < 476 THEN 'starożytność'
        WHEN s.creation_year < 1492 THEN 'średniowiecze'
        WHEN s.creation_year < 1789 THEN 'nowożytność'
        ELSE 'czasy współczesne'
    END AS ceratino_era,
    CASE 
        WHEN (YEAR(GETDATE()) - s.acquisition_year) < 1 THEN '<1'
        WHEN (YEAR(GETDATE()) - s.acquisition_year) < 5 THEN '<5'
        WHEN (YEAR(GETDATE()) - s.acquisition_year) < 10 THEN '<10'
        ELSE '>=10'
    END AS acquasition_duration,
    s.type,
    CASE 
        WHEN s.value < 10000 THEN '<10 000'
        WHEN s.value < 100000 THEN '<100 000'
        WHEN s.value < 1000000 THEN '<1 000 000'
        ELSE '>1 000 000'
    END AS value
FROM StockCSV_Staging s;
GO

Declare @Today datetime;
SELECT @Today = GETDATE();

MERGE INTO Exhibit AS TT 
    USING vETLDimExhibit AS ST
        ON TT.number = ST.exhibit_id
            WHEN NOT MATCHED
                THEN
                    INSERT VALUES (
                        ST.exhibit_id,
                        ST.name,
                        ST.author,
                        ST.ceratino_era,
                        ST.acquasition_duration,
                        ST.type,
                        ST.value,
                        @Today, -- data dzisiaj
                        NULL -- data zmiany
                    )
            WHEN MATCHED
                AND TT.effective_end_date IS NULL
                AND (
                    TT.name <> ST.name
                    OR TT.author <> ST.author
                    OR TT.ceratino_era <> ST.ceratino_era
                    OR TT.acquasition_duration <> ST.acquasition_duration
                    OR TT.type <> ST.type
                    OR TT.value <> ST.value
                )
                THEN
                    UPDATE SET 
                        TT.effective_end_date = @Today
            WHEN NOT MATCHED BY SOURCE
			THEN
				UPDATE
				SET TT.effective_end_date = @Today;

INSERT INTO Exhibit (
    number,
    name,
    author,
    ceratino_era,
    acquasition_duration,
    type,
    value,
    effective_start_date,
    effective_end_date
    )
    SELECT
        ST.exhibit_id,
        ST.name,
        ST.author,
        ST.ceratino_era,
        ST.acquasition_duration,
        ST.type,
        ST.value,
        @Today, -- data dzisiaj
        NULL -- data zmiany
    FROM vETLDimExhibit AS ST
    EXCEPT
    SELECT 
        TT.number,
        TT.name,
        TT.author,
        TT.ceratino_era,
        TT.acquasition_duration,
        TT.type,
        TT.value,
        @Today, -- data dzisiaj
        NULL -- data zmiany
    FROM Exhibit AS TT;
GO

DROP TABLE StockCSV_Staging;
Drop View vETLDimExhibit; 
GO