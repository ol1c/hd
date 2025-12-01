USE MuseumDB
GO

IF (object_id('vETLDimVisitor') IS NOT NULL)
    DROP VIEW vETLDimVisitor;
GO

CREATE VIEW vETLDimVisitor AS
SELECT DISTINCT
    name
FROM VisitorTrack.dbo.Visitors;
GO

MERGE INTO Visitor AS TT 
    USING vETLDimVisitor AS ST
        ON TT.name = ST.name
            WHEN NOT MATCHED
                THEN
                    INSERT VALUES (
                        ST.name
                    )
            WHEN NOT MATCHED BY SOURCE
                THEN
                    DELETE;
GO

DROP VIEW vETLDimVisitor;
GO