import tkinter as tk

class Document :
    def __init__(self, name, text, settings, save_path = None) :
        self.name = name
        self.text = text
        self.settings = settings
        self.save_path = save_path
    
class Settings : 
    def __init__(self, model, tokens_send, max_tokens_receive, use_max_tokens) :
        self.model = model
        self.tokens_send = tokens_send
        self.max_tokens_receive = max_tokens_receive
        self.use_max_tokens = use_max_tokens

