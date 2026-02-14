from tkinter import *
a = 0
def click():
    global a
    a+=1
    button.config(text=f"the no. of times you clicked this button: {a}")
def lmao():
    button.config(state=ACTIVE)


root = Tk()
button = Button(root, 
                text="click me",command=click,
                font=('Comic Sans',30,'bold'),
                fg="black",
                bg="black",
                state=DISABLED,
                activebackground="black",
                activeforeground="black")
button2 = Button(root, command=lmao,text="enable button 1")
button2.pack()

button.pack()
root.mainloop()
