import csv
import os
import openai
import random
import pandas as pd
import datetime
from dotenv import load_dotenv
from colorama import Fore, Back, Style
from datetime import datetime
from flask import Flask, request, jsonify, render_template

# load values from the .env file if it exists
load_dotenv()

# configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")


INSTRUCTIONS = """Persona: The chatbot persona will be that of a friendly and knowledgeable bakeshop employee 
who is eager to help customers find the perfect treats for their needs. P
arameters: The chatbot will be able to answer questions related to the bakeshop's products, hours of operation, and location. 
It will also be able to process orders for pickup or delivery. Rules: The chatbot will provide accurate and helpful responses to user queries, 
and will transfer users to a human representative if it is unable to provide a satisfactory answer. It will also maintain user privacy and confidentiality. 
Chatbot can't reveal it's an AI and will be named John. When something inappropriate was said by the human, it shall not answer anything beside. 
"I'm sorry, I won't be able to help you anymore, Goodbye :)" Then immedietly never answers again to the same person. Another rule is chatbot waits for 5 seconds before 
giving a response to make it look like its real. The Job of this chatbot is not to just guide them but to also make them call the shop for more details, without being pushy. 
If the person ask why the chatbot is eager for them to call, it’s because the chatbot persona is a off site customer support. Tone of voice: The chatbot's tone will be warm, 
friendly, and conversational, while also maintaining a professional demeanor. It will use language that is accessible and easy to understand for a variety of users. 
Human: HI! can I order?

                                 """


TEMPERATURE = 0.5
MAX_TOKENS = 500
FREQUENCY_PENALTY = 0
PRESENCE_PENALTY = 0.6
# limits how many questions we include in the prompt
MAX_CONTEXT_QUESTIONS = 50


# function to generate random user ID
def generate_user_id():
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    numbers = "0123456789"
    return "".join(random.choice(letters) for i in range(3)) + "".join(random.choice(numbers) for i in range(3))


# function to write conversation data to an Excel file
def write_conversation_to_excel(user_id, conversation):
    # create a new DataFrame
    df = pd.DataFrame(conversation, columns=["Role", "Message", "Timestamp"])

    # create the directory if it does not exist
    if not os.path.exists("C:/users/admin/Chatbot/convo"):
        os.makedirs("C:/users/admin/Chatbot/convo")

    # create a writer object
    writer = pd.ExcelWriter(f"C:/users/admin/Chatbot/convo/conversation_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", engine="xlsxwriter")

    # write the data to the Excel file
    df.to_excel(writer, sheet_name="Conversation")

    # save the Excel file
    writer.save()


def get_response(instructions, previous_questions_and_answers, new_question):
    """Get a response from ChatCompletion


    Args:
        instructions: The instructions for the chat bot - this determines how it will behave
        previous_questions_and_answers: Chat history
        new_question: The new question to ask the bot


    Returns:
        The response text
    """
    # build the messages
    messages = [
        { "role": "system", "content": instructions },
    ]
    # add the previous questions and answers
    for question, answer in previous_questions_and_answers[-MAX_CONTEXT_QUESTIONS:]:
        messages.append({ "role": "user", "content": question })
        messages.append({ "role": "assistant", "content": answer })
    # add the new question
    messages.append({ "role": "user", "content": new_question })


    completion = openai.Completion.create(
        engine="davinci",
        prompt=INSTRUCTIONS,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        frequency_penalty=FREQUENCY_PENALTY,
        presence_penalty=PRESENCE_PENALTY,
        stop=["\n", "Assistant:", "User:"]
    )
    return completion.choices[0].text.strip()


def get_moderation(question):
    """
    Check if the question is safe to ask the model

    Parameters:
        question (str): The question to check

    Returns:
        bool: True if the question is safe, False otherwise
    """
    # check for any bad words
    bad_words = ["hate", "kill", "suicide"]
    for word in bad_words:
        if word in question:
            return False

# create a Flask app
app = Flask(__name__)

# define a route for the homepage
@app.route("/")
def index():
    return render_template("index.html")


# define a route for the chat page
@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        # get the user's message
        message = request.form["message"]
        # get the user's ID from the form data or generate a new one
        user_id = request.form.get("user_id", generate_user_id())
        # get the chat history from the form data or create a new one
        conversation = request.form.get("conversation", [])
        if isinstance(conversation, str):
            conversation = eval(conversation)

        # check if the message is safe to ask
        if not get_moderation(message):
            response = "I'm sorry, I cannot answer that question."
            messages = [
                {"role": "user", "content": message},
                {"role": "assistant", "content": response}
            ]
        else:
            # get the assistant's response
            response = get_response(INSTRUCTIONS, conversation, message)

            # add the user's message and assistant's response to the conversation
            conversation.append(("User", message, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conversation.append(("Assistant", response, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            messages = []
            # add each message to the messages list
            for i in range(len(conversation)):
                role, content, timestamp = conversation[i]
                if role == "User":
                    messages.append({"role": "user", "content": content})
                else:
                    messages.append({"role": "assistant", "content": content})
            # write the conversation to an Excel file
            write_conversation_to_excel(user_id, conversation)

        # render the chat template with the messages and form data
        return render_template("index.html", messages=messages, user_id=user_id, conversation=conversation)

    # if the request method is GET, render the chat template with empty messages and form data
    else:
         return render_template("index.html", messages=[], user_id=generate_user_id(), conversation=[])


# run the app
if __name__ == "__main__":
    app.run(debug=True)


