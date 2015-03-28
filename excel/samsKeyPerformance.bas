Attribute VB_Name = "samsKeyPerformance"
Sub main()
    
    ' Download CSV file
    strFileCsv = "http://pims.grc.nasa.gov/plots/batch/padtimes/padtimes.csv"
    Application.Workbooks.OpenText (strFileCsv)
    
    ' Save local
    SaveAsWithDatestamp
    
    ' Create sensor hours pivot table
    CreatePivotHours
    
    ' Create sensor bytes pivot table
    CreatePivotBytes
    
    ' Create yearly hours
    CreateYearlyHours
    
    ' Create yearly hours
    CreateYearlyBytes
    
    ' Format
    Worksheets("yearly_hours").Activate
    Range("A1").Select
    
End Sub
' FIXME refactor common parts of CreateYearlyHours[Bytes]
Sub CreateYearlyBytes()
    Worksheets("pivot_bytes").Activate
    Range("A2").Select
    Selection.CurrentRegion.Select
    Selection.Copy
    Sheets.Add Before:=Sheets("pivot_hours")
    Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks _
        :=False, Transpose:=False
    ActiveSheet.Name = "yearly_bytes"
End Sub
Sub CreateYearlyHours()
    Worksheets("pivot_hours").Activate
    Range("A2").Select
    Selection.CurrentRegion.Select
    Selection.Copy
    Sheets.Add Before:=Sheets("pivot_hours")
    Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks _
        :=False, Transpose:=False
    ActiveSheet.Name = "yearly_hours"
End Sub
' FIXME refactor common parts of CreatePivotHours[Bytes]
Sub CreatePivotHours()
    ' Get last row, column
    ActivateLastCell ("padtimes")
    lastRow = ActiveCell.Row
    lastCol = ActiveCell.Column
    ' Create pivot table
    ActiveWorkbook.Sheets("padtimes").Select
    Set sht = ActiveSheet
    With sht
        bottomMostRow = .Cells(1, 1).End(xlDown).Row
        rightMostColumn = .Cells(1, 1).End(xlToRight).Column
        Set DataRange = .Range(.Cells(1, 1), .Cells(bottomMostRow, rightMostColumn))
    End With
    'Debug.Print DataRange.Address
    ActiveSheet.PivotTableWizard xlDatabase, DataRange, TableName, "PivotTableHours"
    Set pivotSheet = ActiveSheet
    With pivotSheet
        .Select
        .Name = "pivot_hours"
    End With
    With ActiveSheet.PivotTables("PivotTableHours").PivotFields("Year")
        .Orientation = xlRowField
        .Position = 1
    End With
    With ActiveSheet.PivotTables("PivotTableHours").PivotFields("Month")
        .Orientation = xlRowField
        .Position = 2
    End With
    ActiveSheet.PivotTables("PivotTableHours").AddDataField ActiveSheet.PivotTables( _
        "PivotTableHours").PivotFields("121f02_hours"), "Sum of 121f02_hours", xlSum
    ActiveSheet.PivotTables("PivotTableHours").AddDataField ActiveSheet.PivotTables( _
        "PivotTableHours").PivotFields("121f03_hours"), "Sum of 121f03_hours", xlSum
    ActiveSheet.PivotTables("PivotTableHours").AddDataField ActiveSheet.PivotTables( _
        "PivotTableHours").PivotFields("121f04_hours"), "Sum of 121f04_hours", xlSum
    ActiveSheet.PivotTables("PivotTableHours").AddDataField ActiveSheet.PivotTables( _
        "PivotTableHours").PivotFields("121f05_hours"), "Sum of 121f05_hours", xlSum
    ActiveSheet.PivotTables("PivotTableHours").AddDataField ActiveSheet.PivotTables( _
        "PivotTableHours").PivotFields("121f06_hours"), "Sum of 121f06_hours", xlSum
    ActiveSheet.PivotTables("PivotTableHours").AddDataField ActiveSheet.PivotTables( _
        "PivotTableHours").PivotFields("121f08_hours"), "Sum of 121f08_hours", xlSum
    ActiveSheet.PivotTables("PivotTableHours").AddDataField ActiveSheet.PivotTables( _
        "PivotTableHours").PivotFields("es03_hours"), "Sum of es03_hours", xlSum
    ActiveSheet.PivotTables("PivotTableHours").AddDataField ActiveSheet.PivotTables( _
        "PivotTableHours").PivotFields("es05_hours"), "Sum of es05_hours", xlSum
    ActiveSheet.PivotTables("PivotTableHours").AddDataField ActiveSheet.PivotTables( _
        "PivotTableHours").PivotFields("es06_hours"), "Sum of es06_hours", xlSum
    ActiveSheet.PivotTables("PivotTableHours").AddDataField ActiveSheet.PivotTables( _
        "PivotTableHours").PivotFields("es08_hours"), "Sum of es08_hours", xlSum
    ActiveSheet.PivotTables("PivotTableHours").AddDataField ActiveSheet.PivotTables( _
        "PivotTableHours").PivotFields("ossbtmf_hours"), "Sum of ossbtmf_hours", xlSum
    ActiveSheet.PivotTables("PivotTableHours").AddDataField ActiveSheet.PivotTables( _
        "PivotTableHours").PivotFields("ossraw_hours"), "Sum of ossraw_hours", xlSum
    ActiveSheet.PivotTables("PivotTableHours").AddDataField ActiveSheet.PivotTables( _
        "PivotTableHours").PivotFields("hirap_hours"), "Sum of hirap_hours", xlSum
    With ActiveSheet.PivotTables("PivotTableHours").DataPivotField
        .Orientation = xlColumnField
        .Position = 1
    End With
    Range("A1").Select
