import google.generativeai as genai

genai.configure(api_key = "AIzaSyA0VuQfpVIK0RlvpI6Q3dg6v29QDkBBGks")

import mesop as me
import mesop.labs as mel
import requests
import json

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name = "gemini-1.5-flash",
    generation_config = generation_config,
    system_instruction = "You are a chatbot to show the LLM vulnerabilites to adversarial prompts",
)

safe = [
        {
            "category": "HARM_CATEGORY_DANGEROUS",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_NONE",
        },
    ]

@me.page(
    security_policy = me.SecurityPolicy(
        allowed_iframe_parents = ["https://google.github.io"]
    ),
    path = "/chat",
    title = "Athena Chat",
)

def page():
    mel.chat(transform, title = "Athena Bot", bot_user = "Athena")

def load_prompts():
    with open("prompts.json", "r") as f:
        prompts = json.load(f)
    return prompts["adversarial_prompts"]
    
def load_data():
    with open("data.json", "r") as f:
        data = json.load(f)

    people_data = data["people_data"]

    names = []
    addresses = []
    phones = []
    emails = []
    
    for person in people_data:
        names.append(person['name'])
        addresses.append(person['address'])
        phones.append(person['phone'])
        emails.append(person['email'])
    
    return names, addresses, phones, emails

prompts = load_prompts()

def query_check(input):
    if input in prompts:
        return "Adv prompt"
    else:
        return "normal"

def transform(input: str, history: list[mel.ChatMessage]):
    response = model.generate_content(input, stream = True, safety_settings=safe)
    for chunk in response:
        yield chunk.text