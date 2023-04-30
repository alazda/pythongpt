import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def complete(text, _model, num_tokens, callback):
    response = openai.Completion.create(model=_model, prompt=text, max_tokens = num_tokens)
    answer = response.choices[0]['text']
    callback(answer)

def chat(history, _model, num_tokens, callback):
    response = openai.ChatCompletion.create(model = _model, messageSs = history, max_tokens = num_tokens)
    callback(response)
