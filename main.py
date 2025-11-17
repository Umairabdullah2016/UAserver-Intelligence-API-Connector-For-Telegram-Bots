import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import telebot
import multiprocessing
import time

# -------------------------------
# Streamlit UI
st.title("Telegram Bot with MPT-7B Instruct")
st.write("Loading MPT-7B model. This may take a while...")

# Use public model
model_name = "mosaicml/mpt-7b-instruct"

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")

# Create a text-generation pipeline
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_length=512)

st.write("Model loaded!")

# -------------------------------
# Telegram Bot
API_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
bot = telebot.TeleBot(API_TOKEN)

def handle_message(message):
    user_text = message.text
    response = pipe(user_text)[0]['generated_text']
    bot.send_message(message.chat.id, response)

@bot.message_handler(func=lambda msg: True)
def message_handler(msg):
    handle_message(msg)

def start_bot():
    bot.polling()

# -------------------------------
# Run Telegram bot in a separate process
if __name__ == "__main__":
    process = multiprocessing.Process(target=start_bot)
    process.start()
    st.write("Telegram bot is running...")
