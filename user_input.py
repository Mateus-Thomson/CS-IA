from tkinter import *

can_float = ['m_cPower', 'm_pPower']
format_options = ["json","txt","image","tiled"]
format_idx = 0

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
    error_msg = Label(inputWindow, text="", fg = "red")
    error_msg.grid(column =2, row =2)

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
    value = IntVar()

    def toggle_text():
        return f'Export as: {format_options[value.get()]}'
    tgl = Button(inputWindow, text=toggle_text(),
                 fg="red")
    tgl.grid(column=2, row=1)

    def toggle_format():
        value.set(value.get()+1)
        if value.get()>=len(format_options):value.set(0)
        tgl.config(text=toggle_text())
    tgl.config(command=toggle_format)

    btn = Button(inputWindow, text = "Confirm Settings" ,
                 fg = "red", command=clicked)
    btn.grid(column=2, row=0)

    inputWindow.mainloop()
    return settings