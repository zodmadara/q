import random
import time
import requests
import asyncio
import aiohttp
import telebot
from datetime import datetime, timedelta

# Initialize bot with token
token = input('Enter your bot token: ')
bot = telebot.TeleBot(token)

# Dictionary to track last request time for each user
# Dictionary to track last request time for each user
user_last_request = {}
request_limit_time = 5  # time limit in seconds for requests

# Helper function to safely make a request
def safe_request(url):
    try:
        return requests.get(url)
    except requests.exceptions.RequestException:
        return None

# Rate limiting check
def is_request_allowed(user_id):
    now = datetime.now()
    last_request_time = user_last_request.get(user_id)

    if last_request_time is None or (now - last_request_time) > timedelta(seconds=request_limit_time):
        user_last_request[user_id] = now
        return True
    return False

# Check if website has captcha
def check_captcha(url):
    response = safe_request(url)
    if response is None:
        return False
    if ('https://www.google.com/recaptcha/api' in response.text or
        'captcha' in response.text or
        'verifyRecaptchaToken' in response.text or
        'grecaptcha' in response.text or
        'www.google.com/recaptcha' in response.text):
        return True
    return False

# Check for multiple payment systems in the website
def check_credit_card_payment(url):
    response = safe_request(url)
    if response is None:
        return 'Error accessing the website'
    
    gateways = []
    if 'stripe' in response.text:
        gateways.append('Stripe')
    if 'Cybersource' in response.text:
        gateways.append('Cybersource')
    if 'paypal' in response.text:
        gateways.append('Paypal')
    if 'authorize.net' in response.text:
        gateways.append('Authorize.net')
    if 'Bluepay' in response.text:
        gateways.append('Bluepay')
    if 'Magento' in response.text:
        gateways.append('Magento')
    if 'woo' in response.text:
        gateways.append('WooCommerce')
    if 'Shopify' in response.text:
        gateways.append('Shopify')
    if 'adyen' in response.text or 'Adyen' in response.text:
        gateways.append('Adyen')
    if 'braintree' in response.text:
        gateways.append('Braintree')
    if 'square' in response.text:
        gateways.append('Square')
    if 'payflow' in response.text:
        gateways.append('Payflow')
    
    return ', '.join(gateways) if gateways else 'No recognized payment gateway found'

# Check for cloud services in the website
def check_cloud_in_website(url):
    response = safe_request(url)
    if response is None:
        return False
    if 'cloudflare' in response.text.lower():
        return True
    return False

# Check for GraphQL
def check_graphql(url):
    response = safe_request(url)
    if response is None:
        return False
    if 'graphql' in response.text.lower() or 'query {' in response.text or 'mutation {' in response.text:
        return True
    
    # Optionally, try querying the /graphql endpoint directly
    graphql_url = url.rstrip('/') + '/graphql'
    graphql_response = safe_request(graphql_url)
    if graphql_response and graphql_response.status_code == 200:
        return True
    
    return False

# Check if the path /my-account/add-payment-method/ exists
def check_auth_path(url):
    auth_path = url.rstrip('/') + '/my-account/add-payment-method/'
    response = safe_request(auth_path)
    if response is not None and response.status_code == 200:
        return 'Auth ✔️'
    return 'None ❌'

# Get the status code
def get_status_code(url):
    response = safe_request(url)
    if response is not None:
        return response.status_code
    return 'Error'

# Check for platform (simplified)
def check_platform(url):
    response = safe_request(url)
    if response is None:
        return 'None'
    if 'wordpress' in response.text.lower():
        return 'WordPress'
    if 'shopify' in response.text.lower():
        return 'Shopify'
    return 'None'

# Check for error logs (simplified)
def check_error_logs(url):
    response = safe_request(url)
    if response is None:
        return 'None'
    if 'error' in response.text.lower() or 'exception' in response.text.lower():
        return 'Error logs found'
    return 'None'

