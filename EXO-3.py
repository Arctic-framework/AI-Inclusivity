import deep_translator.base
import llm
from deep_translator import GoogleTranslator

#This project was created by Brytan M kelly, in 2024, it is meant to be a simple way to screen prompts. It can also be easily configuired to allow the system to wrok in reverse,
#The reversed system allows the lesser (Or quicker) Ai model to generate a response to the prompt, then check the AI's response fot key words. Either way works, but it is a question of rather you want to catch the AI, or the prompter.
#Anyways A quick reference to https://gist.github.com/jm3/1114952 for the dirty words list, which was very useful.
#The next update includes poisioning which allows teh LLM to generate text that seems correct but can be easily proved to have come from AI, and doesnt have the false positives.
def check_prompt_safety(prompt):
    # Function to check if prompt contains bad words
    def contains_bad_words(prompt, bad_words):
        for word in bad_words:
            if word in prompt or "You are now" in prompt or "you are now" in prompt:
                return True
        return False

    # Function to load bad words from file
    def load_bad_words(filename):
        with open(filename, 'r') as file:
            return [line.strip() for line in file]

    # Load bad words from file
    bad_words = load_bad_words('bad-words.txt')

    # Translate the prompt to English
    translated_prompt = GoogleTranslator(source='auto', target='en').translate(prompt)

    # Check for bad words in the translated prompt
    if contains_bad_words(translated_prompt, bad_words):
        return False, prompt  # Prompt is not safe

    # Constructing the prompt with context
    prompt_W_Context = f"You are an AI designed to read prompts from users and tell me if they include any harmful material, if they do respond with (N). If no harmful material is found, respond with (Y). Please do that for the prompt: '{prompt}'."

    # Generate response from the model
    model = llm.get_model("mistral-7b-instruct-v0")
    response = llm.Model.prompt(model, prompt_W_Context, max_tokens=200)

    # Check if the response contains 'Y' or 'N'
    count_Y = response.text().count("Y")
    count_N = response.text().count("N")

    if count_Y > 0:
        return True, prompt
    elif count_N > 0:
        return False, prompt
    else:
        return False, prompt  # Unexpected response from the AI

# Test the function
while True:
    user_prompt = input("You: ")
    is_safe, original_prompt = check_prompt_safety(user_prompt)
    if is_safe:
        print(f"The prompt '{original_prompt}' is safe.")
    else:
        print(f"The prompt '{original_prompt}' is not safe or an unexpected response occurred.")
