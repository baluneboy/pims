import win32com.client
import sys, io

# Open up Excel and make it visible (actually you don't need to make it visible)
excel = win32com.client.Dispatch('Excel.Application')
excel.Visible = True

# Redirect the stdout to a file
orig_stdout = sys.stdout
bk = io.open("c:/temp/Answers_Report.txt", mode="w", encoding="utf-8")
sys.stdout = bk

# Select a file and open it
file = "C:/Temp/file1.xlsx"
wb_data = excel.Workbooks.Open(file)

# Get the answers to the Q1A and write them into the summary file
mission = wb_data.Worksheets("MissionVision").Range("C6")
vision = wb_data.Worksheets("MissionVision").Range("C7")
print("Question 1A")
print("Mission:", mission)
print("Vision:", vision)
print()

# Get the answers to the Q1B and write them into the summary file
oe1 = wb_data.Worksheets("MissionVision").Range("C14")
ju1 = wb_data.Worksheets("MissionVision").Range("D14")
oe2 = wb_data.Worksheets("MissionVision").Range("C15")
ju2 = wb_data.Worksheets("MissionVision").Range("D15")
print("Question 1B")
print("OEN1:", oe1, "- JUSTIF:", ju1)
print("OEN2:", oe2, "- JUSTIF:", ju2)
print()

# Close the file without saving
wb_data.Close(True)

# Closing Excel and restoring the stdout
sys.stdout = orig_stdout
bk.close()
excel.Quit()
