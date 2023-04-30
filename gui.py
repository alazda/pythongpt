from transformers import GPT2Tokenizer
import tkinter as tk
import request as rq

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

last_highlight_index = "1.0"

#scripts
def on_callback(answer):
    text.insert(tk.END, answer)
    update_tokens(answer)

def send_for_completion():
    answer = rq.complete(text.get("1.0"), 'davinci', tokens_retrieve.get(), on_callback)

    
def update_tokens(event):
    #calculates the tokens
    tokens = tokenizer.encode(text.get("1.0", tk.END))

    token_strings = [tokenizer.decode(token) for token in tokens]

    #number of tokens
    num_tokens = len(tokens)

    #sets the number of tokens in the gui
    token_count_label.config(text = num_tokens)

    #the max tokens that can be used assuming a max 2048 context size
    _max_tokens = 2048 - tokens_use.get()

    #recalibrates the scalers based on the token limits and such
    tokens_use.config(to=num_tokens)
    tokens_retrieve.config(to=(_max_tokens))

    #total characters in the text
    char_count = int(text.index("end-1c").split('.')[1])

    token_start_index = char_count + 1

    for i in range(num_tokens - 1, -1, -1) :
        _string = token_strings[i]

        chars_in_token = len(_string)
        
        token_start_index -= chars_in_token
        
        if i <= num_tokens - tokens_use.get() :
            break

    start_index_string = "1." + str(token_start_index)

    change_highlighted(start_index_string)

    

def change_highlighted(new_start_index) :

    global last_highlight_index
    
    text.tag_remove("tokens_using", last_highlight_index, tk.END)
    
    # Add a tag to the text to highlight tokens being used
    text.tag_add("tokens_using", new_start_index, tk.END)

    # Configure the tag to have a red foreground color
    text.tag_config("tokens_using", foreground="lightgrey", rmargin=0)


    last_highlight_index = new_start_index

def change_document(event) :
    document_list.get()
    return

def new_document() :
    d_list.append("another")
    documents.set(d_list)

#building the gui
window = tk.Tk()

bottom_frame = tk.Frame(window)
left_frame = tk.Frame(window)
bottom_frame.pack(side = tk.BOTTOM)
left_frame.pack(side = tk.LEFT)

token_count_label = tk.Label()

text = tk.Text(
    foreground='white',
    background='black',
    width=100,
    height=30
)

d_list = ["new"]

documents = tk.Variable(value=d_list)

document_list = tk.Listbox(left_frame, height = 5, listvariable=documents)

text.tag_add("tokens_using", last_highlight_index, tk.END)


newbutton = tk.Button(left_frame,
    command = new_document,
    text="+",
    width = 3,
    height = 1,
)

button = tk.Button(bottom_frame,
    command = send_for_completion,
    text="Send",
    width = 10,
    height = 3,
)



#token scales

#this is the slider to indicate how many of the tokens in the document should be sent off
tokens_use = tk.Scale(bottom_frame, from_=1, to=1, orient=tk.HORIZONTAL)
tokens_use.pack(side = tk.RIGHT)


#this is the slider of how many tokens the user wants to get back
tokens_retrieve = tk.Scale(bottom_frame, from_=1, to=2048, orient=tk.HORIZONTAL)
tokens_retrieve.pack(side = tk.RIGHT)

#event handlers
tokens_use.bind("<B1-Motion>", update_tokens)
text.bind("<KeyRelease>", update_tokens)
document_list.bind("<<ListboxSelect>>", change_document)

#packing

newbutton.pack()
document_list.pack()

token_count_label.pack()
text.pack()
tokens_use.pack()

button.pack()

window.mainloop()
