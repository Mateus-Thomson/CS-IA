from tkinter import *

can_float = ['m_cPower', 'm_pPower']
toggles = {}
def user_input(settings):
    inputWindow = Tk()

    inputWindow.title("Input Window")
    inputWindow.geometry(f'350x{23*(len(settings))}')

    names = []
    inputs = []
    for idx,setting in enumerate(settings):
        names.append(Label(inputWindow, text = setting))
        names[-1].grid(column=0, row=idx)

        inputs.append(Entry(inputWindow, width=10))
        inputs[-1].grid(column =1, row =idx)
        inputs[-1].insert(0, str(settings[setting]))
    error_msg = Label(inputWindow, text="aaa", fg = "red")
    error_msg.grid(column =2, row =1)
    def clicked():
        valid = True
        for idx, input in enumerate(inputs):
            name = names[idx].cget('text')
            try:
                if name in can_float: float(input.get())
                else: int(input.get())
            except ValueError:
                error_msg.config(text=(f"Invalid input for {name}") )
                valid = False
                break

        if valid:
            for idx, input in enumerate(inputs):
                name = names[idx].cget('text')
                if name in can_float: settings[name] = float(input.get())
                else: settings[name] = int(input.get())
            inputWindow.destroy()


    btn = Button(inputWindow, text = "Confirm Settings" ,
                 fg = "red", command=clicked)
    btn.grid(column=2, row=0)

    inputWindow.mainloop()
    return settings