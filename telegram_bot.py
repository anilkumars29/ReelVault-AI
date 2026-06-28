import os
import telebot
import chromadb
import ollama
import threading
import logging
from dotenv import load_dotenv
from pipeline import process_pipeline

# --- 🔐 CONFIGURATION & SECURE LOADING ---
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHROMA_PATH = "./chroma_db"
LLM_MODEL = "llama3.2"  # Fast, lightweight CPU model optimized for edge execution

# Configure system-wide logging parameters
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("reelvault.log"),
        logging.StreamHandler()
    ]
)

if not BOT_TOKEN:
    logging.error("CRITICAL: TELEGRAM_BOT_TOKEN missing from local .env file.")
    exit(1)

# Initialize system clients
bot = telebot.TeleBot(BOT_TOKEN)
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)


# --- 🩺 BOOT-TIME HEALTH CHECKS ---
def verify_local_ai():
    logging.info("Checking local AI engine status...")
    try:
        models_list = ollama.list()
        
        # Version-agnostic check to see if the required model is downloaded
        if LLM_MODEL not in str(models_list):
            logging.warning(f"'{LLM_MODEL}' not found locally. Running automatic pull...")
            ollama.pull(LLM_MODEL)
            
        logging.info(f"Local AI Engine verified. '{LLM_MODEL}' is ready.")
    except Exception as e:
        logging.error(f"CRITICAL: Could not connect to Ollama server: {str(e)}")
        print("Please ensure the Ollama desktop application is actively running!")
        exit(1)

# Run health check before entering polling loop
verify_local_ai()
logging.info("ReelVault Brain Active (Secure Mode)! Listening on Telegram...")