End Sub
Sub CreatePivotBytes()
    ' Get last row, column
    ActivateLastCell ("padtimes")
    lastRow = ActiveCell.Row
    lastCol = ActiveCell.Column
    ' Create pivot table
    ActiveWorkbook.Sheets("padtimes").Select
    Set sht = ActiveSheet
    With sht
        bottomMostRow = .Cells(1, 1).End(xlDown).Row
        rightMostColumn = .Cells(1, 1).End(xlToRight).Column
        Set DataRange = .Range(.Cells(1, 1), .Cells(bottomMostRow, rightMostColumn))
    End With
    'Debug.Print DataRange.Address
    ActiveSheet.PivotTableWizard xlDatabase, DataRange, TableName, "PivotTableBytes"
    Set pivotSheet = ActiveSheet
    With pivotSheet
        .Select
        .Name = "pivot_bytes"
    End With
    With ActiveSheet.PivotTables("PivotTableBytes").PivotFields("Year")
        .Orientation = xlRowField
        .Position = 1
    End With
    ActiveSheet.PivotTables("PivotTableBytes").AddDataField ActiveSheet.PivotTables( _
        "PivotTableBytes").PivotFields("121f02_bytes"), "Sum of 121f02_bytes", xlSum
    ActiveSheet.PivotTables("PivotTableBytes").AddDataField ActiveSheet.PivotTables( _
        "PivotTableBytes").PivotFields("121f03_bytes"), "Sum of 121f03_bytes", xlSum
    ActiveSheet.PivotTables("PivotTableBytes").AddDataField ActiveSheet.PivotTables( _
        "PivotTableBytes").PivotFields("121f04_bytes"), "Sum of 121f04_bytes", xlSum
    ActiveSheet.PivotTables("PivotTableBytes").AddDataField ActiveSheet.PivotTables( _
        "PivotTableBytes").PivotFields("121f05_bytes"), "Sum of 121f05_bytes", xlSum
    ActiveSheet.PivotTables("PivotTableBytes").AddDataField ActiveSheet.PivotTables( _
        "PivotTableBytes").PivotFields("121f06_bytes"), "Sum of 121f06_bytes", xlSum
    ActiveSheet.PivotTables("PivotTableBytes").AddDataField ActiveSheet.PivotTables( _
        "PivotTableBytes").PivotFields("121f08_bytes"), "Sum of 121f08_bytes", xlSum
    ActiveSheet.PivotTables("PivotTableBytes").AddDataField ActiveSheet.PivotTables( _
        "PivotTableBytes").PivotFields("es03_bytes"), "Sum of es03_bytes", xlSum
    ActiveSheet.PivotTables("PivotTableBytes").AddDataField ActiveSheet.PivotTables( _
        "PivotTableBytes").PivotFields("es05_bytes"), "Sum of es05_bytes", xlSum
    ActiveSheet.PivotTables("PivotTableBytes").AddDataField ActiveSheet.PivotTables( _
        "PivotTableBytes").PivotFields("es06_bytes"), "Sum of es06_bytes", xlSum
    ActiveSheet.PivotTables("PivotTableBytes").AddDataField ActiveSheet.PivotTables( _
        "PivotTableBytes").PivotFields("es08_bytes"), "Sum of es08_bytes", xlSum
    ActiveSheet.PivotTables("PivotTableBytes").AddDataField ActiveSheet.PivotTables( _
        "PivotTableBytes").PivotFields("ossbtmf_bytes"), "Sum of ossbtmf_bytes", xlSum
    ActiveSheet.PivotTables("PivotTableBytes").AddDataField ActiveSheet.PivotTables( _
        "PivotTableBytes").PivotFields("ossraw_bytes"), "Sum of ossraw_bytes", xlSum
    ActiveSheet.PivotTables("PivotTableBytes").AddDataField ActiveSheet.PivotTables( _
        "PivotTableBytes").PivotFields("hirap_bytes"), "Sum of hirap_bytes", xlSum
    With ActiveSheet.PivotTables("PivotTableBytes").DataPivotField
        .Orientation = xlColumnField
        .Position = 1
    End With
    Range("A1").Select
