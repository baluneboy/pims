#!/usr/bin/python

import pyoo

# create headless pipe named "hello"
#soffice --accept="pipe,name=hello;urp;" --norestore --nologo --nodefault

def demo1():

    desktop = pyoo.Desktop(pipe="hello")

    doc = desktop.create_spreadsheet()
    doc.sheets.create("MySheet", index=1)

    doc.sheets.copy("MySheet", "CopiedSheet", 2)

    del doc.sheets[1]
    del doc.sheets['CopiedSheet']
    
    get_sheet_name = pyoo.NameGenerator()
    doc.sheets.create(get_sheet_name('Mysheet'))

    doc.sheets.create(get_sheet_name('Mysheet'))

    sheet = doc.sheets[0]
    str(sheet[0,0].address)

    sheet[0,0].value = 1
    sheet[0,1].value = 2
    sheet[0,1].formula = '$A$1-$B$1'
    sheet[0,1].value = 2
    sheet[0,2].formula = '=$A$1-$B$1'
    sheet[0,2].formula = '=$A$1+$B$1'
    sheet[1:3,0:2].values = [[3,4],[5,6]]
    sheet[3,0:2].formulas = ['=$A$1+$A$2+$a$3','=$b$1+$b$2+$b$3']
    cells = sheet[:4,:3]

    cells.font_size = 20
    cells[3,:].font_weight = pyoo.FONT_WEIGHT_BOLD
    cells[:,2].text_align = pyoo.TEXT_ALIGN_LEFT
    cells[-1,-1].underline = pyoo.UNDERLINE_DOUBLE
    cells[0,0].underline = pyoo.UNDERLINE_DOUBLE
    cells[:3,:2].text_color = 0xFF0000
    cells[:-1,:-1].background_color = 0x0000FF

    cells[:,:].border_width = 10
    cells[-4:-1,-3:-1].inner_border_width = 50
    loc = doc.get_locale('en', 'us')
    sheet.number_format = loc.format(pyoo.FORMAT_PERCENT_INT)

    chart = sheet.charts.create("my chart", sheet[5:10,0:5], sheet[:4,:3])
    sheet.charts[0].name

    diagram = chart.change_type(pyoo.LineDiagram)
    doc.save('/tmp/example1.xlsx', pyoo.FILTER_EXCEL_2007)
    doc.close()

if __name__ == "__main__":
    demo1()