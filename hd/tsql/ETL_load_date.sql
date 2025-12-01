USE MuseumDB
GO

DECLARE @StartDate DATE;
DECLARE @EndDate   DATE;

-- Od min do max z exhibition (nie mamy sztucznych ram czasowych, trzeba za karzdym razem przemielić???)
SELECT 
    @StartDate = MIN(exhibition_start),
    @EndDate   = MAX(exhibition_end)
FROM VisitorTrack.dbo.Exhibitions;

DECLARE @DateInProcess DATETIME = @StartDate;

WHILE @DateInProcess <= @EndDate
BEGIN
    DECLARE @Year    INT = YEAR(@DateInProcess);
    DECLARE @Quarter INT = DATEPART(QUARTER, @DateInProcess);
    DECLARE @Month   INT = MONTH(@DateInProcess);
    DECLARE @Day     INT = DAY(@DateInProcess);
    
    IF NOT EXISTS (
        SELECT 1 
        FROM Date 
        WHERE [year] = @Year 
          AND [month] = @Month 
          AND [day] = @Day
    )
    BEGIN
        INSERT INTO Date ([year], [quater], [month], [day], [day_name])
        VALUES (
            @Year,
            @Quarter,
            @Month,
            @Day,
            DATENAME(DW, @DateInProcess)
        );
    END
    
    SET @DateInProcess = DATEADD(DAY, 1, @DateInProcess);
END
GO