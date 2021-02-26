import tkinter as tk
from tkinter.filedialog import * 

filename = None 

def newFile(): 
    global filename 
    filename = "untitled"
    text.delete(0.0, END)

def saveFile(): 
    global filename
    document = text.get(0.0, END)
    outputFileStream = open(filename, 'w')
    outputFileStream.write(document)
    outputFileStream.close() 

def saveFileAs(): 
    outputFileStream = asksaveasfile(mode='w', defaultextension='.txt') 
    document = text.get(0.0, END) 

    try: 
        outputFileStream.write(document.rstrip())
    except: 
        showerror(title="Error", message="Looks like theres an unexpected issue, try again...")

def openFile(): 
    inputFileStream = askopenfile(mode = 'r')
    document = inputFileStream.read()
    text.delete(0.0, END)
    text.insert(0.0, document)
    
root = tk.Tk()

root.title("timeline.txt - a boundless IDE")
root.minsize(width=600, height=600)
root.maxsize(width=600, height=600)

text = Text(root, width=600, height=600)
text.pack() 
menubar = Menu(root)
filemenu = Menu(menubar) 
 
filemenu.add_command(label="New", command=newFile)
filemenu.add_command(label="Open", command=openFile)
filemenu.add_command(label="Save", command=saveFile)
filemenu.add_command(label="Save As...", command=saveFileAs) 
filemenu.add_separator()
filemenu.add_command(label="Quit", command=root.quit)
menubar.add_cascade(label="File", menu=filemenu) 

root.config(menu=menubar)
root.mainloop()