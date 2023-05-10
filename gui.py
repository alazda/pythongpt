from transformers import GPT2Tokenizer
import request as rq
import tkinter as tk
import tkinter.ttk as ttk
from document import *
import theme as th
import os

import subprocess

from tkinter import filedialog

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

#-- global settings
models = { "ada" : 2049 , "babbage" : 2049 , "curie" : 2049 , "davinci" : 2049, "text-davinci-002" : 4097, "text-davinci-003" : 4097, 
          "text-ada-001" :  2049, "text-babbage-001" : 2049,  "text-curie-001" : 2049}

theme = th.Theme("Default")
#--

#-- not so global settings
use_max_tokens = False
#--
start_send = "1.0"
#--

docs = []

#initialise first doc
def initial_doc() :
    new_doc = Document("new", "hello world!", Settings("curie", 1, 1, False))
    docs.append(new_doc)

initial_doc()

current_doc = docs[0]
#----

#--- change theme

def change_theme(event) :
    global theme
    theme = th.Theme(theme_selected.get())
    print("Changing to:" + theme.name)
    update_theme()

def update_theme() :
    c_text.config(bg=theme.bg, fg=theme.text_colour, font=(theme.font, theme.font_size),  highlightbackground=theme.highlight_colour)
#---
#sending to the api

def on_callback(answer):
    c_text.tag_remove("last_sent", "1.0", tk.END)
    c_text.insert(tk.END, answer, "last_sent")
    update_tokens(answer)
    c_text.tag_config("last_sent", foreground=theme.last_sent_colour, rmargin=0)

def send_for_completion():
    text_to_send = c_text.get(start_send, tk.END).removesuffix("\n")
    print("Sending: '" + text_to_send + "'")
    answer = rq.complete(text_to_send, model.get(), tokens_retrieve.get(), on_callback)

def resend_for_completion():
    remove_last_sent_text()
    update_tokens("")
    text_to_send = c_text.get(start_send, tk.END).removesuffix("\n")
    print("Sending: '" + text_to_send + "'")
    answer = rq.complete(text_to_send, model.get(), tokens_retrieve.get(), on_callback)

#-----token calulation and such

def update_tokens(event):
    #calculates the tokens
    to_tokenize = get_all_text()

    #print(to_tokenize)

    tokens = tokenizer.encode(to_tokenize)

    token_strings = [tokenizer.decode(token) for token in tokens]

    #number of tokens
    num_tokens = len(tokens)

    #sets the number of tokens in the gui
    token_count_label.config(text = num_tokens)

    #the max tokens that can be used assuming a max 2048 context size
    _max_tokens = models[model.get()] - num_tokens_use.get()

    #recalibrates the scalers based on the token limits and such

    num_tokens_use.config(to=num_tokens)

    global use_max_tokens

    if(use_max_tokens) :
        num_tokens_use.set(num_tokens_use.cget("to"))

    tokens_retrieve.config(to=(_max_tokens))

    #total characters in the text
    char_count = len(get_all_text())

    token_start_index = char_count


    for i in range(num_tokens - 1, -1, -1) :
        _string = token_strings[i]

        chars_in_token = len(_string)
        
        token_start_index -= chars_in_token
        
        if i <= num_tokens - num_tokens_use.get() :
            break

    tk_pos = c_text.index(f'1.0 + {token_start_index} chars')

    #print("Pos: " + tk_pos)

    change_highlighted(tk_pos)

def remove_highlighted() :
    c_text.tag_remove("tokens_using", "1.0", tk.END)

def change_highlighted(new_start_index) :

    global start_send
    
    remove_highlighted()
    
    # Add a tag to the text to highlight tokens being used
    c_text.tag_add("tokens_using", new_start_index, "end - 1 char")

    # Configure the tag to have a red foreground color
    c_text.tag_config("tokens_using", background=theme.token_select_colour, rmargin=0)


    start_send = new_start_index

def remove_last_sent_text():
    # Get the list of start and end indices for the 'red' tag
    ranges = c_text.tag_ranges("last_sent")

    # Iterate over the indices in reverse order and remove the text with the 'red' tag
    for i in range(len(ranges)-1, 0, -2):
        start_index = ranges[i-1]
        end_index = ranges[i]
        c_text.delete(start_index, end_index)

def change_tokens_use(event) :
    update_tokens(event)
    return
    if(num_tokens_use.get() >= num_tokens_use.cget("to") - 2):
        use_max_tokens = False
    
    else : use_max_tokens = True

def change_model(event) :
    global model
    tokens_retrieve.config(to=models[model.get()])
    

#-----------------

#because tkinter is a b
def get_all_text() :
    return c_text.get("1.0", tk.END).removesuffix("\n")

#-----saving and loading documents

def save_curr_doc() : 
    global model, use_max_tokens
    current_doc.text = get_all_text()
    current_doc.settings = Settings(model.get(), num_tokens_use.get(), tokens_retrieve.get(), use_max_tokens)

def change_document(event) :
    save_curr_doc()
    index = document_selector.curselection()[0]
    print("doc index: " + str(index))
    load_doc(index)
    return

def new_document() :
    save_curr_doc()

    new_doc = Document("new2", "hello world2!", Settings("curie", 1, 1, False))

    docs.append(new_doc)

    document_selector.insert(tk.END, new_doc.name)

    load_doc(len(docs) - 1)
    return

