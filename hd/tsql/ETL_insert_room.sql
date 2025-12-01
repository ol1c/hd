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

Declare @Today datetime;
SELECT @Today = GETDATE();

MERGE INTO Room AS TT 
    USING vETLDimRoom AS ST
        ON TT.number = ST.room_id
            WHEN NOT MATCHED
                THEN
                    INSERT VALUES (
                        ST.name,
                        ST.room_id,
                        ST.floor,
                        GETDATE(), -- data dzisiaj
                        NULL -- data zmiany
                    )
            WHEN MATCHED
                AND TT.effective_end_date IS NULL
                AND (  
                    TT.name <> ST.name
                    OR TT.flor <> ST.floor
                )
                THEN
                    UPDATE SET 
                        TT.effective_end_date = @Today
            WHEN NOT MATCHED BY SOURCE
            AND TT.PID != 'UNKNOWN' -- do not update the UNKNOWN tuple
			THEN
				UPDATE
				SET TT.effective_end_date = @Today;

INSERT INTO Room (
    name,
    number,
    flor,
    effective_start_date,
    effective_end_date
    )
    SELECT
        ST.name,
        ST.room_id,
        ST.floor,
        @Today, -- data dzisiaj
        NULL -- data zmiany
    FROM vETLDimRoom AS ST;
    EXCEPT
    SELECT
        TT.name,
        TT.number,
        TT.flor,
        @Today, -- data dzisiaj
        NULL -- data zmiany
    FROM Room AS TT;
GO

DROP VIEW vETLDimRoom;
GO

