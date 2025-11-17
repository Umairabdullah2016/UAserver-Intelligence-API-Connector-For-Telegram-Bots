# main.py

# -----------------------------
# IMPORTS
# -----------------------------
import telebot
import time
import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.title("UAserver AI API")
st.write("🚀 Starting UAserver AI 7B...")

# Initialize a message queue in session_state
if "message_queue" not in st.session_state:
    st.session_state.message_queue = []

# -----------------------------
# LOAD AI MODEL (Mistral-7B)
# -----------------------------
model_name = "mistralai/Mistral-7B-Instruct-v0"

st.write("Loading Mistral-7B model. This may take a while...")
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", torch_dtype=torch.float16)
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=150, temperature=0.7)

st.success("Mistral-7B Loaded ✅")

# -----------------------------
# TELEGRAM BOT SETUP
# -----------------------------
# Leave empty for user input
TOKEN = st.text_input("Enter your Telegram Bot Token", type="password")

bot = None
if TOKEN:
    bot = telebot.TeleBot(TOKEN)
    st.success("Connected with UAserver Intelligence API 9.7.0 ✅")

# -----------------------------
# AI HELPER FUNCTION
# -----------------------------
def ask_local_ai(msg):
    try:
        messages = [{"role": "user", "content": msg}]
        out = pipe(messages)
        if isinstance(out, list) and len(out) > 0:
            if isinstance(out[0], dict) and "generated_text" in out[0]:
                reply = out[0]["generated_text"]
            else:
                reply = str(out[0])
        else:
            reply = str(out)
        return reply.strip()[:4000]
    except Exception as e:
        print("Error in ask_local_ai:", e)
        return "Sorry, I could not generate a reply."

# -----------------------------
# BOT HANDLERS
# -----------------------------
if bot:

    @bot.message_handler(commands=["start"])
    def start_cmd(message):
        bot.send_message(message.chat.id, "Hey ✌️ I am UAserver AI 9.7.0!")

    @bot.message_handler(commands=["stop"])
    def stop_cmd(message):
        bot.send_message(message.chat.id, "Stopped.")
        raise SystemExit

    @bot.message_handler(content_types=["text"])
    def handle(message):
        chat = message.chat.id
        text = message.text

        # Add to Streamlit message queue
        st.session_state.message_queue.append({"text": text, "chat": chat, "msg_id": time.time()})

        bot.send_chat_action(chat, "typing")
        reply = ask_local_ai(text)
        bot.send_message(chat, f"🔹UAserver AI: {reply}")

    # -----------------------------
    # START BOT
    # -----------------------------
    import threading

    def start_bot():
        bot.polling(none_stop=True)

    threading.Thread(target=start_bot, daemon=True).start()