# Generate credit card numbers based on a BIN
def generate_credit_card_numbers(bin_number, amount):
    card_numbers = []
    for _ in range(amount):  # Generate 'amount' card numbers
        # Create a 16-digit card number using the BIN
        card_number = bin_number + ''.join([str(random.randint(0, 9)) for _ in range(10)])  
        expiration_date = f"{random.randint(1, 12):02}|{random.randint(2024, 2030)}"  # MM|YYYY
        cvv = f"{random.randint(100, 999)}"  # CVV
        card_numbers.append(f"{card_number}|{expiration_date}|{cvv}")
    return card_numbers

# Check single URL with /check command
@bot.message_handler(commands=['check'])
def check_url(message):
    if len(message.text.split()) < 2:
        bot.reply_to(message, '𝐏𝐥𝐞𝐚𝐬𝐞 𝐩𝐫𝐨𝐯𝐢𝐝𝐞 𝐚 𝐯𝐚𝐥𝐢𝐝 𝐔𝐑𝐋 𝐚𝐟𝐭𝐞𝐫 𝐭𝐡𝐞 /check 𝐜𝐨𝐦𝐦𝐚𝐧𝐝')
        return

    user_id = message.from_user.id
    if not is_request_allowed(user_id):
        bot.reply_to(message, '𝐏𝐥𝐞𝐚𝐬𝐞 𝐰𝐚𝐢𝐭 𝐚 𝐟𝐞𝐰 𝐬𝐞𝐜𝐨𝐧𝐝𝐬 𝐛𝐞𝐟𝐨𝐫𝐞 𝐦𝐚𝐤𝐢𝐧𝐠 𝐚𝐧𝐨𝐭𝐡𝐞𝐫 𝐫𝐞𝐪𝐮𝐞𝐬𝐭')
        return

    url = message.text.split()[1]

    try:
        captcha = check_captcha(url)
    except:
        captcha = 'Error checking captcha'

    cloud = check_cloud_in_website(url)
    payment = check_credit_card_payment(url)
    graphql = check_graphql(url)
    auth_path = check_auth_path(url)
    platform = check_platform(url)
    error_logs = check_error_logs(url)
    status_code = get_status_code(url)

    loading_message = bot.reply_to(message, '<strong>[~]-Loading... 🥸</strong>', parse_mode="HTML")
    time.sleep(1)

    captcha_emoji = "😞" if captcha else "🔥"
    cloud_emoji = "😞" if cloud else "🔥"

    # Create formatted message with <code> tag for the URL
    response_message = (
        "🔍 ɢᴀᴛᴇᴡᴀʏꜱ ꜰᴇᴛᴄʜᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ \n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔗 𝐔𝐑𝐋: <code>{url}</code>\n"
        f"💳 𝐏𝐚𝐲𝐦𝐞𝐧𝐭 𝐆𝐚𝐭𝐞𝐰𝐚𝐲𝐬: {payment}\n"
        f"👾 𝐂𝐚𝐩𝐭𝐜𝐡𝐚: {captcha} {captcha_emoji}\n"
        f"☁️ 𝐂𝐥𝐨𝐮𝐝𝐟𝐥𝐚𝐫𝐞: {cloud} {cloud_emoji}\n"
        f"📊 𝐆𝐫𝐚𝐩𝐡𝐐𝐋: {graphql}\n"
        f"🛤️ 𝐀𝐮𝐭𝐡 𝐏𝐚𝐭𝐡: {auth_path}\n"
        f"⭐ 𝐏𝐥𝐚𝐭𝐟𝐨𝐫𝐦: {platform}\n"
        f"🤖 𝐄𝐫𝐫𝐨𝐫 𝐋𝐨𝐠𝐬: {error_logs}\n"
        f"🌡️ 𝐒𝐭𝐚𝐭𝐮𝐬: {status_code}\n"
        "\n𝐁𝐨𝐭 𝐁𝐲: @ZodMadara"
    )

    bot.edit_message_text(response_message, message.chat.id, loading_message.message_id, parse_mode='HTML')


