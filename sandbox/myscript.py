import sys
def PythonVersion(*args):
    """Prints the Python version into the current document"""
#get the doc from the scripting context which is made available to all scripts
    desktop = XSCRIPTCONTEXT.getDesktop()
    model = desktop.getCurrentComponent()
#check whether there's already an opened document. Otherwise, create a new one
    if not hasattr(model, "Sheets"):
        model = desktop.loadComponentFromURL(
            "private:factory/scalc","_blank", 0, () )
#get the XText interface
    sheet = model.Sheets.getByIndex(0)
#create an XTextRange at the end of the document
    tRange = sheet.getCellRangeByName("C4")
#and set the string
    tRange.String = "The Python version is %s.%s.%s" % sys.version_info[:3]
#do the same for the python executable path
    tRange = sheet.getCellRangeByName("C5")
    tRange.String = sys.executable
    return None

