import PySimpleGUI as sg

layout = [[sg.Text('GPU')],
            [sg.In('Enter comma-seperated list of GPU(s) to use')],
            [sg.Text('_'  * 80)],
            [sg.Text('Algorithm')],
            [sg.Drop(values=('DQN','Double','Dueling','DuelingDouble'))],
            [sg.Text('_'  * 80)],
            [sg.Text('Task')],
            [sg.Drop(values=('Play', 'Eval', 'Train'))],
            [sg.Text('_'  * 80)],
            [sg.Text('Files')],
            [sg.Text('File 1'), sg.In('Select text file comtaining list of images'), sg.FolderBrowse()],
            [sg.Text('File 1'), sg.In('Select second text file if task == train or eval'), sg.FolderBrowse()],
            [sg.Text('_'  * 80)],
            [sg.Text('Flags')],
            [sg.Checkbox('Save GIF')],[sg.Checkbox('Save Video')],[sg.Checkbox('Load Model')],
            [sg.Text('_'  * 80)],
            [sg.Text('Training Logs')],
            [sg.In('Select directory for storing logs'), sg.FolderBrowse()],
            [sg.In('Enter name of experiment for logs')],
            [sg.Text('_'  * 80)],
            [sg.Button('Run'), sg.Exit()]]

window = sg.Window('Landmark Detection Options', layout)

event, values = window.Read()

#sg.Popup(event, values)