def load_doc(index) :
    global current_doc, settings

    current_doc = docs[index]
    settings = current_doc.settings

    load_settings()

    remove_highlighted()

    start_send = "1.0"

    c_text.delete("1.0", tk.END)
    c_text.insert("1.0", current_doc.text)
    c_text.delete(tk.END + "-1c")

    update_tokens(None)

def load_settings() :
    global settings, model, use_max_tokens

    model.set(settings.model)
    use_max_tokens = settings.use_max_tokens

    num_tokens_use.set(settings.tokens_send)
    tokens_retrieve.set(settings.max_tokens_receive)

    
def save_to_file() :


    filename = "./save/" + current_doc.name + ".txt"

    with open(filename, "w") as f:
        f.write(get_all_text())

def save_as_to_file() :

    #filedialogue = tk.filedialog

    filename = tk.filedialog.asksaveasfilename(initialdir = "./save/", title = "Select file", filetypes = (("text files","*.txt"),("all files","*.*")))

    with open(filename, "w") as f:
        f.write(get_all_text())

#-----------------

#----
def get_installed_fonts():
    output = subprocess.check_output(['fc-list'])
    font_list = output.decode('utf-8').split('\n')
    fonts = []

    for font in font_list:
        try:
            font_name = font.split(':')[1].split(',')[0].strip()
            if font_name not in fonts:
                fonts.append(font_name)
        except:
            pass

    return fonts

root = tk.Tk()

font = tk.Variable(root, ("Courier", 12))

root.columnconfigure(0, minsize = 100)
root.columnconfigure(1, weight= 5)
root.columnconfigure(2, minsize= 100)

root.rowconfigure(0, minsize = 50)
root.rowconfigure(1, weight = 5)
root.rowconfigure(2, minsize= 50)


bottom_frame = tk.Frame(root)
left_frame = tk.Frame(root)
text_frame = tk.Frame(root)

bottom_frame.grid(column=1,row=2, sticky="s")
left_frame.grid(column=0, row=1, sticky="w")
text_frame.grid(column=1, row=1, sticky="nsew")   

token_count_label = tk.Label()

c_text = tk.Text(
    text_frame,
    font = font,
    wrap=tk.WORD,
    foreground='black',
    background='white',
)

#making the doc tabs



document_selector = tk.Listbox(left_frame, height = 10)

document_selector.bind("<<ListboxSelect>>", change_document)

for _doc in docs :
    document_selector.insert(tk.END, _doc.name)

#---

c_text.tag_add("tokens_using", start_send, tk.END)
c_text.tag_add("last_sent", tk.END, tk.END)



new_doc_button = tk.Button(left_frame,
    command = new_document,
    text="+",
    width = 3,
    height = 1,
)

send_button = tk.Button(bottom_frame,
    command = send_for_completion,
    text="Send",
    width = 6,
    height = 2,
)

resend_button = tk.Button(bottom_frame,
    command = resend_for_completion,
    text="Resend",
    width = 6,
    height = 2,
)

save_button = tk.Button(left_frame,
    command = save_to_file,
    text="Save",
    width = 6,
    height = 2,
)

save_as_button = tk.Button(left_frame,
    command = save_as_to_file,
    text="Save As",
    width = 3,
    height = 2,
)

#options menu
def open_options():
    if not options_window.winfo_viewable() :
        options_window.deiconify()
        options_window.lift()

def close_options_window(): 
    options_window.withdraw()  

options_button = tk.Button(root, text="Options", command=open_options)

options_window = tk.Toplevel(root)

options_window.geometry("200x200")

options_window.attributes('-top', 1)
    
options_window.title("Options")

options_window.protocol("WM_DELETE_WINDOW", close_options_window)

themes = []

path = "./themes/"

theme_selected = tk.StringVar(options_window)

theme_selected.set("Default")

for theme_p in os.listdir(path):
# get all file names and add to the list
    if os.path.isfile(os.path.join(path, theme_p)):
        themes.append(theme_p.split(".")[0])

theme_menu = tk.OptionMenu(options_window, theme_selected, *themes)

theme_menu.bind("<<OptionMenuSelect>>", change_theme)

theme_menu.pack()

options_window.withdraw()

#----

#model selection

model_strings = list(models.keys())

model = tk.StringVar(bottom_frame)

model.set("curie")

model_select = tk.OptionMenu(bottom_frame, model, *model_strings, command = change_model)

send_button.pack(side=tk.RIGHT)

resend_button.pack(side=tk.RIGHT)

#token scales

#this is the slider to indicate how many of the tokens in the document should be sent off
num_tokens_use = tk.Scale(bottom_frame, from_=1, to=1, orient=tk.HORIZONTAL)
num_tokens_use.pack(side = tk.RIGHT)


#this is the slider of how many tokens the user wants to get back
tokens_retrieve = tk.Scale(bottom_frame, from_=1, to=models[model.get()], orient=tk.HORIZONTAL)
tokens_retrieve.pack(side = tk.RIGHT)

#event handlers
num_tokens_use.bind("<B1-Motion>", change_tokens_use)
c_text.bind("<KeyRelease>", update_tokens)


#packing

new_doc_button.pack()
document_selector.pack()

token_count_label.grid(column=1, row = 0)
c_text.place(x=0, y= 0, relheight=1, relwidth=1)
num_tokens_use.pack()



save_button.pack()

save_as_button.pack()

model_select.pack()

options_button.grid(column=0, row = 0)


load_doc(0)

update_theme()

root.mainloop()
