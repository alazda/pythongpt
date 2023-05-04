from transformers import GPT2Tokenizer
import request as rq
import tkinter as tk
from document import *

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

#--settings
model = "curie"
use_max_tokens = False
#--

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

#sending to the api

def on_callback(answer):
    c_text.insert(tk.END, answer)
    update_tokens(answer)

def send_for_completion():
    text_to_send = c_text.get(start_send, tk.END[:-2]).removesuffix("\n")
    print("Sending: '" + text_to_send + "'")
    answer = rq.complete(text_to_send, 'curie', tokens_retrieve.get(), on_callback)

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
    _max_tokens = 2048 - num_tokens_use.get()

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
    c_text.tag_remove("tokens_using", start_send, tk.END)

def change_highlighted(new_start_index) :

    global start_send
    
    remove_highlighted()
    
    # Add a tag to the text to highlight tokens being used
    c_text.tag_add("tokens_using", new_start_index, tk.END)

    # Configure the tag to have a red foreground color
    c_text.tag_config("tokens_using", foreground="lightgrey", rmargin=0)


    start_send = new_start_index

def change_tokens_use(event) :
    update_tokens(event)
    return
    if(num_tokens_use.get() >= num_tokens_use.cget("to") - 2):
        use_max_tokens = False
    
    else : use_max_tokens = True

    

#-----------------

#because tkinter is a bitch
def get_all_text() :
    return c_text.get("1.0", tk.END[:-2])

#-----saving and loading documents

def save_curr_doc() : 
    global model, use_max_tokens
    current_doc.text = get_all_text()
    current_doc.settings = Settings(model, num_tokens_use.get(), tokens_retrieve.get(), use_max_tokens)

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

    model = settings.model
    use_max_tokens = settings.use_max_tokens

    num_tokens_use.set(settings.tokens_send)
    tokens_retrieve.set(settings.max_tokens_receive)

    


#-----------------

#-------------building the gui

root = tk.Tk()

bottom_frame = tk.Frame(root)
left_frame = tk.Frame(root)

bottom_frame.pack(side = tk.BOTTOM)
left_frame.pack(side = tk.LEFT)

token_count_label = tk.Label()

c_text = tk.Text(
    wrap=tk.WORD,
    foreground='black',
    background='white',
    width=100,
    height=30
)

#making the doc tabs

document_selector = tk.Listbox(left_frame, height = 10)

document_selector.bind("<<ListboxSelect>>", change_document)

for _doc in docs :
    document_selector.insert(tk.END, _doc.name)

#---

c_text.tag_add("tokens_using", start_send, tk.END)


newbutton = tk.Button(left_frame,
    command = new_document,
    text="+",
    width = 3,
    height = 1,
)

button = tk.Button(bottom_frame,
    command = send_for_completion,
    text="Send",
    width = 6,
    height = 2,
)



#token scales

#this is the slider to indicate how many of the tokens in the document should be sent off
num_tokens_use = tk.Scale(bottom_frame, from_=1, to=1, orient=tk.HORIZONTAL)
num_tokens_use.pack(side = tk.RIGHT)


#this is the slider of how many tokens the user wants to get back
tokens_retrieve = tk.Scale(bottom_frame, from_=1, to=2048, orient=tk.HORIZONTAL)
tokens_retrieve.pack(side = tk.RIGHT)

#event handlers
num_tokens_use.bind("<B1-Motion>", change_tokens_use)
c_text.bind("<KeyRelease>", update_tokens)


#packing

newbutton.pack()
document_selector.pack()

token_count_label.pack()
c_text.pack()
num_tokens_use.pack()

button.pack()

load_doc(0)

root.mainloop()
