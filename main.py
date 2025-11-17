import streamlit as st
import telebot
import multiprocessing
import time
from transformers import pipeline

# ---------------------------------
# Streamlit UI
# ---------------------------------
st.title("UAserver AI Telegram Bot (Python AI) v9.7.0")

st.markdown("""
Enter your **Telegram Bot Token** and **Chat ID** below.
The bot will automatically reply using Python AI (DialoGPT).
""")

token = st.text_input("Enter Your Telegram Bot Token:", type="password")
chat_id = st.text_input("Enter Telegram Chat ID:", value="")

# ---------------------------------
# Multiprocessing manager & queues
# ---------------------------------
if "manager" not in st.session_state:
    st.session_state.manager = multiprocessing.Manager()
    st.session_state.bot_process = None

# ---------------------------------
# Function to start bot
# ---------------------------------
def start_bot(token, chat_id):
    # Load DialoGPT AI
    pipe = pipeline(
        "text-generation",
        model="microsoft/DialoGPT-medium",
        max_new_tokens=150,
        temperature=0.7,
        top_p=0.9
    )

    bot = telebot.TeleBot(token)

    # Startup message
    try:
        bot.send_message(chat_id, "Connected with UAserver Intelligence API 9.7.0")
    except:
        pass

    # AI reply function
    def ask_local_ai(msg):
        try:
            out = pipe(msg)
            reply = out[0]["generated_text"]
            return reply.strip()[:4000]
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
# Start/Stop buttons
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