# --- 📬 MESSAGE INTERCEPTOR & ROUTER ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_text = message.text.strip()
    
    # 🗑️ ACTION 1: Natural Language Record Deletion (Intent-Driven)
    if any(keyword in user_text.lower() for keyword in ["delete", "remove", "erase", "purge"]) and ("instagram.com/" in user_text):
        logging.info("Deletion Intent Detected via Natural Language")
        try:
            # Dynamically extract the URL from anywhere inside your sentence
            words = user_text.split()
            target_url = None
            for word in words:
                if "instagram.com/" in word:
                    target_url = word.strip()
                    break
            
            if not target_url:
                bot.reply_to(message, "⚠️ I see you want to delete something, but I couldn't find a valid Instagram link in your message.")
                return
                
            collection = chroma_client.get_or_create_collection(name="reels_archive")
            existing = collection.get(where={"url": target_url})
            
            if not existing or not existing['ids']:
                bot.reply_to(message, "🤷‍♂️ Checked my system, but that specific link isn't saved in your ReelVault archive anyway.")
                return

            # Purge the coordinates from the local vector database
            collection.delete(where={"url": target_url})
            logging.info(f"Successfully purged vector indices for: {target_url}")
            bot.reply_to(message, "🗑️ Got it! I have completely erased that reel from your local memory.")
            
        except Exception as e:
            logging.error(f"Deletion routine failure: {str(e)}")
            bot.reply_to(message, "❌ Something went wrong trying to clear that file from my database.")
        return

    # 📥 ACTION 2: Asynchronous Multimedia Ingestion (With Duplicate Check)
    elif "instagram.com/reel/" in user_text or "instagram.com/p/" in user_text:
        url = user_text.split()[0]
        logging.info(f"Link received for ingestion: {url}")
        
        # Pre-check ChromaDB to filter duplicate records before downloading
        try:
            collection = chroma_client.get_or_create_collection(name="reels_archive")
            existing = collection.get(where={"url": url})
            
            if existing and existing['ids']:
                bot.reply_to(message, "🧠 Hey! This Reel is already indexed in your ReelVault archive. Skipping processing.")
                logging.info(f"Skipped duplicate link: {url}")
                return  
                
        except Exception as db_err:
            logging.warning(f"Pre-check warning: {str(db_err)}")

        bot.reply_to(message, "🎬 New Reel detected! Spawning background execution thread... ⏳")
        
        def worker():
            try:
                process_pipeline(url)
                bot.reply_to(message, "🎉 Success! This Reel is fully indexed into Notion and ChromaDB.")
                logging.info(f"Successfully indexed: {url}")
            except Exception as e:
                logging.error(f"Worker thread execution failed: {str(e)}")
                bot.reply_to(message, "❌ Wrong link shared! Please ensure you are sending a valid Instagram Reel containing video content.")
        
        bg_thread = threading.Thread(target=worker)
        bg_thread.start()

    # 🔍 ACTION 3: Local Semantic Knowledge Retrieval & Live Dashboards
    else:
        logging.info(f"Neural Query received: '{user_text}'")
        bot.send_chat_action(message.chat.id, 'typing')
        
        try:
            collection = chroma_client.get_collection(name="reels_archive")
            total_items = collection.count()
            
            if total_items == 0:
                bot.reply_to(message, "📭 Your ReelVault archive is currently empty. Send some reels first!")
                return

            # 📊 SUB-ROUTING A: High-Level Dashboard Summary
            if "dashboard" in user_text.lower() or "list" in user_text.lower() or "summarize all" in user_text.lower():
                logging.info("Intent Detected: Macro Dashboard View Generation")
                bot.reply_to(message, "📊 Processing data matrix... Compiling your high-level dashboard view... ⏳")
                
                # Context Window Guard: Limit dashboard compilation up to 5 elements max
                num_results = min(5, total_items)
                
                if "all" in user_text.lower() or "till now" in user_text.lower():
                    search_results = collection.get(limit=num_results)
                    docs_list = search_results.get('documents', [])
                    meta_list = search_results.get('metadatas', [])
                else:
                    topic_query = user_text.lower().replace("dashboard", "").replace("of", "").replace("list", "").strip()
                    search_results = collection.query(query_texts=[topic_query], n_results=num_results)
                    docs_list = search_results.get('documents', [[]])[0]
                    meta_list = search_results.get('metadatas', [[]])[0]

                dashboard_prompt = f"""
                You are an elite executive strategy assistant. Generate a high-level, ultra-scannable dashboard report of the compiled videos provided.
                For each video item listed, output a clean 1-sentence bullet point explaining exactly what strategic concept or topic it covers.
                
                Rules:
                - Use bold headers for each video title.
                - Keep descriptions strictly to a single, concise sentence.
                - Prioritize maximum readability and space efficiency.
                
                Compiled Video Data:
                """
                for i in range(len(docs_list)):
                    dashboard_prompt += f"\n👉 Title: {meta_list[i].get('title', 'Untitled')}\nContent Context: {docs_list[i]}\n"

                response = ollama.chat(model=LLM_MODEL, messages=[{'role': 'user', 'content': dashboard_prompt}])
                dashboard_summary = response['message']['content'].strip()
                
                links_footer = "\n\n🔗 **Quick Access Directory:**\n"
                for i in range(len(meta_list)):
                    links_footer += f"• [{meta_list[i].get('title', 'Link')}]({meta_list[i].get('url', '#')})\n"
                
                final_reply = f"📊 **ReelVault Intelligence Dashboard**\n\n{dashboard_summary}{links_footer}"
                bot.reply_to(message, final_reply, parse_mode="Markdown", disable_web_page_preview=True)
                logging.info("Strategic multi-item dashboard dispatched successfully.")
            
            # 🎯 SUB-ROUTING B: Standard Point-to-Point Q&A Routine
            else:
                search_results = collection.query(query_texts=[user_text], n_results=1)
                
                if search_results and search_results['documents'] and len(search_results['documents'][0]) > 0:
                    matched_transcript = search_results['documents'][0][0]
                    matched_meta = search_results['metadatas'][0][0]
                    
                    # Distance Shield Guard against out-of-bounds queries
                    if 'distances' in search_results and search_results['distances'][0][0] > 1.3:
                        bot.reply_to(message, "🤷‍♂️ I found a few entries in your Vault, but none of them are mathematically close enough to genuinely answer that question without guessing.")
                        logging.info(f"Desperate Match Shield triggered. Score: {search_results['distances'][0][0]}")
                        return

                    qa_prompt = f"""
                    You are a precise personal knowledge assistant. Answer the user's question strictly using the provided Video Context.
                    If the context doesn't contain the information required to answer, reply with: "I found a relevant reel, but it doesn't explicitly answer that."
                    
                    Video Context:
                    {matched_transcript}
                    
                    User Question: {user_text}
                    """
                    
                    response = ollama.chat(model=LLM_MODEL, messages=[{'role': 'user', 'content': qa_prompt}])
                    answer = response['message']['content'].strip()
                    
                    source_title = matched_meta.get('title', 'Untitled Reel')
                    source_url = matched_meta.get('url', '#')
                    final_reply = f"💡 *Answer:*\n{answer}\n\n📚 *Source:* [{source_title}]({source_url})"
                    
                    bot.reply_to(message, final_reply, parse_mode="Markdown", disable_web_page_preview=True)
                    logging.info("Context retrieved and precise answer dispatched.")
                else:
                    bot.reply_to(message, "🤷‍♂️ I couldn't find any reels in your local archive that match that topic.")
                
        except Exception as e:
            bot.reply_to(message, "📭 Your ReelVault archive appears to be empty or initializing. Index a link first!")
            logging.error(f"Database query exception managed: {str(e)}")


# --- 🚀 ENGINE START ---
# --- 🚀 ENGINE START WITH NETWORK RESILIENCE SHIELDS ---
if __name__ == "__main__":
    import time
    
    logging.info("ReelVault Engine Active! Entering polling loop...")
    
    while True:
        try:
            # timeout: Socket read timeout (forces a refresh before things hang)
            # long_polling_timeout: Server-side long poll wait threshold
            bot.infinity_polling(timeout=30, long_polling_timeout=15)
            
        except Exception as polling_err:
            logging.error(f"Network polling socket interrupted: {str(polling_err)}")
            logging.info("Resource starvation or timeout detected. Cooling down for 5 seconds before self-healing reconnect...")
            time.sleep(5)
            logging.info("Re-establishing active long-polling channel to Telegram Cloud...")