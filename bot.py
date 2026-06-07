import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, InlineQueryHandler, ContextTypes

game_sessions = {}

TOKEN = os.getenv("BOT_TOKEN")

def generate_game_text(players_list, target):
    text = f"🎯 روليت عادي 🎯\n\n"
    text += f"👥 المشاركين: {len(players_list)} من أصل {target} مشارك\n"
    
    if len(players_list) == 0:
        text += "🏆 لم يتم اختيار الفائز بعد\n"
    elif len(players_list) < target:
        text += "🏆 لم يتم اختيار الفائز بعد\n\n"
        text += "📜 قائمة المشتركين الحالية:\n"
        for i, p in enumerate(players_list, 1):
            text += f"{i}-Player: {p[ name ]}\n"
    else:
        text += "🏆 اكتمل العدد وتم اختيار الفائز!\n"
    
    return text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    keyboard = [
        [InlineKeyboardButton("5", callback_data="set_5"), InlineKeyboardButton("10", callback_data="set_10"), InlineKeyboardButton("15", callback_data="set_15")],
        [InlineKeyboardButton("20", callback_data="set_20"), InlineKeyboardButton("25", callback_data="set_25"), InlineKeyboardButton("30", callback_data="set_30")],
        [InlineKeyboardButton("35", callback_data="set_35"), InlineKeyboardButton("40", callback_data="set_40"), InlineKeyboardButton("45", callback_data="set_45")],
        [InlineKeyboardButton("50", callback_data="set_50")],
        [InlineKeyboardButton("حباً برسول الله صلوا عليهِ 🩵", callback_data="pray_on_prophet")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"أهلًا بك يا 🕯️ {user.first_name} 🕯️ في لعبة الروليت العادي! 👋\n\n"
        f"اختر عدد المشاركين من الأزرار أدناه لتجهيز جولة جديدة:\n\n"
        f"💎 تذكير نوراني: لا تنسَ الصلاة على النبي قبل البدء باللعب 👇", 
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data

    if data == "pray_on_prophet":
        await query.answer()
        await query.message.reply_text("اللهم صلِّ وسلم وبارك على سيدنا ونبينا محمد وعلى آله وصحبه أجمعين\n\nجزاك الله خيراً وكسبت الأجر 🩵")
        return

    # عندما يختار المسؤول الرقم، يظهر له زر إطلاق الروليت مباشرة بدل زر الدخول
    if data.startswith("set_"):
        await query.answer()
        target = int(data.split("_")[1])
        
        keyboard = [
            [InlineKeyboardButton(f"إطلاق الروليت وتحديد الفائز ({target} مشارك) 🎯", switch_inline_query=f"run_{target}")],
            [InlineKeyboardButton("حباً برسول الله صلوا عليهِ 🩵", callback_data="pray_on_prophet")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(
            f"تم تجهيز الروليت العادي بنجاح 💎\n"
            f"👥 عدد المشتركين المستهدف: {target}\n\n"
            f"اضغط على زر (إطلاق الروليت) بالأسفل لنشرها في قنواتك ومجموعاتك 👇",
            reply_markup=reply_markup
        )
        return

    # هذا الجزء مخصص للمشتركين داخل الجروبات عندما يضغطون على انضمام
    if data.startswith("join_"):
        _, target_str, session_id = data.split("_")
        target = int(target_str)
        
        if session_id not in game_sessions:
            game_sessions[session_id] = []
            
        players_list = game_sessions[session_id]

        if len(players_list) >= target:
            await query.answer("عذراً، اكتمل عدد المشتركين لهذه الجولة! ⚠️", show_alert=True)
            return

        if user.id not in [p["id"] for p in players_list]:
            clean_name = user.first_name.replace("[", "").replace("]", "")
            players_list.append({"id": user.id, "name": clean_name})
            current_len = len(players_list)
            
            if current_len == target:
                await query.answer("اكتمل العدد! جاري اختيار الفائز...", show_alert=True)
                winner = random.choice(players_list)
                
                final_text = (
                    f"🎯 روليت عادي 🎯\n\n"
                    f"👥 المشاركين: {target} من أصل {target} مشارك\n"
                    f"🎉 الروليت دار واختار...\n"
                    f"🎯 الفائز هو: 🕯️ {winner[ name ]} 🕯️\n\n"
                    f"مبروك للفائز وحظاً أوفر للبقية!"
                )
                await query.edit_message_text(text=final_text)
                game_sessions.pop(session_id, None)
            else:
                await query.answer("تم تسجيلك بنجاح! ✅")
                new_text = generate_game_text(players_list, target)
                keyboard = [
                    [InlineKeyboardButton(f"مشاركة ({current_len}) 📥", callback_data=f"join_{target}_{session_id}")],
                    [InlineKeyboardButton("حباً برسول الله صلوا عليهِ 🩵", callback_data="pray_on_prophet")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text=new_text, reply_markup=reply_markup)
        else:
            await query.answer("أنت مسجل بالفعل في هذه الجولة! ⚠️", show_alert=True)

async def inline_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    
    if query.startswith("run_"):
        try:
            target = int(query.split("_")[1])
        except:
            target = 5
    else:
        target = 5

    session_id = str(random.randint(100000, 999999))
    game_sessions[session_id] = []

    results = [
        InlineQueryResultArticle(
            id=session_id,
            title=f"نشر روليت عادي - {target} مشاركين",
            input_message_content=InputTextMessageContent(
                f"🎯 روليت عادي 🎯\n\n"
                f"👥 المشاركين: 0 من أصل {target} مشارك\n"
                f"🏆 لم يتم اختيار الفائز بعد"
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("مشاركة (0) 📥", callback_data=f"join_{target}_{session_id}")],
                [InlineKeyboardButton("حباً برسول الله صلوا عليهِ 🩵", callback_data="pray_on_prophet")]
            ])
        )
    ]
    await update.inline_query.answer(results, cache_time=1)


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler, pattern="^(join_.*|pray_on_prophet|set_.*)$"))
app.add_handler(InlineQueryHandler(inline_query_handler))

app.run_polling()

