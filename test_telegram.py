import requests
import os

def send_telegram_message(bot_token, chat_id, message):
    """Send a message to Telegram via bot API"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"  # Allows HTML formatting like <b>bold</b>
    }
    
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        print("✅ Message sent successfully!")
    else:
        print(f"❌ Failed to send message. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return response

def main():
    # Get credentials from environment variables
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN environment variable not found!")
        return
    
    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID environment variable not found!")
        return
    
    # Test message with HTML formatting
    test_message = """
🎓 <b>College News Bot is working!</b>

📢 This is a test message from your automated news scraper.

✅ Bot Status: <i>Active</i>
🕐 Check Frequency: Every 6 hours
    """
    
    print("Sending test message to Telegram...")
    send_telegram_message(bot_token, chat_id, test_message)

if __name__ == "__main__":
    main()