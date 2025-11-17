import streamlit as st
import telebot
import multiprocessing
import json
import time

# ---------------------------------
# Streamlit UI
# ---------------------------------
st.title("UAserver AI with Putter.js (v9.7.0)")

st.markdown("""
Enter your **Telegram Bot Token** and **Chat ID** below.
Messages will go through **Putter.js AI** in HTML and the reply will be sent back to Telegram.
""")

token = st.text_input("Enter Your Telegram Bot Token:", type="password")
chat_id = st.text_input("Enter Telegram Chat ID:", value="")

# Store a message queue for Python-JS communication
if "message_queue" not in st.session_state:
    st.session_state.message_queue = []

if "reply_queue" not in st.session_state:
    st.session_state.reply_queue = []

# ---------------------------------
# JS AI HTML component
# ---------------------------------
html_code = """
<div id="js-ai"></div>
<script src="https://cdn.jsdelivr.net/npm/puter.js"></script>
<script>
window.addEventListener("message", async function(event) {
    let data = event.data;
    try {
        let obj = JSON.parse(data);
        if(obj.user_msg){
            // Call Putter.js AI
            let preply = await Putter.generate(obj.user_msg);
            // Send back to Python via postMessage
            window.parent.postMessage(JSON.stringify({preply: preply, msg_id: obj.msg_id}), "*");
        }
    } catch(e){
        console.log("Error:", e);
    }
});
</script>
"""

st.components.v1.html(html_code, height=200)

# ---------------------------------
# Function to run Telegram bot
# ---------------------------------
def start_bot(token, chat_id):
    bot = telebot.TeleBot(token)

    # Send startup message
    try:
        bot.send_message(chat_id, "Connected with UAserver Intelligence API 9.7.0")
    except:
        pass

    # Handle text messages
    @bot.message_handler(content_types=["text"])
    def handle(message):
        # Put message in Streamlit session queue
        st.session_state.message_queue.append({"text": message.text, "chat": message.chat.id, "msg_id": time.time()})

        # Wait for JS reply (polling)
        start_time = time.time()
        reply = "..."  # fallback if no reply
        while time.time() - start_time < 10:  # 10 sec timeout
            for r in st.session_state.reply_queue:
                if r["msg_id"] == st.session_state.message_queue[-1]["msg_id"]:
                    reply = r["preply"]
                    st.session_state.reply_queue.remove(r)
                    break
            if reply != "...":
                break
            time.sleep(0.5)

        bot.send_message(message.chat.id, f"🔹UAserver AI: {reply}")

    bot.polling(none_stop=True)

# ---------------------------------
# Start/Stop buttons
# ---------------------------------
if "bot_process" not in st.session_state:
    st.session_state.bot_process = None

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
            st.info("Bot already running.")

if st.button("Stop Bot"):
    if st.session_state.bot_process:
        st.session_state.bot_process.terminate()
        st.session_state.bot_process = None
        st.success("🛑 Bot stopped.")
    else:
        st.warning("Bot is not running.")
