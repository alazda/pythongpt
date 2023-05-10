import openai
import os

with open('./' + 'openai_key.txt', 'r') as f:
    api_key = f.read().strip()

openai.api_key = api_key

print(openai.api_key)

def complete(text, _model, num_tokens, callback):
    response = openai.Completion.create(model=_model, prompt=text, max_tokens = num_tokens)
    answer = response.choices[0]['text']
    callback(answer)

def chat(history, _model, num_tokens, callback):
    response = openai.ChatCompletion.create(model = _model, messageSs = history, max_tokens = num_tokens)
    callback(response)

def create_embedding(text, _model, callback):
    response = openai.Embedding.create(model = _model, input = text)
    callback(response)