@bot.message_handler(content_types=['document'])
def handle_txt_file(message):
    file_info = bot.get_file(message.document.file_id)
    file_extension = file_info.file_path.split('.')[-1]

    if file_extension != 'txt':
        bot.reply_to(message, '𝐏𝐥𝐞𝐚𝐬𝐞 𝐮𝐩𝐥𝐨𝐚𝐝 𝐚 .𝐭𝐱𝐭 𝐟𝐢𝐥𝐞 𝐜𝐨𝐧𝐭𝐚𝐢𝐧𝐢𝐧𝐠 𝐔𝐑𝐋𝐬')
        return

    file = bot.download_file(file_info.file_path)
    urls = file.decode('utf-8').splitlines()

    # Validate URL count (should be between 50 and 100)
    if len(urls) < 50 or len(urls) > 100:
        bot.reply_to(message, '𝐏𝐥𝐞𝐚𝐬𝐞 𝐩𝐫𝐨𝐯𝐢𝐝𝐞 𝐚 .𝐭𝐱𝐭 𝐟𝐢𝐥𝐞 𝐰𝐢𝐭𝐡 𝐛𝐞𝐭𝐰𝐞𝐞𝐧 𝟓𝟎 𝐚𝐧𝐝 𝟏𝟎𝟎 𝐔𝐑𝐋𝐬')
        return

    bot.reply_to(message, '𝐏𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠 𝐲𝐨𝐮𝐫 𝐔𝐑𝐋𝐬... 𝐓𝐡𝐢𝐬 𝐦𝐚𝐲 𝐭𝐚𝐤𝐞 𝐬𝐨𝐦𝐞 𝐭𝐢𝐦𝐞')

    results = []
    for url in urls:
        try:
            captcha = check_captcha(url)
        except:
            captcha = 'Error checking captcha'

        cloud = check_cloud_in_website(url)
        payment = check_credit_card_payment(url)
        graphql = check_graphql(url)
        auth_path = check_auth_path(url)
        platform = check_platform(url)
        error_logs = check_error_logs(url)
        status_code = get_status_code(url)

        captcha_emoji = "😞" if captcha else "🔥"
        cloud_emoji = "😞" if cloud else "🔥"

        # Create result message with <code> tag for the URL
        result_message = (
            "━━━━━━━━━━━━━━\n"
            f"🔗 𝐔𝐑𝐋: <code>{url}</code>\n"
            f"💳 𝐏𝐚𝐲𝐦𝐞𝐧𝐭 𝐆𝐚𝐭𝐞𝐰𝐚𝐲𝐬: {payment}\n"
            f"👾 𝐂𝐚𝐩𝐭𝐜𝐡𝐚: {captcha} {captcha_emoji}\n"
            f"☁️ 𝐂𝐥𝐨𝐮𝐝𝐟𝐥𝐚𝐫𝐞: {cloud} {cloud_emoji}\n"
            f"📊 𝐆𝐫𝐚𝐩𝐡𝐐𝐋: {graphql}\n"
            f"🛤️ 𝐀𝐮𝐭𝐡 𝐏𝐚𝐭𝐡: {auth_path}\n"
            f"⭐ 𝐏𝐥𝐚𝐭𝐟𝐨𝐫𝐦: {platform}\n"
            f"🤖 𝐄𝐫𝐫𝐨𝐫 𝐋𝐨𝐠𝐬: {error_logs}\n"
            f"🌡️ 𝐒𝐭𝐚𝐭𝐮𝐬: {status_code}\n"
        )
        results.append(result_message)

    # Send all results back to the user with HTML parsing
    final_response = "\n".join(results)
    bot.reply_to(message, final_response, parse_mode='HTML')

