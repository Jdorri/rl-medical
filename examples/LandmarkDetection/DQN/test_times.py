import timeit

def run_GUI():
    controller = Controller()
    sys.exit(controller.app.exec_())
    controller.window1.right_widget.on_clicking_run()

if __name__ == '__main__':
    # Step 0 - Initialise variables
    recorded_times = []
    section_names = []
    number = 10000
    
    # Step 1 - Import modules
    recorded_times.append(timeit.timeit("import functioning_UI_PyQt", number=number))
    section_names.append("Imports")
    print(f'{section_names[-1]} section lasted: {recorded_times[-1]:.3f}')
    from functioning_UI_PyQt import *

    # Step 2 - Launch GUI
    recorded_times.append(timeit.timeit("run_GUI()", number=number, setup="from __main__ import run_GUI"))
    section_names.append("Launch GUI")
    print(f'{section_names[-1]} section lasted: {recorded_times[-1]:.3f}')
    # run_GUI()



