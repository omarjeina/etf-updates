import requests
import os

def send_discord_message(webhook_url, message):
    """Send a simple text message to Discord via webhook"""
    data = {
        "content": message
    }
    
    response = requests.post(webhook_url, json=data)
    
    if response.status_code == 204:
        print("✅ Message sent successfully!")
    else:
        print(f"❌ Failed to send message. Status code: {response.status_code}")
        print(f"Response: {response.text}")

def main():
    # Get webhook URL from environment variable
    webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
    
    if not webhook_url:
        print("❌ DISCORD_WEBHOOK_URL environment variable not found!")
        print("Make sure to set it in your GitHub repository secrets.")
        return
    
    # Test message
    test_message = "🎓 College News Bot is working! This is a test message."
    
    print("Sending test message to Discord...")
    send_discord_message(webhook_url, test_message)

if __name__ == "__main__":
    main()