import threading
import telebot
import requests
import re
import time
import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Initialize the bot
bot = telebot.TeleBot("7790502564:AAE8kIqK_0VbtPH6xuwUMpVVW-yHrR9aLZc")  # Replace with your actual bot token

# Session management
session = requests.Session()

def normalize_url(url):
    """Ensure URL has http/https prefix and is properly formatted"""
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url

def is_valid_url(url):
    """Check if URL has valid structure"""
    try:
        url = normalize_url(url)
        regex = re.compile(
            r'^(?:http|ftp)s?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(regex, url) is not None
    except:
        return False

def find_payment_gateways(response_text):
    payment_gateways = [
        "paypal", "stripe", "braintree", "square", "cybersource", "authorize.net", "2checkout",
        "adyen", "worldpay", "sagepay", "checkout.com", "shopify", "razorpay", "bolt", "paytm",
        "venmo", "pay.google.com", "revolut", "eway", "woocommerce", "upi", "apple.com", "payflow",
        "payeezy", "paddle", "payoneer", "recurly", "klarna", "paysafe", "webmoney", "payeer",
        "payu", "skrill", "affirm", "afterpay", "dwolla", "global payments", "moneris", "nmi",
        "payment cloud", "paysimple", "paytrace", "stax", "alipay", "bluepay", "paymentcloud",
        "clover", "zelle", "google pay", "cashapp", "wechat pay", "transferwise", "stripe connect",
        "mollie", "sezzle", "afterpay", "payza", "gocardless", "bitpay", "sureship",
        "conekta", "fatture in cloud", "payzaar", "securionpay", "paylike", "nexi",
        "kiosk information systems", "adyen marketpay", "forte", "worldline", "payu latam"
    ]
    
    detected_gateways = []
    for gateway in payment_gateways:
        if gateway in response_text.lower():
            detected_gateways.append(gateway.capitalize())
    return detected_gateways

def check_captcha(response_text):
    captcha_keywords = {
        'recaptcha': ['recaptcha', 'google recaptcha'],
        'image selection': ['click images', 'identify objects', 'select all'],
        'text-based': ['enter the characters', 'type the text', 'solve the puzzle'],
        'verification': ['prove you are not a robot', 'human verification', 'bot check'],
        'security check': ['security check', 'challenge'],
        'hcaptcha': [
            'hcaptcha', 'verify you are human', 'select images', 
            'cloudflare challenge', 'anti-bot verification', 'hcaptcha.com',
            'hcaptcha-widget', 'solve the puzzle', 'please verify you are human'
        ]
    }

    detected_captchas = []
    for captcha_type, keywords in captcha_keywords.items():
        for keyword in keywords:
            if re.search(rf'\b{re.escape(keyword)}\b', response_text, re.IGNORECASE):
                if captcha_type not in detected_captchas:
                    detected_captchas.append(captcha_type)

    if re.search(r'<iframe.*?src=".*?hcaptcha.*?".*?>', response_text, re.IGNORECASE):
        if 'hcaptcha' not in detected_captchas:
            detected_captchas.append('hcaptcha')

    return ', '.join(detected_captchas) if detected_captchas else 'No captcha detected'

def check_url(url):
    """Check a single URL for payment gateways and security features"""
    try:
        url = normalize_url(url)
        if not is_valid_url(url):
            return [], 400, "Invalid", "Invalid", "Invalid URL", "N/A", "N/A"
        
        headers = {
            'User -Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Referer': 'https://www.google.com'
        }

        response = session.get(url, headers=headers, timeout=10)
        
        if response.status_code == 403:
            for attempt in range(3):
                time.sleep(2 ** attempt)
                response = session.get(url, headers=headers, timeout=10)
                if response.status_code != 403:
                    break

        if response.status_code == 403:
            return [], 403, "403 Forbidden: Access Denied", "N/A", "403 Forbidden", "N/A", "N/A"
        
        response.raise_for_status()
        detected_gateways = find_payment_gateways(response.text)
        captcha_type = check_captcha(response.text)
        gateways_str = ', '.join(detected_gateways) if detected_gateways else "None"

        return detected_gateways, response.status_code, captcha_type, "None", "2D (No extra security)", "N/A", "N/A"

    except requests.exceptions.HTTPError as http_err:
        return [], 500, "HTTP Error", "N/A", f"HTTP Error: {str(http_err)}", "N/A", "N/A"
    except requests.exceptions.RequestException as req_err:
        return [], 500, "Request Error", "N/A", f"Request Error: {str(req_err)}", "N/A", "N/A"

def update_progress_message(chat_id, message_id, url, progress):
    """Update progress message with loading bar"""
    try:
        progress_bars = "■" * progress + "□" * (5 - progress)
        truncated_url = url[:50] + "..." if len(url) > 50 else url
        status_message = (
            f"Checking URL: `{truncated_url}`\n"
            f"Progress: {progress_bars} ({progress*20}%)\n"
            "Please wait..."
        )
        bot.edit_message_text(
            status_message, 
            chat_id=chat_id, 
            message_id=message_id, 
            parse_mode='Markdown'
        )
        return message_id
    except Exception as e:
        print(f"Error updating progress: {e}")
        return None

@bot.message_handler(func=lambda message: message.text.startswith(('/start', '.start')))
def handle_start(message):
    """Handle /start command"""
    today_date = datetime.datetime.now().strftime("%d - %m - %Y")
    welcome_message = (
        "Welcome to URL Checker Bot\n"
        "Available commands:\n"
        "/url <url> - Check single URL\n"
        "/murl <url1> <url2> ... - Check multiple URLs\n"
        f"Today's date: {today_date}\n"
        "\nYou can now enter URLs with or without http:// or https://"
    )
    bot.reply_to(message, welcome_message)

@bot.message_handler(func=lambda message: message.text.startswith(("/url", ".url")))
def cmd_url(message):
    """Handle single URL check"""
    try:
        _, url = message.text.split(maxsplit=1)
        original_url = url.strip()
        url = normalize_url(original_url)
    except ValueError:
        bot.reply_to(message, "Usage: `.url <URL>` or `/url <URL>`")
        return

    if not is_valid_url(url):
        bot.reply_to(message, "Invalid URL. Please try again.")
        return

    # Send initial progress message
    try:
        progress_msg = bot.send_message(
            message.chat.id, 
            f"Checking URL: `{original_url[:50]}`\nProgress: □□□□□ (0%)\nPlease wait...", 
            parse_mode='Markdown'
        )
        message_id = progress_msg.message_id
        
        # Update progress in steps
        for progress in range(1, 6):
            time.sleep(0.3)
            message_id = update_progress_message(message.chat.id, message_id, original_url, progress)
            if not message_id:
                break
        
        # Get results
        detected_gateways, status_code, captcha, cloudflare, payment_security_type, cvv_cvc_status, inbuilt_status = check_url(url)
        gateways_str = ', '.join(detected_gateways) if detected_gateways else "None"
        
        # Format output
        formatted_url = f"`{original_url[:100]}`" if len(original_url) <= 100 else f"`{original_url[:97]}...`"
        
        result_message = (
            f"┏━━━━━━━⍟\n"
            f"┃ 𝗟𝗼𝗼𝗸𝘂𝗽 𝗥𝗲𝘀𝘂𝗹𝘁 : ✅\n"
            f"┗━━━━━━━━━━━━⊛\n"
            f"─━─━─━─━─━─━─━─━─━─\n"
            f"➥ 𝗦𝗶𝘁𝗲 -» {formatted_url}\n"
            f"➥ 𝗣𝗮𝘆𝗺𝗲𝗻𝘁 𝗚𝗮𝘁𝗲𝘄𝗮𝘆𝘀 -» {gateways_str}\n"
            f"➥ 𝗖𝗮𝗽𝘁𝗰𝗵𝗮 -» {captcha}\n"
            f"➥ 𝗖𝗹𝗼𝘂𝗱𝗳𝗹𝗮𝗿𝗲 -» {cloudflare}\n"
            f"➥ 𝗦𝗲𝗰𝘂𝗿𝗶𝘁𝘆 -» {payment_security_type}\n"
            f"➥ 𝗖𝗩𝗩/𝗖𝗩𝗖 -» {cvv_cvc_status}\n"
            f"➥ 𝗜𝗻𝗯𝘂𝗶𝗹𝘁 𝗦𝘆𝘀𝘁𝗲𝗺 -» {inbuilt_status}\n"
            f"➥ 𝗦𝘁𝗮𝘁𝘂𝘀 -» {status_code}\n"
            f"─━─━─━─━─━─━─━─━─━─\n"
        )
        
        # Send final result
        try:
            bot.edit_message_text(
                result_message, 
                chat_id=message.chat.id, 
                message_id=message_id,
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"Error editing final message: {e}")
            bot.edit_message_text(
                result_message.replace('`', '').replace('*', ''),
                chat_id=message.chat.id,
                message_id=message_id
            )
            
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")

@bot.message_handler(func=lambda message: message.text.startswith(("/murl", ".murl")))
def cmd_murl(message):
    """Handle multiple URL checks"""
    try:
        _, urls = message.text.split(maxsplit=1)
        urls = re.split(r'[\n\s]+', urls.strip())
    except ValueError:
        bot.reply_to(message, "Usage: `.murl <URL1> <URL2> ...` or `/murl <URL1> <URL2> ...`")
        return

    if not urls:
        bot.reply_to(message, "No URLs provided. Please try again.")
        return

    # Send initial processing message
    try:
        processing_msg = bot.send_message(
            message.chat.id,
            f"Processing 0/{len(urls)} URLs\nCurrent: None\nPlease wait...",
            parse_mode='Markdown'
        )
        message_id = processing_msg.message_id
    except Exception as e:
        print(f"Error sending initial message: {e}")
        message_id = None

    results = []
    total_urls = len(urls)
    
    for index, url in enumerate(urls, 1):
        original_url = url.strip()
        url = normalize_url(original_url)
        
        if not is_valid_url(url):
            results.append(f"[↯] URL: `{original_url}` ➡ Invalid URL")
            continue

        # Update progress
        progress_text = f"Processing {index}/{total_urls} URLs\nCurrent: `{original_url[:50]}`"
        try:
            if message_id:
                bot.edit_message_text(
                    progress_text,
                    chat_id=message.chat.id,
                    message_id=message_id,
                    parse_mode='Markdown'
                )
        except Exception as e:
            print(f"Error updating progress: {e}")

        # Check URL
        detected_gateways, status_code, captcha, cloudflare, payment_security_type, cvv_cvc_status, inbuilt_status = check_url(url)
        gateways_str = ', '.join(detected_gateways) if detected_gateways else "None"
        
        # Format output
        formatted_url = f"`{original_url[:100]}`" if len(original_url) <= 100 else f"`{original_url[:97]}...`"
        
        results.append(
            f"┏━━━━━━━⍟\n"
            f"┃ 𝗟𝗼𝗼𝗸𝘂𝗽 𝗥𝗲𝘀𝘂𝗹𝘁 : ✅ ({index}/{total_urls})\n"
            f"┗━━━━━━━━━━━━⊛\n"
            f"─━─━─━─━─━─━─━─━─━─\n"
            f"➥ 𝗦𝗶𝘁𝗲 -» {formatted_url}\n"
            f"➥ 𝗣𝗮𝘆𝗺𝗲𝗻𝘁 𝗚𝗮𝘁𝗲𝘄𝗮𝘆𝘀 -» {gateways_str}\n"
            f"➥ 𝗖𝗮𝗽𝘁𝗰𝗵𝗮 -» {captcha}\n"
            f"➥ 𝗖𝗹𝗼𝘂𝗱𝗳𝗹𝗮𝗿𝗲 -» {cloudflare}\n"
            f"➥ 𝗦𝗲𝗰𝘂𝗿𝗶𝘁𝘆 -» {payment_security_type}\n"
            f"➥ 𝗖𝗩𝗩/𝗖𝗩𝗖 -» {cvv_cvc_status}\n"
            f"➥ 𝗜𝗻𝗯𝘂𝗶𝗹𝘁 𝗦𝘆𝘀𝘁𝗲𝗺 -» {inbuilt_status}\n"
            f"➥ 𝗦𝘁𝗮𝘁𝘂𝘀 -» {status_code}\n"
            f"─━─━─━─━─━─━─━─━─━─\n"
        )

    # Delete processing message if it exists
    if message_id:
        try:
            bot.delete_message(message.chat.id, message_id)
        except Exception as e:
            print(f"Error deleting progress message: {e}")

    if results:
        # Send completion message
        completion_msg = f"✅ Completed checking {len(results)} URLs"
        try:
            bot.send_message(message.chat.id, completion_msg)
        except Exception as e:
            print(f"Error sending completion message: {e}")
        
        # Send results
        for result in results:
            try:
                if len(result) > 4096:
                    for i in range(0, len(result), 4096):
                        bot.send_message(
                            message.chat.id, 
                            result[i:i + 4096], 
                            parse_mode='Markdown'
                        )
                else:
                    bot.send_message(
                        message.chat.id, 
                        result, 
                        parse_mode='Markdown'
                    )
            except Exception as e:
                print(f"Error sending result: {e}")
    else:
        bot.reply_to(message, "No valid URLs detected. Please try again.")

def run_bot():
    while True:
        try:
            print("Bot is running...")
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    # Start the bot
    run_bot()
