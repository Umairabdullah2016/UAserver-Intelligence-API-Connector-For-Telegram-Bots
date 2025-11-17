import streamlit as st
import telebot
import threading
from transformers import pipeline

# ---------------------------------
# LOAD LOCAL AI MODEL
# ---------------------------------
pipe = pipeline(
    "text-generation",
    model="microsoft/DialoGPT-medium",
    max_new_tokens=150,
    temperature=0.7,
    top_p=0.9
)

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

# Session states
if "bot_thread" not in st.session_state:
    st.session_state.bot_thread = None

if "bot_instance" not in st.session_state:
    st.session_state.bot_instance = None


# ---------------------------------
# LOCAL AI MODEL FUNCTION
# ---------------------------------
def ask_local_ai(msg):
    try:
        messages = [{"role": "user", "content": msg}]
        out = pipe(messages)

        # Robustly extract string from pipeline output
        if isinstance(out, list):
            # Flatten nested lists if necessary
            while len(out) == 1 and isinstance(out[0], list):
                out = out[0]

            if len(out) > 0:
                if isinstance(out[0], dict) and "generated_text" in out[0]:
                    reply = out[0]["generated_text"]
                else:
                    reply = str(out[0])
            else:
                reply = ""
        else:
            reply = str(out)

        # Limit to Telegram max message length
        return reply.strip()[:4000]

    except Exception as e:
        print("Error in ask_local_ai:", e)
        return "Sorry, I could not generate a reply."

# ---------------------------------
# BOT STARTUP FUNCTION
# ---------------------------------
def start_bot(token, chat_id):
    bot = telebot.TeleBot(token)

    # Send connection message immediately
    try:
        bot.send_message(chat_id, "Connected with UAserver Intelligence API 9.7.0")
    except:
        pass  # prevents crash if chat ID invalid

    # Commands
    @bot.message_handler(commands=["start"])
    def start_cmd(message):
        bot.send_message(message.chat.id, "Hey ✌️ I am UAserver AI!")

    @bot.message_handler(commands=["stop"])
    def stop_cmd(message):
        bot.send_message(message.chat.id, "Stopped.")
        raise SystemExit

    # Main message handler
    @bot.message_handler(content_types=["text"])
    def handle(message):
        chat = message.chat.id
        text = message.text

        bot.send_chat_action(chat, "typing")
        ai_reply = ask_local_ai(text)

        bot.send_message(chat, f"🔹UAserver AI: {ai_reply}")

    st.session_state.bot_instance = bot
    bot.polling(none_stop=True)


# ---------------------------------
# START BUTTON
# ---------------------------------
if st.button("Start UAserver AI Bot"):
    if not token:
        st.error("❌ Enter your bot token.")
    elif not chat_id:
        st.error("❌ Enter a chat ID.")
    else:
        if st.session_state.bot_thread is None:
            st.session_state.bot_thread = threading.Thread(
                target=start_bot, args=(token, chat_id)
            )
            st.session_state.bot_thread.start()
            st.success("✅ UAserver AI Bot Started!")
            st.info("Telegram startup message sent.")
        else:
            st.info("Bot is already running.")


# ---------------------------------
# STOP BUTTON
# ---------------------------------
if st.button("Stop Bot"):
    if st.session_state.bot_instance:
        try:
            st.session_state.bot_instance.stop_polling()
            st.session_state.bot_thread = None
            st.success("🛑 Bot stopped successfully.")
        except:
            st.error("Error stopping bot.")
    else:
        st.warning("Bot is not running.")
