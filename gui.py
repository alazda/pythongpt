from transformers import GPT2Tokenizer
import request as rq
import tkinter as tk

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

start_send = "1.0"

use_max_tokens = True

#scripts
def on_callback(answer):
    text.insert(tk.END, answer)
    update_tokens(answer)

def send_for_completion():
    text_to_send = text.get(start_send, tk.END)
    print("Sending: '" + text_to_send + "'")
    answer = rq.complete(text_to_send, 'curie', tokens_retrieve.get(), on_callback)

    
def update_tokens(event):
    #calculates the tokens
    to_tokenize = text.get("1.0", tk.END)

    #print(to_tokenize)

    tokens = tokenizer.encode(to_tokenize)





    token_strings = [tokenizer.decode(token) for token in tokens]

    #number of tokens
    num_tokens = len(tokens)

    #sets the number of tokens in the gui
    token_count_label.config(text = num_tokens)

    #the max tokens that can be used assuming a max 2048 context size
    _max_tokens = 2048 - tokens_use.get()

    #recalibrates the scalers based on the token limits and such

    tokens_use.config(to=num_tokens)

    if(use_max_tokens) :
        tokens_use.set(tokens_use.cget("to"))

    tokens_retrieve.config(to=(_max_tokens))

    #total characters in the text
    char_count = len(text.get("1.0", tk.END))

    #print("chars total: " + str(char_count))

    token_start_index = char_count


    for i in range(num_tokens - 1, -1, -1) :
        _string = token_strings[i]

        chars_in_token = len(_string)
        
        token_start_index -= chars_in_token
        
        if i <= num_tokens - tokens_use.get() :
            break

    tk_pos = text.index(f'1.0 + {token_start_index} chars')

    #print("Pos: " + tk_pos)

    change_highlighted(tk_pos)

    

def change_highlighted(new_start_index) :

    global start_send
    
    text.tag_remove("tokens_using", start_send, tk.END)
    
    # Add a tag to the text to highlight tokens being used
    text.tag_add("tokens_using", new_start_index, tk.END)

    # Configure the tag to have a red foreground color
    text.tag_config("tokens_using", foreground="lightgrey", rmargin=0)


    start_send = new_start_index

def change_tokens_use(event) :
    if(tokens_use.get() >= tokens_use.cget("to") - 2):
        use_max_tokens = False
    
    else : use_max_tokens = True

    update_tokens(event)

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
    wrap=tk.WORD,
    foreground='white',
    background='black',
    width=100,
    height=30
)

d_list = ["new"]

documents = tk.Variable(value=d_list)

document_list = tk.Listbox(left_frame, height = 5, listvariable=documents)

text.tag_add("tokens_using", start_send, tk.END)


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
tokens_use.bind("<B1-Motion>", change_tokens_use)
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
