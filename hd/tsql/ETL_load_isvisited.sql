USE MuseumDB
GO

WITH vETLFactIsVisited AS (
    SELECT DISTINCT
        v.visit_id,
        ex.exhibit_id
    FROM VisitorTrack.dbo.Exhibition_visits ev
    INNER JOIN VisitorTrack.dbo.Exhibitions e 
        ON ev.exhibition_id = e.exhibition_id
    INNER JOIN VisitorTrack.dbo.Exhibit_Exhibitions ee 
        ON e.exhibition_id = ee.fk_exhibition_id
    INNER JOIN MuseumDB.dbo.Exhibit ex 
        ON ee.fk_exhibit_id = ex.number
    INNER JOIN MuseumDB.dbo.Exhibition exhibition 
        ON e.name = exhibition.name
    INNER JOIN MuseumDB.dbo.Visit v 
        ON v.exhibition_id = exhibition.exhibition_id
)
MERGE INTO IsVisited AS TT 
    USING vETLFactIsVisited AS ST
        ON TT.visit_id = ST.visit_id 
        AND TT.exhibit_id = ST.exhibit_id
    WHEN NOT MATCHED THEN
        INSERT VALUES (ST.visit_id, ST.exhibit_id)
    WHEN NOT MATCHED BY SOURCE THEN
        DELETE;
GO