End Sub
Sub ActivateLastCell(strSheet)
    Worksheets(strSheet).Activate
    ActiveSheet.Cells.SpecialCells(xlCellTypeLastCell).Activate
    'Debug.Print ActiveCell.Row, ActiveCell.Column
End Sub
Sub SaveAsWithDatestamp()
    datestamp = Format(Now(), "yyyy_MM_dd")
    ActiveWorkbook.SaveAs Filename:= _
        "C:\sams_kpi\padtimes_" & datestamp & ".xlsm", FileFormat:= _
        xlOpenXMLWorkbookMacroEnabled, CreateBackup:=False
    Cells.Select
    With Selection
        .HorizontalAlignment = xlCenter
        .VerticalAlignment = xlBottom
        .WrapText = False
        .Orientation = 0
        .AddIndent = False
        .IndentLevel = 0
        .ShrinkToFit = False
        .ReadingOrder = xlContext
        .MergeCells = False
    End With
    Cells.EntireColumn.AutoFit
    Rows("1:1").Select
    Selection.Font.Bold = True
    With ActiveWindow
        .SplitColumn = 0
        .SplitRow = 1
    End With
    ActiveWindow.FreezePanes = True
    Range("A2").Select
End Sub
Public Function SortWorksheetsByNameArray(NameArray() As Variant, ByRef ErrorText As String) As Boolean
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    ' WorksheetSortByArray by Chip Pearson
    ' This procedure sorts the worksheets named in NameArray to the order in
    ' which they appear in NameArray. The adjacent elements in NameArray need
    ' not be adjacent sheets, but the collection of all sheets named in
    ' NameArray must form a set of adjacent sheets. If successful, returns
    ' True and ErrorText is vbNullString. If failure, returns False and
    ' ErrorText contains reason for failure.
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    Dim Arr() As Long
    Dim N As Long
    Dim M As Long
    Dim L As Long
    Dim WB As Workbook
    
    ErrorText = vbNullString
    
    '''''''''''''''''''''''''''''''''''''''''''''''
    ' The NameArray need not contain all of the
    ' worksheets in the workbook, but the sheets
    ' that it does name together must form a group of
    ' adjacent sheets. Sheets named in NameArray
    ' need not be adjacent in the NameArray, only
    ' that when all sheet taken together, they form an
    ' adjacent group of sheets
    '''''''''''''''''''''''''''''''''''''''''''''''
    ReDim Arr(LBound(NameArray) To UBound(NameArray))
    On Error Resume Next
    For N = LBound(NameArray) To UBound(NameArray)
        '''''''''''''''''''''''''''''''''''''''
        ' Ensure all sheets in name array exist
        '''''''''''''''''''''''''''''''''''''''
        Err.Clear
        M = Len(WB.Worksheets(NameArray(N)).Name)
        If Err.Number <> 0 Then
            ErrorText = "Worksheet does not exist."
            SortWorksheetsByNameArray = False
            Exit Function
        End If
        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        ' Put the index value of the sheet into Arr. Ensure there
        ' are no duplicates. If Arr(N) is not zero, we've already
        ' loaded that element of Arr and thus have duplicate sheet
        ' names.
        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        If Arr(N) > 0 Then
            ErrorText = "Duplicate worksheet name in NameArray."
            SortWorksheetsByNameArray = False
            Exit Function
        End If
            
        Arr(N) = Worksheets(NameArray(N)).Index
    Next N
    
    '''''''''''''''''''''''''''''''''''''''
    ' Sort the sheet indexes. We don't use
    ' these for the sorting order, but we
    ' do use them to ensure that the group
    ' of sheets passed in NameArray are
    ' together contiguous.
    '''''''''''''''''''''''''''''''''''''''
    For M = LBound(Arr) To UBound(Arr)
        For N = M To UBound(Arr)
            If Arr(N) < Arr(M) Then
                L = Arr(N)
                Arr(N) = Arr(M)
                Arr(M) = L
            End If
        Next N
    Next M
    ''''''''''''''''''''''''''''''''''''''''
    ' Now that Arr is sorted ascending, ensure
    ' that the elements are in order differing
    ' by exactly 1. Otherwise, sheet are not
    ' adjacent.
    '''''''''''''''''''''''''''''''''''''''''
    If ArrayElementsInOrder(Arr:=Arr, Descending:=False, Diff:=1) = False Then
        ErrorText = "Specified sheets are not adjacent."
        SortWorksheetsByNameArray = False
        Exit Function
    End If
    
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    ' Now, do the actual move of the sheets.
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    On Error GoTo 0
    WB.Worksheets(NameArray(LBound(NameArray))).Move Before:=WB.Worksheets(Arr(1))
    For N = LBound(NameArray) + 1 To UBound(NameArray) - 1
        WB.Worksheets(NameArray(N)).Move Before:=WB.Worksheets(NameArray(N + 1))
    Next N
    
    SortWorksheetsByNameArray = True

End Function

