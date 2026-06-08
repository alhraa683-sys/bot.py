import os
import random
import threading
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, InlineQueryHandler, ContextTypes

# قاموس حفظ الجولات واللاعبين وبيانات منشئ الروليت
game_sessions = {}

# التحقق من وجود التوكن لمنع انهيار السيرفر
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("ERROR: BOT_TOKEN variable is missing from environment!")

# وظيفة ذكية لحذف الجولات القديمة (تنظيف تلقائي للذاكرة كل ساعة)
def auto_clean_old_sessions():
    while True:
        time.sleep(3600)  # فحص كل ساعة
        current_time = time.time()
        expired_ids = [
            sid for sid, session in game_sessions.items()
            if current_time - session.get("created_at", 0) > 86400  # حذف بعد 24 ساعة
        ]
        for sid in expired_ids:
            game_sessions.pop(sid, None)

threading.Thread(target=auto_clean_old_sessions, daemon=True).start()

def generate_game_text(players_list, target):
    text = "🎯 روليت عادي 🎯\n\n"
    text += f"👥 المشاركين: {len(players_list)} من أصل {target} مشارك\n"
    
    if len(players_list) == 0:
        text += "🏆 لم يتم اختيار الفائز بعد\n"
    else:
        text += "🏆 لم يتم اختيار الفائز بعد\n\n"
        text += "📜 قائمة المشتركين الحالية:\n"
        for i, p in enumerate(players_list, 1):
            text += f"{i}-Player: {p[ name ]}\n"
    
    return text

