import PySimpleGUI as sg

layout = [[sg.Text('Posting date', size=(22, 1)), sg.In(k='-DATE-', size=(18, 1))],
          [sg.Text('Posting month', size=(22, 1)), sg.In(k='-MON-', size=(18, 1))],
          [sg.Ok(), sg.Cancel()]]

# One Shot window version
event, values = sg.Window('CSV Reformatter', layout).read(close=True)

if event == 'Ok':
    print('You entered:', values['-DATE-'], values['-MON-'])
else:
    print('Cancelled')
