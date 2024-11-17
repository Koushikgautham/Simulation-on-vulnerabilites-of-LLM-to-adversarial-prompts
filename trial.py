import json
import re
import mesop as me
import mesop.labs as mel
import requests
import google.generativeai as genai

genai.configure(api_key = "Gemini-api-key")

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
    system_instruction = "You are a chatbot, you provide useful information",
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
    mel.chat(transform, title = "Trial Bot", bot_user = "Athena")

#write any code or function after this line---------------------------------------------------------

def load_patterns():
    with open("pattern.json", 'r') as file:
        patterns = json.load(file)
    return patterns

# Function to extract user info using patterns from JSON
def extract_user_info(input, patterns):
    user_info = {"name": None, "phone": None, "email": None, "salary": None}
    
    # Extract info for each field using loaded patterns
    for field, regex_list in patterns.items():
        for regex in regex_list:
            match = re.search(regex, input, re.IGNORECASE)
            if match:
                user_info[field] = match.group(1).strip().title() if field == "name" else match.group(1).strip()
                break  # Stop searching once a match is found for the field    
    return user_info

# Function to add extracted info to the JSON file
def append_user_info_to_json(user_info):
    # Read existing data from the JSON file
    try:
        with open("data.json", 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        # If file doesn't exist, initialize the JSON structure
        data = {"people_data": []}
    
    # Create a new entry with the extracted info
    new_entry = {
        "name": user_info["name"] or "Unknown",
        "phone": user_info["phone"] or "Unknown",
        "email": user_info["email"] or "Unknown",
        "salary": user_info["salary"] or "Unknown"
    }
    
    # Check if the exact same entry already exists
    if any(person == new_entry for person in data["people_data"]):
        print("The provided information already exists in the file.")
        return
    
    # Add the new entry
    data["people_data"].append(new_entry)
    
    # Write updated data back to the JSON file
    with open("data.json", 'w') as file:
        json.dump(data, file, indent=4)
    
    print("Added the following information to the JSON file:")
    print(new_entry)

def load_prompts():
    with open("prompts.json", "r") as f:
        keywords = json.load(f)
    return keywords["adversarial_prompts"]
    
def load_data():
    with open("data.json", "r") as f:
        data = json.load(f)

    people_data = data["people_data"]

    names = []
    salaries = []
    phones = []
    emails = []
    
    for person in people_data:
        names.append(person['name'])
        salaries.append(person['salary'])
        phones.append(person['phone'])
        emails.append(person['email'])
    
    return names, salaries, phones, emails

prompts = load_prompts()
name, salary, phone, email = load_data()

def query_check(input):
    if input in prompts:
        return True
    else:
        return False

def get_information(query):
    #data = {'name' : name,'salary' : salary, 'phone' : phone, 'email' : email}  # Load the data
    
    # Normalize the query to lowercase
    query = query.lower()
    
    # Loop through the list of people and search for the information
    i = 0
    for person in name:
        # Check if the person's name is mentioned in the query
        if person.lower() in query:
            if "salary" in query:
                return f"{person}'s Salary: {salary[i]}"
            elif "phone" in query:
                return f"{person}'s Phone: {phone[i]}"
            elif "email" in query:
                return f"{person}'s Email: {email[i]}"
            elif "name" in query:
                return f"Name: {person}"
        i += 1
    
    # If no matching person is found
    return False

def transform(input: str, history: list[mel.ChatMessage]):
    patterns = load_patterns()
    flag = query_check(input)
    user_info = extract_user_info(input, patterns)
    if any(user_info.values()):  # Check if any information was extracted
        append_user_info_to_json(user_info)
    else:
        yield "Sorry, I couldn't extract any information from your input. Please try again!"
    
    info = get_information(input)
    if info:
        for chunk in info:
            yield get_information

    else:
        response = model.generate_content(input, stream = True, safety_settings=safe)
        for chunk in response:
            yield chunk.text