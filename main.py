import streamlit as st
import telebot
import multiprocessing
from transformers import pipeline
import torch
import sentencepiece  # required by some models

# ---------------------------------
# STREAMLIT UI
# ---------------------------------
st.title("UAserver AI — Telegram Bot Host (v9.7.0)")

st.markdown("""
Enter your **Telegram Bot Token** and **Chat ID** below.

As soon as the bot connects, it will automatically send:

**“Connected with UAserver Intelligence API 9.7.0”**
""")

token = st.text_input("Enter Your Telegram Bot Token:", type="password")
chat_id = st.text_input("Enter Telegram Chat ID to Send Startup Message:")

# ---------------------------------
# BOT PROCESS FUNCTION
# ---------------------------------
def start_bot_process(token, chat_id):
    # Load AI model inside process (safe)
    pipe = pipeline(
        "text-generation",
        model="microsoft/DialoGPT-medium",
        max_new_tokens=150,
        temperature=0.7,
        top_p=0.9
    )

    bot = telebot.TeleBot(token)

    # Send connection message immediately
    try:
        bot.send_message(chat_id, "Connected with UAserver Intelligence API 9.7.0")
    except:
        pass

    # AI function
    def ask_local_ai(msg):
        try:
            messages = [{"role": "user", "content": msg}]
            out = pipe(messages)

            # Flatten nested lists if needed
            while len(out) == 1 and isinstance(out[0], list):
                out = out[0]

            if len(out) > 0:
                if isinstance(out[0], dict) and "generated_text" in out[0]:
                    reply = out[0]["generated_text"]
                else:
                    reply = str(out[0])
            else:
                reply = ""
            return reply.strip()[:4000]

        except Exception as e:
            print("Error in ask_local_ai:", e)
            return "Sorry, I could not generate a reply."

    # Commands
    @bot.message_handler(commands=["start"])
    def start_cmd(message):
        bot.send_message(message.chat.id, "Hey ✌️ I am UAserver AI!")

    @bot.message_handler(commands=["stop"])
    def stop_cmd(message):
        bot.send_message(message.chat.id, "Stopped.")
        raise SystemExit

    # Message handler
    @bot.message_handler(content_types=["text"])
    def handle(message):
        chat = message.chat.id
        text = message.text
        bot.send_chat_action(chat, "typing")
        ai_reply = ask_local_ai(text)
        bot.send_message(chat, f"🔹UAserver AI: {ai_reply}")

    bot.polling(none_stop=True)


# ---------------------------------
# START / STOP BUTTONS
# ---------------------------------
if "bot_process" not in st.session_state:
    st.session_state.bot_process = None

# Start bot
if st.button("Start UAserver AI Bot"):
    if not token or not chat_id:
        st.error("❌ Enter both Bot Token and Chat ID.")
    else:
        if st.session_state.bot_process is None:
            process = multiprocessing.Process(target=start_bot_process, args=(token, chat_id))
            process.start()
            st.session_state.bot_process = process
            st.success("✅ Bot started!")
        else:
            st.info("Bot is already running.")

# Stop bot
if st.button("Stop Bot"):
    if st.session_state.bot_process:
        st.session_state.bot_process.terminate()
        st.session_state.bot_process = None
        st.success("🛑 Bot stopped.")
    else:
        st.warning("Bot is not running.")
