USE MuseumDB
GO

DECLARE @StartSeconds  INT;
DECLARE @EndSeconds    INT;

SELECT 
    @StartSeconds  = 0,
    @EndSeconds    = 24*60*60;

DECLARE @TimeInProcess INT = @StartSeconds;

WHILE @TimeInProcess < @EndSeconds
BEGIN
    DECLARE @Hour   INT = @TimeInProcess / 3600;
    DECLARE @Minute INT = (@TimeInProcess % 3600) / 60;
    DECLARE @Second INT = @TimeInProcess % 60;

    IF NOT EXISTS (
        SELECT 1 
        FROM Time 
        WHERE [hour] = @Hour 
          AND [minute] = @Minute 
          AND [second] = @Second
    )
    BEGIN
        INSERT INTO Time ([hour], [minute], [second])
        VALUES (@Hour, @Minute, @Second);
    END

    SET @TimeInProcess += 1;
END
GO

