import os
import random
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, InlineQueryHandler

# جلب التوكن وإعدادات السيرفر
TOKEN = os.getenv("BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL") # هذا متغير يوفره ريندر تلقائياً لرابط موقعك

if not TOKEN:
    raise ValueError("ERROR: BOT_TOKEN is missing!")

# إنشاء تطبيق التليجرام
telegram_app = Application.builder().token(TOKEN).build()

# إنشاء سيرفر Flask
app_flask = Flask(__name__)

# قاموس حفظ الجولات
game_sessions = {}

def generate_game_text(players_list, target):
    text = "🎯 روليت عادي 🎯\n\n"
    text += f"👥 المشاركين: {len(players_list)} من أصل {target} مشارك\n"
    text += "🏆 لم يتم اختيار الفائز بعد\n\n"
    if len(players_list) > 0:
        text += "📜 قائمة المشتركين الحالية:\n"
        for i, p in enumerate(players_list, 1):
            text += f"{i}-Player: {p[ name ]}\n"
    return text

# ---Handlers---
async def start(update: Update, context):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🏆 إنشاء روليت", callback_data="create")],
        [InlineKeyboardButton("حباً برسول الله صلوا عليهِ 🩵", callback_data="pray")]
    ]
    await update.message.reply_text(
        f"أهلًا بك يا 🕯️ {user.first_name} 🕯️ في لعبة الروليت العادي! 👋\n\n💎 لا تنسَ الصلاة على النبي قبل البدء 👇", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context):
    query = update.callback_query
    user = query.from_user
    data = query.data

    if data == "pray":
        await query.answer("اللهم صلِّ وسلم على نبينا محمد 🩵")
        try: await query.message.reply_text("اللهم صلِّ وسلم وبارك على نبينا محمد وعلى آله وصحبه أجمعين 🩵")
        except: pass
        return

    if data == "create":
        await query.answer()
        keyboard = [
            [InlineKeyboardButton("5", callback_data="s_5"), InlineKeyboardButton("10", callback_data="s_10"), InlineKeyboardButton("15", callback_data="s_15")],
            [InlineKeyboardButton("20", callback_data="s_20"), InlineKeyboardButton("25", callback_data="s_25"), InlineKeyboardButton("30", callback_data="s_30")],
            [InlineKeyboardButton("50", callback_data="s_50")],
            [InlineKeyboardButton("رجوع ↩️", callback_data="back")]
        ]
        await query.edit_message_text(text="⚙️ اختر عدد المشاركين المطلوب للروليت:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data == "back":
        await query.answer()
        keyboard = [[InlineKeyboardButton("🏆 إنشاء روليت", callback_data="create")], [InlineKeyboardButton("حباً برسول الله صلوا عليهِ 🩵", callback_data="pray")]]
        await query.edit_message_text(text=f"أهلًا بك في لعبة الروليت العادي! 👋\n\n💎 لا تنسَ الصلاة على النبي قبل البدء 👇", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("s_"):
        await query.answer()
        target = int(data.split("_")[1])
        session_id = f"{random.randint(1000, 9999)}"
        game_sessions[session_id] = {"target": target, "players": [], "creator": user.id}
        
        keyboard = [
            [InlineKeyboardButton(f"اضغط هنا لنشر الروليت المحدد ({target} مشارك) 📣", switch_inline_query=f"run_{target}_{session_id}")],
            [InlineKeyboardButton("تعديل العدد ⚙️", callback_data="create")]
        ]
        await query.edit_message_text(text=f"تم تجهيز الروليت بنجاح 💎\n👥 العدد المطلوب: {target}", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("spin_"):
        parts = data.split("_")
        target, session_id = int(parts[1]), parts[2]
        if session_id not in game_sessions:
            await query.answer("عذراً، هذه الجولة انتهت! ⚠️", show_alert=True)
            return
        session = game_sessions[session_id]
        if user.id != session["creator"]:
            await query.answer("منشئ الروليت فقط هو من يمكنه تدوير العجلة! ⚠️", show_alert=True)
            return
        if len(session["players"]) == 0:
            await query.answer("لا يوجد أي مشتركين حتى الآن! ⚠️", show_alert=True)
            return
        await query.answer("جاري تدوير العجلة... 🎡")
        winner = random.choice(session["players"])
        await query.edit_message_text(text=f"🎯 روليت عادي 🎯\n\n🎉 الفائز هو: 🕯️ {winner[ name ]} 🕯️\n\nمبروك للفائز!")
        game_sessions.pop(session_id, None)
        return

    if data.startswith("j_"):
        parts = data.split("_")
        target, session_id = int(parts[1]), parts[2]
        if session_id not in game_sessions:
            await query.answer("عذراً، هذه الجولة انتهت! ⚠️", show_alert=True)
            return
        session = game_sessions[session_id]
        if len(session["players"]) >= target:
            await query.answer("اكتمل الحد الأقصى! ⚠️", show_alert=True)
            return
        if user.id in [p["id"] for p in session["players"]]:
            await query.answer("أنت مسجل بالفعل! ⚠️", show_alert=True)
            return
        
        session["players"].append({"id": user.id, "name": user.first_name.replace("[", "").replace("]", "")})
        current_len = len(session["players"])
        await query.answer("تم تسجيلك بنجاح! ✅")
        
        keyboard = [
            [InlineKeyboardButton(f"مشاركة ({current_len}) 📥", callback_data=f"j_{target}_{session_id}")],
            [InlineKeyboardButton("🎡 تدوير العجلة 🎡", callback_data=f"spin_{target}_{session_id}")],
            [InlineKeyboardButton("حباً برسول الله صلوا عليهِ 🩵", callback_data="pray")]
        ]
        try: await query.edit_message_text(text=generate_game_text(session["players"], target), reply_markup=InlineKeyboardMarkup(keyboard))
        except: pass

async def inline_query_handler(update: Update, context):
    query = update.inline_query.query
    target, session_id = 5, f"{random.randint(1000, 9999)}"
    if query.startswith("run_"):
        parts = query.split("_")
        if len(parts) >= 3: target, session_id = int(parts[1]), parts[2]

    if session_id not in game_sessions:
        game_sessions[session_id] = {"target": target, "players": [], "creator": update.effective_user.id}
    
    session = game_sessions[session_id]
    current_len = len(session["players"])
    
    results = [
        InlineQueryResultArticle(
            id=session_id,
            title=f"نشر روليت ({target} مشارك)",
            input_message_content=InputTextMessageContent(generate_game_text(session["players"], target)),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"مشاركة ({current_len}) 📥", callback_data=f"j_{target}_{session_id}")],
                [InlineKeyboardButton("🎡 تدوير العجلة 🎡", callback_data=f"spin_{target}_{session_id}")],
                [InlineKeyboardButton("حباً برسول الله صلوا عليهِ 🩵", callback_data="pray")]
            ])
        )
    ]
    try: await update.inline_query.answer(results, cache_time=0)
    except: pass

# ربط الـ Handlers بالتطبيق
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button_handler, pattern="^(j_.*|pray|s_.*|create|back|spin_.*)$"))
telegram_app.add_handler(InlineQueryHandler(inline_query_handler))

# مسارات سيرفر Flask
@app_flask.route( / )
def index():
    return "Bot Webhook Server is Live!"

@app_flask.route(f /{TOKEN} , methods=[ POST ])
def webhook():
    # استقبال الرسائل القادمة من التليجرام وتمريرها للمكتبة لتعالجها بشكل منفصل وأنيق
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), telegram_app.bot)
        asyncio.run(telegram_app.process_update(update))
    return "OK", 200

# تشغيل البوت وربطه بالـ Webhook عند بدء السيرفر
async def setup_webhook():
    await telegram_app.initialize()
    if RENDER_URL:
        url = f"{RENDER_URL.rstrip( / )}/{TOKEN}"
        await telegram_app.bot.set_webhook(url=url)
        print(f"Webhook set to: {url}")

# تنفيذ الـ Setup قبل بدء تشغيل Flask
try:
    asyncio.run(setup_webhook())
except Exception as e:
    print(f"Webhook setup failed: {e}")

if __name__ ==  __main__ :
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host= 0.0.0.0 , port=port)

