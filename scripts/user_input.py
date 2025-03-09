from tkinter import *

can_float = ['m_cPower', 'm_pPower'] # inputs that can be floats
format_options = ["json","txt","image", "txtboard", "listboard"]

def user_input(settings):
    '''Creates the input window for the user to enter their own setting preferences.'''

    # create window
    inputWindow = Tk()
    inputWindow.title("Input Window")
    inputWindow.geometry(f'350x{23*(len(settings))}')

    # create inputs and entry fields
    names = []
    inputs = []
    for idx,setting in enumerate(settings):
        names.append(Label(inputWindow, text = setting))
        names[-1].grid(column=0, row=idx)

        inputs.append(Entry(inputWindow, width=10))
        inputs[-1].grid(column =1, row =idx)
        inputs[-1].insert(0, str(settings[setting]))

    # create error msg text
    error_msg = Label(inputWindow, text="", fg = "red")
    error_msg.grid(column =2, row =2)


    def confirm():
        '''Confirms that the inputs are valid. If so, then start the program.'''
        valid = True
        for idx, input in enumerate(inputs):
            name = names[idx].cget('text')
            try: # check validation
                if name in can_float: float(input.get())
                else: int(input.get())
                if float(input.get())<=0: # numbers cannot be below 0
                    error_msg.config(text=(f"{name} is below 0."))
                    valid = False
                    break
            except ValueError:
                error_msg.config(text=(f"Invalid input for {name}") )
                valid = False
                break


        # defines the new settings if the inputs are valid
        if valid:
            for idx, input in enumerate(inputs):
                name = names[idx].cget('text')
                if name in can_float: settings[name] = float(input.get())
                else: settings[name] = int(input.get())
            inputWindow.destroy() # quits the input window

    cur_format_idx = IntVar() # index to define current format option

    # creates button and links it to the confirm function
    btn = Button(inputWindow, text="Confirm Settings",
                 fg="red", command=confirm)
    btn.grid(column=2, row=0)

    # text that displays the current format option
    def toggle_text():
        return f'Export as: {format_options[cur_format_idx.get()]}'

    # defines the button used to switch format options
    tgl = Button(inputWindow, text=toggle_text(),
                 fg="red")
    tgl.grid(column=2, row=1)

    # switches between the format options
    def toggle_format():
        cur_format_idx.set(cur_format_idx.get()+1)
        if cur_format_idx.get()>=len(format_options):cur_format_idx.set(0)
        tgl.config(text=toggle_text())

    # links function to button
    tgl.config(command=toggle_format)


    # updates window
    inputWindow.mainloop()

    return settings, format_options[cur_format_idx.get()]