# 1️⃣ القائمة الرئيسية لبدء الروليت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🏆 إنشاء روليت", callback_data="create")],
        [InlineKeyboardButton("حباً برسول الله صلوا عليهِ 🩵", callback_data="pray")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"أهلًا بك يا 🕯️ {user.first_name} 🕯️ في لعبة الروليت العادي! 👋\n\n"
        f"💎 تذكير نوراني: لا تنسَ الصلاة على النبي قبل البدء 👇", 
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data

    if data == "pray":
        await query.answer("اللهم صلِّ وسلم على نبينا محمد 🩵")
        try:
            await query.message.reply_text("اللهم صلِّ وسلم وبارك على سيدنا ونبينا محمد وعلى آله وصحبه أجمعين\n\nجزاك الله خيراً وكسبت الأجر 🩵")
        except:
            pass
        return

    # 2️⃣ قائمة الأرقام للروليت
    if data == "create":
        await query.answer()
        keyboard = [
            [InlineKeyboardButton("5", callback_data="s_5"), InlineKeyboardButton("10", callback_data="s_10"), InlineKeyboardButton("15", callback_data="s_15")],
            [InlineKeyboardButton("20", callback_data="s_20"), InlineKeyboardButton("25", callback_data="s_25"), InlineKeyboardButton("30", callback_data="s_30")],
            [InlineKeyboardButton("35", callback_data="s_35"), InlineKeyboardButton("40", callback_data="s_40"), InlineKeyboardButton("45", callback_data="s_45")],
            [InlineKeyboardButton("50", callback_data="s_50")],
            [InlineKeyboardButton("رجوع ↩️", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="⚙️ اختر عدد المشاركين المطلوب للروليت من الأزرار أدناه:",
            reply_markup=reply_markup
        )
        return

    if data == "back":
        await query.answer()
        keyboard = [
            [InlineKeyboardButton("🏆 إنشاء روليت", callback_data="create")],
            [InlineKeyboardButton("حباً برسول الله صلوا عليهِ 🩵", callback_data="pray")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=f"أهلًا بك يا 🕯️ {user.first_name} 🕯️ في لعبة الروليت العادي! 👋\n\n💎 تذكير نوراني: لا تنسَ الصلاة على النبي قبل البدء 👇",
            reply_markup=reply_markup
        )
        return

    # 3️⃣ زر تحديد العدد وإنشاء الجولة بالذاكرة
    if data.startswith("s_"):
        await query.answer()
        target = int(data.split("_")[1])
        
        session_id = f"{random.randint(1000, 9999)}{int(time.time()) % 100}"
        game_sessions[session_id] = {
            "target": target, 
            "players": [], 
            "creator": user.id,
            "created_at": time.time()
        }
        
        keyboard = [
            [InlineKeyboardButton(f"اضغط هنا لنشر الروليت المحدد ({target} مشارك) 📣", switch_inline_query=f"run_{target}_{session_id}")],
            [InlineKeyboardButton("تعديل العدد ⚙️", callback_data="create")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=f"تم تجهيز الروليت بنجاح 💎\n👥 عدد المشتركين المطلوب: {target}\n\nاضغطي على الزر بالأسفل لنشره مباشرة في قناتك أو مجموعتك 👇",
            reply_markup=reply_markup
        )
        return

    # 4️⃣ زر تدوير العجلة اليدوي لمنشئ الروليت
    if data.startswith("spin_"):
        parts = data.split("_")
        target = int(parts[1])
        session_id = parts[2]
        
        if session_id not in game_sessions:
            await query.answer("عذراً، هذه الجولة انتهت أو غير موجودة! ⚠️", show_alert=True)
            return
            
        session = game_sessions[session_id]
        
        if user.id != session["creator"]:
            await query.answer("عذراً، الشخص الذي أنشأ هذا الروليت فقط هو من يمكنه تدوير العجلة! ⚠️", show_alert=True)
            return
            
        players_list = session["players"]
        
        if len(players_list) == 0:
            await query.answer("لا يمكن تدوير العجلة؛ لا يوجد أي مشتركين حتى الآن! ⚠️", show_alert=True)
            return
            
        await query.answer("جاري تدوير العجلة واختيار الفائز... 🎡")
        winner = random.choice(players_list)
        
        final_text = (
            f"🎯 روليت عادي 🎯\n\n"
            f"👥 المشاركين النهائيين: {len(players_list)} مشارك\n"
            f"🎉 الروليت دار واختار...\n"
            f"🎯 الفائز هو: 🕯️ {winner[ name ]} 🕯️\n\n"
            f"مبروك للفائز وحظاً أوفر للبقية!"
        )
        try:
            await query.edit_message_text(text=final_text)
        except:
            pass
        game_sessions.pop(session_id, None)
        return

    # 5️⃣ زر الاشتراك وتحديث القائمة فوراً
    if data.startswith("j_"):
        parts = data.split("_")
        target = int(parts[1])
        session_id = parts[2]
        
        if session_id not in game_sessions:
            await query.answer("عذراً، هذه الجولة انتهت! ⚠️", show_alert=True)
            return
            
        session = game_sessions[session_id]
        players_list = session["players"]

        if len(players_list) >= target:
            await query.answer("عذراً، اكتمل الحد الأقصى من المشتركين لهذه الجولة! ⚠️", show_alert=True)
            return

        user_ids = [p["id"] for p in players_list]
        if user.id in user_ids:
            await query.answer("أنت مسجل بالفعل في هذه الجولة! ⚠️", show_alert=True)
            return

        clean_name = user.first_name.replace("[", "").replace("]", "")
        players_list.append({"id": user.id, "name": clean_name})
        current_len = len(players_list)
        
        await query.answer("تم تسجيلك بنجاح! ✅")
        
        new_text = generate_game_text(players_list, target)
        
        keyboard = [
            [InlineKeyboardButton(f"مشاركة ({current_len}) 📥", callback_data=f"j_{target}_{session_id}")],
            [InlineKeyboardButton("🎡 تدوير العجلة 🎡", callback_data=f"spin_{target}_{session_id}")],
            [InlineKeyboardButton("حباً برسول الله صلوا عليهِ 🩵", callback_data="pray")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(text=new_text, reply_markup=reply_markup)
        except Exception:
            pass

# 6️⃣ نظام الـ Inline المستقر لمنع مشاكل الكاش
async def inline_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    
    target = 5
    session_id = f"{random.randint(1000, 9999)}{int(time.time()) % 100}"
    
    if query.startswith("run_"):
        parts = query.split("_")
        if len(parts) >= 3:
            try:
                target = int(parts[1])
                session_id = parts[2]
            except:
                pass

    if session_id in game_sessions:
        session = game_sessions[session_id]
        players_list = session["players"]
        target = session["target"]
    else:
        game_sessions[session_id] = {
            "target": target, 
            "players": [], 
            "creator": update.effective_user.id,
            "created_at": time.time()
        }
        players_list = []

    current_len = len(players_list)
    inline_text = generate_game_text(players_list, target)

    results = [
        InlineQueryResultArticle(
            id=session_id,
            title=f"اضغط هنا لنشر الروليت المحدد ({target} مشارك)",
            input_message_content=InputTextMessageContent(inline_text),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"مشاركة ({current_len}) 📥", callback_data=f"j_{target}_{session_id}")],
                [InlineKeyboardButton("🎡 تدوير العجلة 🎡", callback_data=f"spin_{target}_{session_id}")],
                [InlineKeyboardButton("حباً برسول الله صلوا عليهِ 🩵", callback_data="pray")]
            ])
        )
    ]
    try:
        await update.inline_query.answer(results, cache_time=0)
    except:
        pass

# بدء تشغيل التطبيق بالتوكن الصحيح
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler, pattern="^(j_.*|pray|s_.*|create|back|spin_.*)$"))
app.add_handler(InlineQueryHandler(inline_query_handler))

app.run_polling()

