import streamlit as st
import telebot
import multiprocessing
import time
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# ---------------------------------
# Streamlit UI
# ---------------------------------
st.title("UAserver AI Telegram Bot (Mistral‑12B) v9.7.0")

st.markdown("""
Enter your **Telegram Bot Token** and **Chat ID** below.
The bot will automatically reply using Mistral‑12B Python AI.
""")

token = st.text_input("Enter Your Telegram Bot Token:", type="password")
chat_id = st.text_input("Enter Telegram Chat ID:", value="")

# ---------------------------------
# Multiprocessing manager & state
# ---------------------------------
if "manager" not in st.session_state:
    st.session_state.manager = multiprocessing.Manager()
    st.session_state.bot_process = None

# ---------------------------------
# Function to start the bot
# ---------------------------------
def start_bot(token, chat_id):
    # Load Mistral‑12B
    model_name = "mistralai/Mistral-12B-Instruct-v0"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        torch_dtype=torch.float16,
        load_in_8bit=True  # memory efficient
    )

    bot = telebot.TeleBot(token)

    # Startup message
    try:
        bot.send_message(chat_id, "Connected with UAserver Intelligence API 9.7.0")
    except:
        pass

    # AI reply function
    def ask_local_ai(prompt):
        try:
            inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
            output = model.generate(**inputs, max_new_tokens=150)
            reply = tokenizer.decode(output[0], skip_special_tokens=True)
            return reply
        except Exception as e:
            print("Error generating AI reply:", e)
            return "Sorry, I could not generate a reply."

    # Telegram handlers
    @bot.message_handler(commands=["start"])
    def start_cmd(message):
        bot.send_message(message.chat.id, "Hey ✌️ I am UAserver AI!")

    @bot.message_handler(commands=["stop"])
    def stop_cmd(message):
        bot.send_message(message.chat.id, "Bot stopped.")
        raise SystemExit

    @bot.message_handler(content_types=["text"])
    def handle(message):
        bot.send_chat_action(message.chat.id, "typing")
        reply = ask_local_ai(message.text)
        bot.send_message(message.chat.id, f"🔹UAserver AI: {reply}")

    bot.polling(none_stop=True)

# ---------------------------------
# Streamlit Start/Stop buttons
# ---------------------------------
if st.button("Start UAserver AI Bot"):
    if not token or not chat_id:
        st.error("Enter both Bot Token and Chat ID.")
    else:
        if st.session_state.bot_process is None:
            process = multiprocessing.Process(target=start_bot, args=(token, chat_id))
            process.start()
            st.session_state.bot_process = process
            st.success("✅ Bot started!")
        else:
            st.info("Bot is already running.")

if st.button("Stop UAserver AI Bot"):
    if st.session_state.bot_process:
        st.session_state.bot_process.terminate()
        st.session_state.bot_process = None
        st.success("🛑 Bot stopped.")
    else:
        st.warning("Bot is not running.")
