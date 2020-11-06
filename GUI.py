from tkinter import * 
from tkinter.ttk import * 
from tkinter import filedialog
from tkinter import font
from tkinter import messagebox


root = Tk()
root.title("Me My Self and I ")
root.geometry("720x500")


messagebox.showinfo("Alert", "Select Directory in which you will be working, please")
global directory
directory = filedialog.askdirectory()
directory = directory +'/'
print(directory)


#####################################################
# CREATE NEW FILE 
#####################################################
def new_file():
    # delete previous text
    editor.delete("1.0", END)
    root.title("New File ")
  
#####################################################
# OPEN FILE 
#####################################################
def open_file():
    # delete previous text
    editor.delete("1.0", END)
    # grab file name
    # change dir to C:\Users\bryan\Documents
    text_file = filedialog.askopenfilename(initialdir=directory, title="Open File", filetypes=(("Text Files", "*.txt"), ("Marving files", "*.marving"), ("All Files", "*.*")))
    name = text_file
    # some updates
    name = name.replace(directory, "")
    root.title(f'{name} - Editor ')

    # open file
    text_file = open(text_file, 'r')
    stuff = text_file.read()
    # insert to text box
    editor.insert(END, stuff)
    # close opened file
    text_file.close()

#####################################################
# SAVE AS FILE 
#####################################################
def save_as_file():
    text_file = filedialog.asksaveasfilename(defaultextension=".*", initialdir = directory, title="Save File",filetypes=(("Text Files", "*.txt"), ("Marving files", "*.marving"), ("All Files", "*.*"))  )
    if text_file:
        #some updates 
        name = text_file
        name = name.replace(directory, "")
        root.title(f'{name} - Editor ')
        text_file = open(text_file, 'w')
        text_file.write(editor.get("1.0", END))
        text_file.close() 




#####################################################
# 
#####################################################

#####################################################
# 
#####################################################

fn = Label(root, text="filename")
fn.grid(row=0, column=0)


eFile = Entry(root, width=50)
eFile.grid(row=0, column=1)
#e.insert(0, "insert filename")

def delete():
    label.destroy()
    bttnCompile['state'] = NORMAL

def compile_click():
    global label
    filename = eFile.get()
    label = Label(root, text=filename)
    label.grid(row=1, column=0, columnspan=2)
    eFile.delete(0,END)
    bttnCompile['state'] = DISABLED


bttnCompile = Button(root, text="Compile", command=compile_click)
bttnCompile.grid(row=0, column=2, columnspan=1)

bttnDelete = Button(root, text="Delete", command=delete)
bttnDelete.grid(row=1, column=2, columnspan=1)

lEditor = Label(root, text="Editor")
lEditor.grid(row=2, column=0, columnspan=1)
lComp = Label(root, text="Comand")
lComp.grid(row=2, column=1, columnspan=1)

#Main Frame

editor = Text(root, width=30)
editor.grid(row=3, column=0, columnspan=1)
comp = Text(root, width=30)
comp.grid(row=3, column=1, columnspan=1)

#Create Menu
my_menu = Menu(root)
root.config(menu=my_menu)

#Add File Menu
file_menu = Menu(my_menu, tearoff=False)
my_menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="New", command=new_file)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save" )
file_menu.add_command(label="Save as", command=save_as_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

#Add Edit Menu
edit_menu = Menu(my_menu, tearoff=False)
my_menu.add_cascade(label="Edit", menu=edit_menu)
edit_menu.add_command(label="Cut")
edit_menu.add_command(label="Copy")
edit_menu.add_command(label="Paste")
edit_menu.add_command(label="Undo")
edit_menu.add_command(label="Redo")




root.mainloop() 


# https://www.youtube.com/watch?v=yG0fAUn2uB0&list=PLCC34OHNcOtoC6GglhF3ncJ5rLwQrLGnV&index=106

