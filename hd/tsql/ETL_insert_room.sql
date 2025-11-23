USE MuseumDB
GO

IF (object_id('vETLDimRoom') IS NOT NULL)
    DROP VIEW vETLDimRoom;
GO

CREATE VIEW vETLDimRoom AS
SELECT
    room_id,
    name,
    floor
FROM VisitorTrack.dbo.Rooms;
GO

MERGE INTO Room AS TT 
    USING vETLDimRoom AS ST
        ON TT.number = ST.room_id
            WHEN NOT MATCHED
                THEN
                    INSERT VALUES (
                        ST.name,
                        ST.room_id,
                        ST.floor,
                        GETDATE(),
                        NULL
                    )
            WHEN NOT MATCHED BY SOURCE
                THEN
                    DELETE;
GO

DROP VIEW vETLDimRoom;
GO

