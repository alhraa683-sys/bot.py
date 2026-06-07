import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, InlineQueryHandler, ContextTypes

players = []
TARGET_COUNT = 5

TOKEN = os.getenv("BOT_TOKEN")

def generate_game_text(current_players, target):
    text = f"🎯 روليت عادي 🎯\n\n"
    text += f"👥 المشاركين: {len(current_players)} من أصل {target} مشارك\n"
    
    if len(current_players) == 0:
        text += "🏆 لم يتم اختيار الفائز بعد\n"
    elif len(current_players) < target:
        text += "🏆 لم يتم اختيار الفائز بعد\n\n"
        text += "📜 قائمة المشتركين الحالية:\n"
        for i, p in enumerate(current_players, 1):
            text += f"{i}-Player: {p[ name ]}\n"
    else:
        text += "🏆 اكتمل العدد وتم اختيار الفائز!\n"
    
    return text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    global players
    players.clear()
    
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
        f"اختر عدد المشاركين من الأزرار أدناه:\n\n"
        f"💎 تذكير نوراني: لا تنسَ الصلاة على النبي قبل البدء باللعب 👇", 
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data
    global TARGET_COUNT, players

    if data == "pray_on_prophet":
        await query.answer()
        await query.message.reply_text("اللهم صلِّ وسلم وبارك على سيدنا ونبينا محمد وعلى آله وصحبه أجمعين\n\nجزاك الله خيراً وكسبت الأجر 🩵")
        return

    if data.startswith("set_"):
        await query.answer()
        TARGET_COUNT = int(data.split("_")[1])
        players.clear() 
        
        keyboard = [
            [InlineKeyboardButton(f"اضغط هنا لنشر الروليت المحدد ({TARGET_COUNT} مشارك) 📣", switch_inline_query=f"run_{TARGET_COUNT}")],
            [InlineKeyboardButton("حباً برسول الله صلوا عليهِ 🩵", callback_data="pray_on_prophet")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(
            f"تم تجهيز الروليت العادي 🎯\n"
            f"👥 عدد المشتركين المطلوب: {TARGET_COUNT}\n\n"
            f"اضغطي على الزر بالأسفل لإرسال اللعبة إلى الجروبات والقنوات:",
            reply_markup=reply_markup
        )
        return

    if data == "join_game":
        if len(players) >= TARGET_COUNT:
            await query.answer("عذراً، اكتمل عدد المشتركين لهذه الجولة! ⚠️", show_alert=True)
            return

        if user.id not in [p["id"] for p in players]:
            clean_name = user.first_name.replace("[", "").replace("]", "")
            players.append({"id": user.id, "name": clean_name})
            current_len = len(players)
            
            if current_len == TARGET_COUNT:
                await query.answer("اكتمل العدد! جاري اختيار الفائز...", show_alert=True)
                winner = random.choice(players)
                
                final_text = (
                    f"🎯 روليت عادي 🎯\n\n"
                    f"👥 المشاركين: {TARGET_COUNT} من أصل {TARGET_COUNT} مشارك\n"
                    f"🎉 الروليت دار واختار...\n"
                    f"🎯 الفائز هو: 🕯️ {winner[ name ]} 🕯️\n\n"
                    f"مبروك للفائز وحظاً أوفر للبقية!"
                )
                await query.edit_message_text(text=final_text)
                players.clear() 
            else:
                await query.answer("تم تسجيلك بنجاح! ✅")
                new_text = generate_game_text(players, TARGET_COUNT)
                keyboard = [
                    [InlineKeyboardButton(f"مشاركة ({current_len}) 📥", callback_data="join_game")],
                    [InlineKeyboardButton("حباً برسول الله صلوا عليهِ 🩵", callback_data="pray_on_prophet")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text=new_text, reply_markup=reply_markup)
        else:
            await query.answer("أنت مسجل بالفعل في هذه الجولة! ⚠️", show_alert=True)

async def inline_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    global TARGET_COUNT, players
    
    if query.startswith("run_"):
        try:
            TARGET_COUNT = int(query.split("_")[1])
        except:
            TARGET_COUNT = 5
    else:
        TARGET_COUNT = 5

    players.clear()

    results = [
        InlineQueryResultArticle(
            id=str(random.randint(10000, 99999)),
            title=f"نشر روليت عادي - {TARGET_COUNT} مشاركين",
            input_message_content=InputTextMessageContent(
                f"🎯 روليت عادي 🎯\n\n"
                f"👥 المشاركين: 0 من أصل {TARGET_COUNT} مشارك\n"
                f"🏆 لم يتم اختيار الفائز بعد"
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("مشاركة (0) 📥", callback_data="join_game")],
                [InlineKeyboardButton("حباً برسول الله صلوا عليهِ 🩵", callback_data="pray_on_prophet")]
            ])
        )
    ]
    await update.inline_query.answer(results, cache_time=1)


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler, pattern="^(join_game|pray_on_prophet|set_.*)$"))
app.add_handler(InlineQueryHandler(inline_query_handler))

app.run_polling()

