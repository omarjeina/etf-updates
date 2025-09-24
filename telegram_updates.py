import requests
import os
from bs4 import BeautifulSoup
from datetime import datetime
import json

def send_telegram_message(bot_token, chat_id, message):
    """Send a message to Telegram via bot API"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        print("✅ Telegram message sent successfully!")
    else:
        print(f"❌ Failed to send message. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return response.status_code == 200

def scrape_etf_news():
    """Scrape ETF general announcements"""
    url = "https://www.etf.unsa.ba/obavjestenja"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        announcements = []
        
        # Find divs with class "mb-3 bg-light p-3" and get "a" tags from them
        announcement_divs = soup.find_all('div', class_=['mb-3', 'bg-light', 'p-3'])
        
        # If the above doesn't work, try different combinations
        if not announcement_divs:
            announcement_divs = soup.find_all('div', class_='mb-3 bg-light p-3')
        
        if not announcement_divs:
            # Fallback: look for divs with any of these classes
            announcement_divs = soup.find_all('div', class_=lambda x: x and ('mb-3' in x or 'bg-light' in x))
        
        print(f"Found {len(announcement_divs)} announcement divs")
        
        for div in announcement_divs[:7]:  # Get first 7
            # Find the "a" tag within this div
            link = div.find('a', href=True)
            
            if link:
                href = link.get('href')
                title = link.get_text(strip=True)
                
                if title and len(title) > 5:  # Basic validation
                    full_url = href if href.startswith('http') else f"https://www.etf.unsa.ba{href}"
                    
                    announcements.append({
                        'title': title[:150],  # Allow longer titles
                        'url': full_url,
                        'source': 'ETF'
                    })
        
        return announcements
        
    except Exception as e:
        print(f"❌ Error scraping ETF news: {e}")
        return []

def scrape_dsai_news():
    """Scrape DSAI news"""
    url = "https://dsai.etf.unsa.ba/news/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        news_items = []
        
        # Find "a" tags with class "ee-post-title-link"
        post_links = soup.find_all('a', class_='ee-post-title-link')
        
        print(f"Found {len(post_links)} DSAI post links")
        
        for link in post_links[:3]:  # Get first 3
            href = link.get('href')
            title = link.get_text(strip=True)
            
            if href and title and len(title) > 5:  # Basic validation
                full_url = href if href.startswith('http') else f"https://dsai.etf.unsa.ba{href}"
                
                news_items.append({
                    'title': title[:150],  # Allow longer titles
                    'url': full_url,
                    'source': 'DSAI'
                })
        
        return news_items
        
    except Exception as e:
        print(f"❌ Error scraping DSAI news: {e}")
        return []

def load_stored_posts(filename):
    """Load previously stored posts from file"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"❌ Error loading {filename}: {e}")
        return []

def save_posts(filename, posts):
    """Save posts to file with cleanup if needed"""
    try:
        # If more than 20 posts, keep only the first 10 (most recent)
        if len(posts) > 20:
            posts = posts[:10]
            print(f"🧹 Cleaned up {filename} - kept 10 most recent posts")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        print(f"💾 Saved {len(posts)} posts to {filename}")
        
    except Exception as e:
        print(f"❌ Error saving to {filename}: {e}")

def find_new_posts(current_posts, stored_posts):
    """Find new posts by comparing URLs"""
    stored_urls = {post['url'] for post in stored_posts}
    new_posts = []
    
    for post in current_posts:
        if post['url'] not in stored_urls:
            new_posts.append(post)
    
    return new_posts

def format_telegram_message(posts, source):
    """Format posts for Telegram message"""
    if not posts:
        return None
    
    emoji = "ETF" if source == "ETF" else "DSAI"
    header = f"{emoji} <b>Novo {source} obavještenje</b>\n\n"
    
    message_parts = [header]
    
    for i, post in enumerate(posts, 1):
        title = post['title'][:80] + "..." if len(post['title']) > 80 else post['title']
        message_parts.append(f"{i}. <a href='{post['url']}'>{title}</a>\n")
    
    message_parts.append(f"\n🕐 <i>Vrijeme provjere: {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>")
    
    return "".join(message_parts)