# Command to check sk_live key
@bot.message_handler(commands=['sk'])
def check_sk_key(message):
    if len(message.text.split()) < 2:
        bot.reply_to(message, '𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗦𝗞 ⚠️

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗡𝗼 𝗩𝗮𝗹𝗶𝗱 𝗦𝗞 𝘄𝗮𝘀 𝗳𝗼𝘂𝗻𝗱 𝗶𝗻 𝘆𝗼𝘂𝗿 𝗶𝗻𝗽𝘂𝘁.')
        return

    user_id = message.from_user.id
    if not is_request_allowed(user_id):
        bot.reply_to(message, 'Please wait a few seconds before making another request.')
        return

    key = message.text.split()[1]
    balance_response = requests.get('https://api.stripe.com/v1/balance', auth=(key, ''))
    account_response = requests.get('https://api.stripe.com/v1/account', auth=(key, ''))

    if balance_response.status_code == 200 and account_response.status_code == 200:
        account_info = account_response.json()
        balance_info = balance_response.json()

        # Collect account information
        publishable_key = account_info.get('keys', {}).get('publishable', 'Not Available')
        account_id = account_info.get('id', 'Not Available')
        charges_enabled = account_info.get('charges_enabled', 'Not Available')
        live_mode = account_info.get('livemode', 'Not Available')
        country = account_info.get('country', 'Not Available')
        currency = balance_info.get('currency', 'Not Available')
        available_balance = balance_info.get('available', [{'amount': '0'}])[0]['amount']
        pending_balance = balance_info.get('pending', [{'amount': '0'}])[0]['amount']
        payments_enabled = account_info.get('payouts_enabled', 'Not Available')
        name = account_info.get('business_name', 'Not Available')
        phone = account_info.get('support_phone', 'Not Available')
        email = account_info.get('email', 'Not Available')
        url = account_info.get('url', 'Not Available')

        response = (
    f''' 𝙎𝙆 𝙠𝙚𝙮✅\n<code>{key}</code>\n\n'''
    
    f''' 🔑 𝙋𝙆 𝙆𝙚𝙮\n<code>{publishable_key}</code>\n'''
    
    f''' 🆔 𝘼𝙘𝙘𝙤𝙪𝙣𝙩 𝙄𝘿 :\n{account_id}\n'''
    
    " ⚜️⚜️ 𝙎𝙆 𝙆𝙚𝙮 𝙄𝙣𝙛𝙤  ⚜️⚜️ \n"
    f" 𝗖𝗵𝗮𝗿𝗴𝗲𝘀 𝗘𝗻𝗮𝗯𝗹𝗲𝗱 : {charges_enabled}\n"
    f" 𝗟𝗶𝘃𝗲 𝗠𝗼𝗱𝗲 : {live_mode}\n"
    f" 𝗣𝗮𝘆𝗺𝗲𝗻𝘁𝘀 : {payments_enabled}\n"
    f" 𝗔𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗕𝗮𝗹𝗮𝗻𝗰𝗲 : {available_balance}\n"
    f" 𝗔𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗕𝗮𝗹𝗮𝗻𝗰𝗲 : {available_balance}\n"
    f" 𝗣𝗲𝗻𝗱𝗶𝗻𝗴 𝗕𝗮𝗹𝗮𝗻𝗰𝗲 : {pending_balance}\n"
    f" 𝗖𝘂𝗿𝗿𝗲𝗻𝗰𝘆 : {currency}\n"
    f" 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 : {country}\n"
    f" 𝗡𝗮𝗺𝗲 : {name}\n"
    f" 𝗣𝗵𝗼𝗻𝗲 : {phone}\n"
    f" 𝗘𝗺𝗮𝗶𝗹 : {email}\n"
    f''' 𝗨𝗿𝗹 : <code>{url}</code>\n'''
)

        bot.reply_to(message, response, parse_mode='HTML')
    else:
        bot.reply_to(message, f'𝐄𝐗𝐏𝐈𝐑𝐄𝐃 𝐊𝐄𝐘 ❌ 𝐎𝐑 𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐊𝐄𝐘 𝐆𝐈𝐕𝐄𝐍 ❌.\nKey: <code>{key}</code>', parse_mode='HTML')

# Function to check if the user can make another request
# Mapping of country codes to flag emojis
country_flags = {
    "AD": "🇦🇩", "AE": "🇦🇪", "AF": "🇦🇫", "AG": "🇦🇬", "AI": "🇦🇮",
    "AL": "🇦🇱", "AM": "🇦🇲", "AO": "🇦🇴", "AR": "🇦🇷", "AS": "🇦🇸",
    "AT": "🇦🇹", "AU": "🇦🇺", "AW": "🇦🇼", "AX": "🇦🇽", "AZ": "🇦🇿",
    "BA": "🇧🇦", "BB": "🇧🇧", "BD": "🇧🇩", "BE": "🇧🇪", "BF": "🇧🇫",
    "BG": "🇧🇬", "BH": "🇧🇭", "BI": "🇧🇮", "BJ": "🇧🇯", "BL": "🇧🇱",
    "BM": "🇧🇲", "BN": "🇧🇳", "BO": "🇧🇴", "BQ": "🇧🇶", "BR": "🇧🇷",
    "BS": "🇧🇸", "BT": "🇧🇹", "BV": "🇧🇻", "BW": "🇧🇼", "BY": "🇧🇾",
    "BZ": "🇧🇿", "CA": "🇨🇦", "CC": "🇨🇨", "CD": "🇨🇩", "CF": "🇨🇫",
    "CG": "🇨🇬", "CH": "🇨🇭", "CI": "🇨🇮", "CK": "🇨🇰", "CL": "🇨🇱",
    "CM": "🇨🇲", "CN": "🇨🇳", "CO": "🇨🇴", "CR": "🇨🇷", "CU": "🇨🇺",
    "CV": "🇨🇻", "CW": "🇨🇼", "CX": "🇭🇨", "CY": "🇨🇾", "CZ": "🇨🇿",
    "DE": "🇩🇪", "DJ": "🇩🇯", "DK": "🇩🇰", "DM": "🇩🇲", "DO": "🇩🇴",
    "DZ": "🇩🇿", "EC": "🇪🇨", "EE": "🇪🇪", "EG": "🇪🇬", "EH": "🇪🇭",
    "ER": "🇪🇷", "ES": "🇪🇸", "ET": "🇪🇹", "FI": "🇫🇮", "FJ": "🇫🇯",
    "FM": "🇫🇲", "FO": "🇫🇴", "FR": "🇫🇷", "GA": "🇬🇦", "GB": "🇬🇧",
    "GD": "🇬🇩", "GE": "🇬🇪", "GF": "🇬🇫", "GG": "🇬🇬", "GH": "🇬🇭",
    "GI": "🇬🇮", "GL": "🇬🇱", "GM": "🇬🇲", "GN": "🇬🇳", "GP": "🇬🇵",
    "GQ": "🇬🇶", "GR": "🇬🇷", "GT": "🇬🇹", "GU": "🇬🇺", "GW": "🇬🇼",
    "GY": "🇬🇾", "HK": "🇭🇰", "HM": "🇭🇲", "HN": "🇭🇳", "HR": "🇭🇷",
    "HT": "🇭🇹", "HU": "🇭🇺", "ID": "🇮🇩", "IE": "🇮🇪", "IL": "🇮🇱",
    "IM": "🇮🇲", "IN": "🇮🇳", "IO": "🇮🇴", "IQ": "🇮🇶", "IR": "🇮🇷",
    "IS": "🇮🇸", "IT": "🇮🇹", "JE": "🇯🇪", "JM": "🇯🇲", "JO": "🇯🇴",
    "JP": "🇯🇵", "KE": "🇰🇪", "KG": "🇰🇬", "KH": "🇰🇭", "KI": "🇰🇮",
    "KM": "🇰🇲", "KN": "🇰🇳", "KP": "🇰🇵", "KR": "🇰🇷", "KW": "🇰🇼",
    "KY": "🇰🇾", "KZ": "🇰🇿", "LA": "🇱🇦", "LB": "🇱🇧", "LC": "🇱🇨",
    "LI": "🇱🇮", "LK": "🇱🇰", "LR": "🇱🇷", "LS": "🇱🇸", "LT": "🇱🇹",
    "LU": "🇱🇺", "LV": "🇱🇻", "LY": "🇱🇾", "MA": "🇲🇦", "MC": "🇲🇨",
    "MD": "🇲🇩", "ME": "🇲🇪", "MF": "🇲🇫", "MG": "🇲🇬", "MH": "🇲🇭",
    "MK": "🇲🇰", "ML": "🇲🇱", "MM": "🇲🇲", "MN": "🇲🇳", "MO": "🇲🇴",
    "MP": "🇲🇵", "MQ": "🇲🇶", "MR": "🇲🇷", "MS": "🇲🇸", "MT": "🇲🇹",
    "MU": "🇲🇺", "MV": "🇲🇻", "MW": "🇲🇼", "MX": "🇲🇽", "MY": "🇲🇾",
    "MZ": "🇲🇿", "NA": "🇳🇦", "NC": "🇳🇨", "NE": "🇳🇪", "NF": "🇳🇫",
    "NG": "🇳🇬", "NI": "🇳🇮", "NL": "🇳🇱", "NO": "🇳🇴", "NP": "🇳🇵",
    "NR": "🇳🇷", "NU": "🇳🇺", "NZ": "🇳🇿", "OM": "🇴🇲", "PA": "🇵🇦",
    "PE": "🇵🇪", "PF": "🇵🇫", "PG": "🇵🇬", "PH": "🇵🇭", "PK": "🇵🇰",
    "PL": "🇵🇱", "PM": "🇵🇲", "PN": "🇵🇳", "PR": "🇵🇷", "PT": "🇵🇹",
    "PW": "🇵🇼", "PY": "🇵🇾", "QA": "🇶🇦", "RE": "🇷🇪", "RO": "🇷🇴",
    "RS": "🇷🇸", "RU": "🇷🇺", "RW": "🇷🇼", "SA": "🇸🇦", "SB": "🇸🇧",
    "SC": "🇸🇨", "SD": "🇸🇩", "SE": "🇸🇪", "SG": "🇸🇬", "SH": "🇸🇭",
    "SI": "🇸🇮", "SJ": "🇸🇯", "SK": "🇸🇰", "SL": "🇸🇱", "SM": "🇸🇲",
    "SN": "🇸🇳", "SO": "🇸🇴", "SR": "🇸🇷", "SS": "🇸🇸", "ST": "🇸🇹",
    "SV": "🇸🇻", "SX": "🇸🇽", "SY": "🇸🇾", "SZ": "🇸🇿", "TC": "🇹🇨",
    "TD": "🇹🇩", "TF": "🇹🇫", "TG": "🇹🇬", "TH": "🇹🇭", "TJ": "🇹🇯", "TK": "🇹🇰",
    "TL": "🇹🇱", "TM": "🇹🇲", "TN": "🇹🇳", "TO": "🇹🇴", "TR": "🇹🇷",
    "TT": "🇹🇹", "TV": "🇹🇻", "TZ": "🇹🇿", "UA": "🇺🇦", "UG": "🇺🇬",
    "UM": "🇺🇲", "US": "🇺🇸", "UY": "🇺🇾", "UZ": "🇺🇿", "VA": "🇻🇦",
    "VC": "🇻🇨", "VE": "🇻🇪", "VG": "🇻🇬", "VI": "🇻🇮", "VN": "🇻🇳",
    "VU": "🇻🇺", "WF": "🇼🇫", "WS": "🇼🇸", "YE": "🇾🇪", "YT": "🇾🇹",
    "ZA": "🇿🇦", "ZM": "🇿🇲", "ZW": "🇿🇼"
}

def is_request_allowed(user_id):
    return True

def get_card_info(bin_number):
    response = requests.get(f'https://lookup.binlist.net/{bin_number}')
    if response.status_code == 200:
        return response.json()
    return None

def generate_credit_card_numbers(bin_number):
    card_numbers = []
    for _ in range(10):  # Generate 10 card numbers
        card_number = f"{bin_number}{''.join(random.choices('0123456789', k=16 - len(bin_number)))}"
        month = random.randint(1, 12)
        year = random.randint(24, 30)  # Valid until 2024-2030
        cvv = ''.join(random.choices('0123456789', k=3))
        card_numbers.append(f"{card_number}|{month:02}|20{year}|{cvv}")
    return card_numbers

@bot.message_handler(commands=['gen'])
def generate_cards(message):
    if len(message.text.split()) < 2:
        bot.reply_to(message, '𝐏𝐥𝐞𝐚𝐬𝐞 𝐩𝐫𝐨𝐯𝐢𝐝𝐞 𝐚 𝐁𝐈𝐍 𝐚𝐟𝐭𝐞𝐫 𝐭𝐡𝐞 /gen 𝐜𝐨𝐦𝐦𝐚𝐧𝐝')
        return

    user_id = message.from_user.id
    if not is_request_allowed(user_id):
        bot.reply_to(message, '𝐏𝐥𝐞𝐚𝐬𝐞 𝐰𝐚𝐢𝐭 𝐚 𝐟𝐞𝐰 𝐬𝐞𝐜𝐨𝐧𝐝𝐬 𝐛𝐞𝐟𝐨𝐫𝐞 𝐦𝐚𝐤𝐢𝐧𝐠 𝐚𝐧𝐨𝐭𝐡𝐞𝐫 𝐫𝐞𝐪𝐮𝐞𝐬𝐭')
        return

    bin_number = message.text.split()[1]
    card_numbers = generate_credit_card_numbers(bin_number)
    bin_info = get_card_info(bin_number)

    card_info = (
        f'𝗕𝗜𝗡 ⇾ {bin_number}\n'
        f'𝗔𝗺𝗼𝘂𝗻𝘁 ⇾ 10\n'
        f'<code>\n' + '\n'.join(card_numbers) + '\n</code>\n'
    )

    # Append BIN info if available
    if bin_info:
        scheme = bin_info.get("scheme", "Unknown").upper()
        card_type = bin_info.get("type", "Unknown").upper()
        brand = bin_info.get("brand", "Unknown").upper()
        issuer = bin_info.get("bank", {}).get("name", "Unknown").upper()
        country = bin_info.get("country", {}).get("name", "Unknown").upper()
        country_code = bin_info.get("country", {}).get("alpha2", "Unknown").upper()
        flag = country_flags.get(country_code, "")

        card_info += (
            "𝗜𝗻𝗳𝗼: \n"
            f'{scheme} - {card_type} - {brand}\n'
            f'𝐈𝐬𝐬𝐮𝐞𝐫: {issuer}\n'
            f'𝗖𝗼𝘂𝗻𝘁𝗿𝗬: {country} {flag}\n'
        )
    else:
        card_info += "𝗜𝗻𝗳𝗼: No additional BIN info available.\n"

    bot.reply_to(message, card_info, parse_mode='HTML')

# Welcome message and commands
@bot.message_handler(commands=['start'])
def welcome(message):
    welcome_text = (
        "𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐭𝐨 𝐭𝐡𝐞 𝐁𝐨𝐭! 𝐇𝐞𝐫𝐞 𝐚𝐫𝐞 𝐭𝐡𝐞 𝐜𝐨𝐦𝐦𝐚𝐧𝐝𝐬 𝐲𝐨𝐮 𝐜𝐚𝐧 𝐮𝐬𝐞 👾:\n"
        "/check Url - 𝐂𝐡𝐞𝐜𝐤 𝐝𝐞𝐭𝐚𝐢𝐥𝐬 𝐚𝐛𝐨𝐮𝐭 𝐭𝐡𝐞 𝐬𝐩𝐞𝐜𝐢𝐟𝐢𝐞𝐝 𝐔𝐑𝐋\n"
        "/sk sk_live - 𝐂𝐡𝐞𝐜𝐤 𝐭𝐡𝐞 𝐬𝐤_𝐥𝐢𝐯𝐞 𝐤𝐞𝐲 𝐢𝐧𝐟𝐨𝐫𝐦𝐚𝐭𝐢𝐨𝐧\n"
        "/gen Bin - 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞 𝐜𝐫𝐞𝐝𝐢𝐭 𝐜𝐚𝐫𝐝 𝐧𝐮𝐦𝐛𝐞𝐫𝐬 𝐛𝐚𝐬𝐞𝐝 𝐨𝐧 𝐭𝐡𝐞 𝐁𝐈𝐍\n"
    )
    bot.reply_to(message, welcome_text)

# Start the bot
bot.polling(none_stop=True)