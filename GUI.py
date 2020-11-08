from tkinter import * 
from tkinter.ttk import * 
from tkinter import filedialog
from tkinter import font
from tkinter import messagebox


root = Tk()
root.title("Me My Self and I ")
root.geometry("820x500")

# Varioble for Open file
global open_status_name 
open_status_name = False

global selected
selected = False


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

    # Varioble for Open file
    #global open_status_name 
    #open_status_name = False
  
#####################################################
# OPEN FILE 
#####################################################
def open_file():
    # delete previous text
    editor.delete("1.0", END)
    # grab file name
    # change dir to C:\Users\bryan\Documents
    text_file = filedialog.askopenfilename(initialdir=directory, title="Open File", filetypes=(("Text Files", "*.txt"), ("Marving files", "*.marving"), ("All Files", "*.*")))
    
    # Check if file name exisrs 
    if text_file:
        global open_status_name 
        open_status_name = text_file
        
    
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
        messagebox.showinfo("Succesfuly saved", "Saved correctly")

#####################################################
# SAVE FILE 
#####################################################
def save_file():
    global open_status_name 
    if open_status_name:
        text_file = open(open_status_name, 'w')
        text_file.write(editor.get("1.0", END))
        text_file.close()
        messagebox.showinfo("Succesfuly saved", "Saved correctly")
    else:
        save_as_file() 

#####################################################
# CUT TEXT
#####################################################
def cut_text(e):
    global selected
    if e:
        selected = root.clipboard_get() 
    else:
        if editor.selection_get(): 
            # Get selected 
            selected = editor.selection_get();
            #delete selected from selected 
            editor.delete("sel.first", "sel.last")

            root.clipboard_clear() 
            root.clipboard_append(selected)

#####################################################
# COPY TEXT
#####################################################
def copy_text(e):
    global selected
    #Check if keyboard command used
    if e:
        selected = root.clipboard_get()

    if editor.selection_get():
        # Get selected 
        selected = editor.selection_get();
        root.clipboard_clear() 
        root.clipboard_append(selected)

#####################################################
# PASTE TEXT
#####################################################
def paste_text(e):
    global selected
    if e:
        selected = root.clipboard_get()
    else:
        if selected:
            position = editor.index(INSERT)
            editor.insert(position, selected)

            root.clipboard_clear() 
            root.clipboard_append(selected)


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



#####################################################
# #Main Frame
#####################################################
editor = Text(root, width=30, font=("Helvetica", 12), undo=True, wrap="none", bg="#003340", fg="white")

editor.grid(row=3, column=0, columnspan=1)
comp = Text(root, width=30,  font=("Helvetica", 12), bg="#012b36", fg="yellow")
comp.grid(row=3, column=1, columnspan=1)

#Create Menu
my_menu = Menu(root)
root.config(menu=my_menu)

#Add File Menu
file_menu = Menu(my_menu, tearoff=False)
my_menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="New", command=new_file)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file )
file_menu.add_command(label="Save as", command=save_as_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

#Add Edit Menu
edit_menu = Menu(my_menu, tearoff=False)
my_menu.add_cascade(label="Edit", menu=edit_menu)
edit_menu.add_command(label="Cut       (Ctrl+X)", command=lambda: cut_text(False))
edit_menu.add_command(label="Copy    (Ctrl+C)", command=lambda: copy_text(False))
edit_menu.add_command(label="Paste    (Ctrl+V)", command=lambda: paste_text(False))
edit_menu.add_command(label="Undo", command=editor.edit_undo, accelerator="(Ctrl+z)")
edit_menu.add_command(label="Redo", command=editor.edit_redo, accelerator="(Ctrl+y)")


# Edit Bindings 
root.bind('<Control-Key-x>', cut_text)
root.bind('<Control-Key-c>', copy_text)
root.bind('<Control-Key-v>', paste_text)



#####################################################
# CONNECT TO LANGUAGE 
#####################################################
import shell

#def connector():

# https://stackoverflow.com/questions/36333293/write-to-terminal-in-tkinter-gui



############################################################################################
root.mainloop() 


# https://www.youtube.com/watch?v=yG0fAUn2uB0&list=PLCC34OHNcOtoC6GglhF3ncJ5rLwQrLGnV&index=106

