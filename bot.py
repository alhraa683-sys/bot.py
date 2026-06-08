import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, InlineQueryHandler, ContextTypes

# قاموس حفظ الجولات واللاعبين وبيانات منشئ الروليت
game_sessions = {}

TOKEN = os.getenv("BOT_TOKEN")

def generate_game_text(players_list, target):
    text = f"🎯 روليت عادي 🎯\n\n"
    text += f"👥 المشاركين: {len(players_list)} من أصل {target} مشارك\n"
    
    if len(players_list) == 0:
        text += "🏆 لم يتم اختيار الفائز بعد\n"
    else:
        text += "🏆 لم يتم اختيار الفائز بعد\n\n"
        text += "📜 قائمة المشتركين الحالية:\n"
        for i, p in enumerate(players_list, 1):
            text += f"{i}-Player: {p['name']}\n"
    
    return text

# 1️⃣ القائمة الرئيسية لبدء المسابقة
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🏆 إنشاء مسابقة", callback_data="create")],
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
        await query.message.reply_text("اللهم صلِّ وسلم وبارك على سيدنا ونبينا محمد وعلى آله وصحبه أجمعين\n\nجزاك الله خيراً وكسبت الأجر 🩵")
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
            [InlineKeyboardButton("🏆 إنشاء مسابقة", callback_data="create")],
            [InlineKeyboardButton("حباً برسول الله صلوا عليهِ 🩵", callback_data="pray")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=f"أهلًا بك يا 🕯️ {user.first_name} 🕯️ في لعبة الروليت العادي! 👋\n\n💎 تذكير نوراني: لا تنسَ الصلاة على النبي قبل البدء 👇",
            reply_markup=reply_markup
        )
        return

    # 3️⃣ زر تحديد العدد (هنا نلتقط الشخص الذي أنشأ الروليت وصنع الجولة فعلياً)
    if data.startswith("s_"):
        await query.answer()
        target = int(data.split("_")[1])
        
        session_id = str(random.randint(100000, 999999))
        # حفظ معرف المستخدم الحالي (الذي يضغط على الأرقام ويصنع الروليت) كمنشئ رئيسي للجولة
        game_sessions[session_id] = {"target": target, "players": [], "creator": user.id}
        
        keyboard = [
            [InlineKeyboardButton(f"اضغط هنا لنشر الروليت المحدد ({target} مشارك) 📣", switch_inline_query=f"run_{target}_{session_id}")],
            [InlineKeyboardButton("تعديل العدد ⚙️", callback_data="create")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=f"تم تجهيز الروليت بنجاح 💎\n👥 عدد المشتركين: {target}\n\nاضغطي على الزر بالأسفل لنشره مباشرة في قناتك أو مجموعتك 👇",
            reply_markup=reply_markup
        )
        return

    # 4️⃣ زر تدوير العجلة اليدوي (يتحقق بدقة من منشئ الروليت الحالي)
    if data.startswith("spin_"):
        parts = data.split("_")
        target = int(parts[1])
        session_id = parts[2]
        
        if session_id not in game_sessions:
            await query.answer("عذراً، هذه الجولة انتهت أو غير موجودة! ⚠️", show_alert=True)
            return
            
        session = game_sessions[session_id]
        
        # التحقق: هل الشخص الذي يضغط على "تدوير" هو نفسه منشئ هذا الروليت؟
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
            f"👥 المشاركين: {len(players_list)} مشارك\n"
            f"🎉 الروليت دار واختار...\n"
            f"🎯 الفائز هو: 🕯️ {winner['name']} 🕯️\n\n"
            f"مبروك للفائز وحظاً أوفر للبقية!"
        )
        await query.edit_message_text(text=final_text)
        game_sessions.pop(session_id, None)
        return

    # 5️⃣ معالجة ضغط زر الاشتراك "مشاركة"
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

        # إضافة المشترك الجديد بنجاح
        clean_name = user.first_name.replace("[", "").replace("]", "")
        players_list.append({"id": user.id, "name": clean_name})
        current_len = len(players_list)
        
        await query.answer("تم تسجيلك بنجاح! ✅")
        new_text = generate_game_text(players_list, target)
        
        # الأزرار في القناة تشمل زر "تدوير العجلة"
        keyboard = [
            [InlineKeyboardButton(f"مشاركة ({current_len}) 📥", callback_data=f"j_{target}_{session_id}")],
            [InlineKeyboardButton("🎡 تدوير العجلة 🎡", callback_data=f"spin_{target}_{session_id}")],
            [InlineKeyboardButton("حباً برسول الله صلوا عليهِ 🩵", callback_data="pray")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=new_text, reply_markup=reply_markup)

# نظام الـ Inline المستقر والمبني على المعرف الثابت
async def inline_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    
    target = 5
    session_id = str(random.randint(100000, 999999))
    
    if query.startswith("run_"):
        parts = query.split("_")
        if len(parts) >= 3:
            try:
                target = int(parts[1])
                session_id = parts[2]
            except:
                pass

    # إذا لم تكن الجولة منشأة مسبقاً بالذاكرة (حالة نادرة جداً)، ننشئها ونحفظ من فتحها كمنشئ احتياطي
    if session_id not in game_sessions:
        game_sessions[session_id] = {"target": target, "players": [], "creator": update.effective_user.id}

    results = [
        InlineQueryResultArticle(
            id=session_id,
            title=f"اضغط هنا لنشر الروليت المحدد ({target} مشارك)",
            input_message_content=InputTextMessageContent(
                f"🎯 روليت عادي 🎯\n\n"
                f"👥 المشاركين: 0 من أصل {target} مشارك\n"
                f"🏆 لم يتم اختيار الفائز بعد"
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("مشاركة (0) 📥", callback_data=f"j_{target}_{session_id}")],
                [InlineKeyboardButton("🎡 تدوير العجلة 🎡", callback_data=f"spin_{target}_{session_id}")],
                [InlineKeyboardButton("حباً برسول الله صلوا عليهِ 🩵", callback_data="pray")]
            ])
        )
    ]
    await update.inline_query.answer(results, cache_time=0)


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler, pattern="^(j_.*|pray|s_.*|create|back|spin_.*)$"))
app.add_handler(InlineQueryHandler(inline_query_handler))

app.run_polling()
