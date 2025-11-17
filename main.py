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
Telegram messages will be passed to **Putter.js AI** in HTML and the AI reply will be sent back to Telegram automatically.
""")

token = st.text_input("Enter Your Telegram Bot Token:", type="password")
chat_id = st.text_input("Enter Telegram Chat ID:", value="")

# ---------------------------------
# Create multiprocessing manager and queues
# ---------------------------------
if "manager" not in st.session_state:
    st.session_state.manager = multiprocessing.Manager()
    st.session_state.message_queue = st.session_state.manager.list()
    st.session_state.reply_queue = st.session_state.manager.list()
    st.session_state.bot_process = None

message_queue = st.session_state.message_queue
reply_queue = st.session_state.reply_queue

# ---------------------------------
# JS AI HTML component
# ---------------------------------
def render_js_ai(latest_message):
    msg_json = json.dumps(latest_message)
    html_code = f"""
    <div id="js-ai"></div>
    <script src="https://cdn.jsdelivr.net/npm/puter.js"></script>
    <script>
    let msg = {msg_json};
    if(msg.text){{
        Putter.generate(msg.text).then(preply => {{
            window.parent.postMessage(JSON.stringify({{preply: preply, msg_id: msg.msg_id}}), "*");
        }});
    }}
    </script>
    """
    st.components.v1.html(html_code, height=200)

# Show latest Telegram message in JS AI
latest_message = message_queue[-1] if len(message_queue) > 0 else {"text":"", "msg_id":0}
render_js_ai(latest_message)

# ---------------------------------
# Function to run Telegram bot
# ---------------------------------
def start_bot(token, chat_id, message_queue, reply_queue):
    bot = telebot.TeleBot(token)

    # Send startup message
    try:
        bot.send_message(chat_id, "Connected with UAserver Intelligence API 9.7.0")
    except:
        pass

    # Handle text messages
    @bot.message_handler(content_types=["text"])
    def handle(message):
        msg_id = time.time()
        message_queue.append({"text": message.text, "chat": message.chat.id, "msg_id": msg_id})

        # Wait for JS reply (polling)
        start_time = time.time()
        reply = "Sorry, no reply from AI."
        while time.time() - start_time < 15:  # 15 sec timeout
            for r in reply_queue:
                if r["msg_id"] == msg_id:
                    reply = r["preply"]
                    reply_queue.remove(r)
                    break
            if reply != "Sorry, no reply from AI.":
                break
            time.sleep(0.5)

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
            process = multiprocessing.Process(
                target=start_bot, args=(token, chat_id, message_queue, reply_queue)
            )
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

# ---------------------------------
# JS → Python listener
# ---------------------------------
# Streamlit automatically receives messages via `window.postMessage`
# We need to poll the browser messages in Streamlit. This is handled by a small JS snippet:
st.markdown("""
<script>
window.addEventListener("message", function(event) {
    let data = event.data;
    try{
        let obj = JSON.parse(data);
        if(obj.preply && obj.msg_id){
            // Append to Streamlit reply queue
            fetch(`/__reply__?data=${encodeURIComponent(JSON.stringify(obj))}`);
        }
    }catch(e){
        console.log("Error parsing message:", e);
    }
});
</script>
""", unsafe_allow_html=True)
