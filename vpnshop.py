import telebot
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8167900941:AAEDWMYSQXMAyNJ1086S9eadlu__OAZmz-I"  # 🔹 توکن ربات تلگرام را اینجا جای‌گذاری کنید
ZIBAL_PAYMENT_URL = "https://www.zibal.ir/startpay/67c9b1866f380300133a3a47"  # 🔹 لینک درگاه پرداخت زیبال را وارد کنید

bot = telebot.TeleBot(TOKEN)
users = {}

# ✅ لیست کانفیگ‌ها و قیمت‌ها
CONFIG_PLANS = {
    "1M_30GB": {"size": "30GB", "duration": "30", "price": 100000},
    "1M_50GB": {"size": "50GB", "duration": "30", "price": 130000},
    "1M_Unlimited": {"size": "نامحدود گیمینگ", "duration": "30", "price": 190000},
    "2M_65GB": {"size": "65GB", "duration": "60", "price": 210000},
    "2M_75GB": {"size": "75GB", "duration": "60", "price": 260000},
    "2M_95GB": {"size": "95GB", "duration": "60", "price": 290000},
    "3M_20GB": {"size": "20GB", "duration": "90", "price": 120000},
    "3M_45GB": {"size": "45GB", "duration": "90", "price": 180000}
}

# 🏠 منوی اصلی
def main_menu():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("🛒 خرید کانفیگ", callback_data="buy"),
        InlineKeyboardButton("📦 سفارشات من", callback_data="orders"),
        InlineKeyboardButton("💳 پرداخت", callback_data="payment"),
        InlineKeyboardButton("📈 موجودی من", callback_data="wallet_balance"),
        InlineKeyboardButton("ℹ️ راهنما", callback_data="help")
    )
    return markup

# 📋 منوی انتخاب کانفیگ
def config_menu():
    markup = InlineKeyboardMarkup()
    for key, plan in CONFIG_PLANS.items():
        markup.add(InlineKeyboardButton(f"{plan['size']} - {plan['duration']} روز - {plan['price']} تومان", callback_data=f"select_{key}"))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    users[message.chat.id] = {"orders": []}
    bot.send_message(message.chat.id, "🔹 اولین فروشنده کانفیگ v2rayssh  در ایران!", parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(commands=['wallet_balance'])
def wallet_balance(message):
    chat_id = message.chat.id
    # فرض کنید موجودی کاربر را 100 هزار تومان فرض کردیم
    balance = 100000
    bot.send_message(chat_id, f"💸 موجودی شما: *{balance} تومان*", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "buy":
        bot.send_message(chat_id, "📋 لطفاً یکی از کانفیگ‌های زیر را انتخاب کنید:", reply_markup=config_menu())
    elif call.data.startswith("select_"):
        plan_key = call.data.split("_")[1]
        if plan_key in CONFIG_PLANS:
            plan = CONFIG_PLANS[plan_key]
            users[chat_id]["selected_plan"] = plan_key
            bot.send_message(chat_id, f"✅ *شما این کانفیگ را انتخاب کردید:*\n💾 حجم: *{plan['size']}*\n⏳ مدت اعتبار: *{plan['duration']} روز*\n💰 قیمت: *{plan['price']} تومان*\n💳 برای پرداخت، دکمه پرداخت را بزنید!", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("💳 پرداخت", callback_data="payment")))

            # هشدار هزینه
            if plan["price"] == 100000:
                bot.send_message(chat_id, "⚠️ هزینه این کانفیگ 100,000 تومان است!", parse_mode="Markdown")
                
    elif call.data == "payment":
        if "selected_plan" in users[chat_id]:
            bot.send_message(chat_id, f"💳 *برای تکمیل خرید، لطفاً پرداخت را انجام دهید:*\n{ZIBAL_PAYMENT_URL}", parse_mode="Markdown")
            users[chat_id]["paid"] = True
    elif call.data == "orders":
        orders = users.get(chat_id, {}).get("orders", [])
        orders_text = "\n".join(orders) if orders else "📦 شما سفارشی ثبت نکرده‌اید."
        bot.send_message(chat_id, f"📦 *سفارشات شما:*\n{orders_text}", parse_mode="Markdown")
    elif call.data == "help":
        bot.send_message(chat_id, "ℹ️ *راهنمای خرید کانفیگ:*\n1️⃣ دکمه `🛒 خرید کانفیگ` را بزنید.\n2️⃣ یکی از پلن‌های موجود را انتخاب کنید.\n3️⃣ پس از انتخاب، دکمه `💳 پرداخت` را بزنید.\n4️⃣ بعد از پرداخت، کانفیگ را دریافت کنید!", parse_mode="Markdown")

@bot.message_handler(func=lambda message: users.get(message.chat.id, {}).get("paid", False))
def send_config(message):
    chat_id = message.chat.id
    plan_key = users[chat_id].get("selected_plan")
    if plan_key and plan_key in CONFIG_PLANS:
        config_file = "config.txt"  # 🔹 این فایل باید شامل اطلاعات کانفیگ باشد
        with open(config_file, "rb") as file:
            bot.send_document(chat_id, file, caption=f"✅ *کانفیگ شما با موفقیت ساخته شد!*\n💾 حجم: *{CONFIG_PLANS[plan_key]['size']}*\n⏳ مدت اعتبار: *{CONFIG_PLANS[plan_key]['duration']} روز*", parse_mode="Markdown")
        users[chat_id]["paid"] = False

bot.polling()
