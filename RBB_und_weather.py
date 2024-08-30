from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import feedparser
from deep_translator import GoogleTranslator
import logging
import asyncio
from datetime import datetime, time, timedelta
import requests

# Replace with your bot token and channel ID
TOKEN = 'XXXX'

CHANNEL_ID = '-100XXX'
SUBGROUP_THREAD_ID = 'XXX'

# RSS feed URL
RSS_URL = "https://www.rbb24.de/panorama/index.xml/feed=rss.xml"

# Initialize the translator
translator = GoogleTranslator()

# Set up logging to track issues
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Application
application = Application.builder().token(TOKEN).build()

# To keep track of the latest news
latest_titles = set()

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('RBB24 designed for ISP, with translation, and weather forecasting')

async def fetch_initial_news():
    logging.info("Fetching initial news...")
    try:
        feed = feedparser.parse(RSS_URL)
    except Exception as e:
        logging.error(f"Failed to parse RSS feed: {e}")
        return None

    global latest_titles
    initial_entries = []
    count = 0

    for entry in feed.entries:
        if count >= 10:
            break
        if entry.title not in latest_titles:
            latest_titles.add(entry.title)
            initial_entries.append(entry)
            count += 1

    if not initial_entries:
        logging.info("No initial news items found.")
    else:
        logging.info(f"Found {len(initial_entries)} initial news items.")

    return initial_entries

async def check_and_post_news(context: CallbackContext):
    logging.info("Fetching news...")
    try:
        feed = feedparser.parse(RSS_URL)
    except Exception as e:
        logging.error(f"Failed to parse RSS feed: {e}")
        return

    global latest_titles
    new_entries = []

    for entry in feed.entries:
        if entry.title not in latest_titles:
            latest_titles.add(entry.title)
            new_entries.append(entry)
        if len(new_entries) >= 10:
            break

    if not new_entries:
        logging.info("No new news items.")
    else:
        logging.info(f"Found {len(new_entries)} new news items.")

    if new_entries:
        # Concatenate all entries into a single message
        weather_report = get_tomorrow_weather_report()
        full_message = weather_report + "\n\n" + "\n\n".join([format_message(entry) for entry in new_entries])
        try:
            # Send the concatenated message as a single message
            sent_message = await context.bot.send_message(chat_id=CHANNEL_ID, message_thread_id=SUBGROUP_THREAD_ID, text=full_message, parse_mode='Markdown')
            logging.info("Message sent successfully.")
            
            # Schedule the message to be deleted after 48 hours
            await schedule_message_deletion(context, sent_message.chat_id, sent_message.message_id, 48 * 3600)  # 48 hours in seconds

        except Exception as e:
            logger.error(f"Failed to send message: {e}")

def format_message(entry):
    title = entry.title
    description = entry.description or "No description available."
    link = entry.link

    try:
        # Translate the title and description to English
        translated_title = translator.translate(title, target='en')
        translated_description = translator.translate(description, target='en')
    except Exception as e:
        logging.error(f"Translation error: {e}")
        translated_title = "Translation failed"
        translated_description = "Translation failed"

    # Use a separator
    separator = "                   ✦✦✦➤➤➤✦✦✦"
    
    return (
        f"**German**:\n"
        f"*{title}*\n\n"
        f"**English**:\n"
        f"*{translated_title}*\n"
        f"Link: [Read more]({link})\n"
        f"{separator}"
    )

async def schedule_message_deletion(context: CallbackContext, chat_id: int, message_id: int, delay_seconds: int):
    # Wait for the specified amount of time before deleting the message
    await asyncio.sleep(delay_seconds)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        logging.info(f"Message {message_id} deleted successfully after {delay_seconds / 3600} hours.")
    except Exception as e:
        logger.error(f"Failed to delete message {message_id}: {e}")

async def fetch_news(update: Update, context: CallbackContext):
    logging.info("Fetch news command received.")
    await check_and_post_news(context)
    await update.message.reply_text("Manually triggered news fetch.")

def get_weather_info(city_name, latitude, longitude):
    # Calculate tomorrow's date
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    tomorrow_date = tomorrow.strftime('%Y-%m-%d')

    # Open-Meteo API call for the specific location
    url = (f"https://api.open-meteo.com/v1/forecast?"
           f"latitude={latitude}&longitude={longitude}"
           f"&hourly=temperature_2m&timezone=Europe/Berlin")

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Extract tomorrow's hourly temperatures
        hourly_times = data['hourly']['time']
        hourly_temps = data['hourly']['temperature_2m']

        # Find min and max temperature and their corresponding times
        min_temp, max_temp = float('inf'), float('-inf')
        min_time, max_time = None, None

        for i, time in enumerate(hourly_times):
            if time.startswith(tomorrow_date):
                temp = hourly_temps[i]
                if temp < min_temp:
                    min_temp = temp
                    min_time = datetime.fromisoformat(time).strftime('%I:%M %p')
                if temp > max_temp:
                    max_temp = temp
                    max_time = datetime.fromisoformat(time).strftime('%I:%M %p')

        return f"\nWeather in {city_name} tomorrow:\n Min {min_temp}°C at {min_time}, Max {max_temp}°C at {max_time}"
    except Exception as e:
        logging.error(f"Failed to fetch weather data for {city_name}: {e}")
        return f"Weather data not available for {city_name}"

def get_tomorrow_weather_report():
    today_day = datetime.now().strftime("%A")  # Get today's day name (e.g., Friday)
    
    # Get weather for Potsdam
    potsdam_weather = get_weather_info("Potsdam", 52.3989, 13.0657)  # Potsdam coordinates
    
    # Get weather for Berlin
    berlin_weather = get_weather_info("Berlin", 52.52, 13.4050)  # Berlin coordinates
    
    return (f"Today is {today_day}\n"
            f"{potsdam_weather},\n"
            f"{berlin_weather},\n")

def main():
    # Explicitly create a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Add the /start command handler
    application.add_handler(CommandHandler("start", start))

    # Add the /fetch_news command handler
    application.add_handler(CommandHandler("fetch_news", fetch_news))

    # Add the /weather command handler
    application.add_handler(CommandHandler("weather", lambda update, context: update.message.reply_text(get_tomorrow_weather_report())))

    # Schedule the job to post news every day at 20:00
    job_queue = application.job_queue
    job_queue.run_daily(check_and_post_news, time=time(hour=20, minute=11))
    logging.info("Daily news posting job scheduled at 20:00.")

    # Fetch the initial 10 news items
    async def startup_tasks():
        initial_news = await fetch_initial_news()
        if initial_news:
            weather_report = get_tomorrow_weather_report()
            full_message = weather_report + "\n\n" + "\n\n".join([format_message(entry) for entry in initial_news])
            try:
                # Send the initial batch of messages as a single message
                sent_message = await application.bot.send_message(chat_id=CHANNEL_ID, message_thread_id=SUBGROUP_THREAD_ID, text=full_message, parse_mode='Markdown')
                logging.info("Initial news message sent successfully.")
                
                # Schedule the initial message to be deleted after 48 hours
                await schedule_message_deletion(application, sent_message.chat_id, sent_message.message_id, 23 * 3600)  # 23 hours in seconds
            except Exception as e:
                logger.error(f"Failed to send initial news message: {e}")

    # Run the startup tasks
    loop.run_until_complete(startup_tasks())

    # Start the bot without the loop argument
    application.run_polling()

if __name__ == '__main__':
    main()