def main():
    print(f"🚀 Starting college news scraper at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get Telegram credentials
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("❌ Missing Telegram credentials!")
        return
    
    # Special check for September 24, 2025 - send current posts summary
    today = datetime.now().strftime('%Y-%m-%d')
    if today == '2025-09-24':
        print("🎯 Special date detected! Sending current posts summary...")
        
        # Scrape current posts
        current_etf_posts = scrape_etf_news()
        current_dsai_posts = scrape_dsai_news()
        
        # Send summary of current posts (not as "new" posts)
        if current_etf_posts or current_dsai_posts:
            summary_message = f"🧪 <b>Test Summary - September 24, 2025</b>\n\n"
            
            if current_etf_posts:
                summary_message += f"🎓 <b>Current ETF Announcements ({len(current_etf_posts)}):</b>\n"
                for i, post in enumerate(current_etf_posts, 1):
                    title = post['title'][:60] + "..." if len(post['title']) > 60 else post['title']
                    summary_message += f"{i}. <a href='{post['url']}'>{title}</a>\n"
                summary_message += "\n"
            
            if current_dsai_posts:
                summary_message += f"🤖 <b>Current DSAI News ({len(current_dsai_posts)}):</b>\n"
                for i, post in enumerate(current_dsai_posts, 1):
                    title = post['title'][:60] + "..." if len(post['title']) > 60 else post['title']
                    summary_message += f"{i}. <a href='{post['url']}'>{title}</a>\n"
                summary_message += "\n"
            
            summary_message += f"✅ <i>Scraper is working correctly!</i>\n"
            summary_message += f"🕐 <i>Checked: {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>"
            
            if send_telegram_message(bot_token, chat_id, summary_message):
                print("✅ Special date summary sent!")
        
        # Continue with normal operation below
    
    # File paths
    etf_file = "etf_posts.json"
    dsai_file = "dsai_posts.json"
    
    # Load stored posts
    print("📂 Loading stored posts...")
    stored_etf_posts = load_stored_posts(etf_file)
    stored_dsai_posts = load_stored_posts(dsai_file)
    
    # Scrape current posts
    print("🔍 Scraping ETF announcements...")
    current_etf_posts = scrape_etf_news()
    print(f"Found {len(current_etf_posts)} ETF posts")
    
    print("🔍 Scraping DSAI news...")
    current_dsai_posts = scrape_dsai_news()
    print(f"Found {len(current_dsai_posts)} DSAI posts")
    
    # Find new posts
    new_etf_posts = find_new_posts(current_etf_posts, stored_etf_posts)
    new_dsai_posts = find_new_posts(current_dsai_posts, stored_dsai_posts)
    
    print(f"📢 Found {len(new_etf_posts)} new ETF posts")
    print(f"📢 Found {len(new_dsai_posts)} new DSAI posts")
    
    # Send notifications for new posts
    messages_sent = 0
    
    if new_etf_posts:
        message = format_telegram_message(new_etf_posts, "ETF")
        if message and send_telegram_message(bot_token, chat_id, message):
            messages_sent += 1
    
    if new_dsai_posts:
        message = format_telegram_message(new_dsai_posts, "DSAI")
        if message and send_telegram_message(bot_token, chat_id, message):
            messages_sent += 1
    
    # Update stored posts with new ones at the beginning
    if current_etf_posts:
        # Add new posts to the beginning, keep existing ones
        updated_etf_posts = current_etf_posts + [post for post in stored_etf_posts if post['url'] not in {p['url'] for p in current_etf_posts}]
        save_posts(etf_file, updated_etf_posts)
    
    if current_dsai_posts:
        updated_dsai_posts = current_dsai_posts + [post for post in stored_dsai_posts if post['url'] not in {p['url'] for p in current_dsai_posts}]
        save_posts(dsai_file, updated_dsai_posts)
    
    # Summary
    if messages_sent > 0:
        print(f"✅ Scraper completed! Sent {messages_sent} notification(s)")
    else:
        print("✅ Scraper completed! No new posts found")
        
        # Send a daily summary if no new posts (optional)
        if datetime.now().hour == 12:  # Send summary at noon
            summary = f"📊 <b>Daily Summary</b>\n\n🎓 ETF: {len(current_etf_posts)} announcements tracked\n🤖 DSAI: {len(current_dsai_posts)} news items tracked\n\n🔍 No new posts since last check\n🕐 <i>{datetime.now().strftime('%d/%m/%Y %H:%M')}</i>"
            send_telegram_message(bot_token, chat_id, summary)

if __name__ == "__main__":
    main()