import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

players = []

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    keyboard = [
        [InlineKeyboardButton("اضغط هنا للدخول في اللعبة 📥", callback_data="join_game")],
        [InlineKeyboardButton("حباً برسول الله صلوا عليهِ 🩵", callback_data="pray_on_prophet")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"أهلًا بك يا 🕯️ {user.first_name} 🕯️ في لعبة الروليت! 👋\n\n"
        f"💎 تذكير نوراني: لا تنسَ الصلاة على النبي قبل البدء باللعب بالضغط على الزر بالأسفل 👇", 
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    data = query.data

    if data == "pray_on_prophet":
        await query.message.reply_text("اللهم صلِّ وسلم وبارك على سيدنا ونبينا محمد وعلى آله وصحبه أجمعين\n\nجزاك الله خيراً وكسبت الأجر 🩵")
        return

    if data == "join_game":
        if user.id not in [p["id"] for p in players]:
            players.append({"id": user.id, "name": f"🕯️ {user.first_name} 🕯️"})
            
            keyboard = [
                [InlineKeyboardButton("إطلاق الروليت وتحديد الفائز 🎯", callback_data="run_roulette")],
                [InlineKeyboardButton("حباً برسول الله صلوا عليهِ 🩵", callback_data="pray_on_prophet")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.reply_text(f"تم تسجيلك بنجاح في القائمة يا 🕯️ {user.first_name} 🕯️ ✅", reply_markup=reply_markup)
        else:
            await query.message.reply_text(f"أنت مسجل بالفعل في القائمة يا 🕯️ {user.first_name} 🕯️ ⚠️")

async def roulette_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if len(players) < 2:
        await query.message.reply_text("لا يمكن بدء اللعبة، يجب أن ينضم لاعبين أو أكثر! ❌")
        return

    winner = random.choice(players)
    
    await query.message.reply_text(f"🎉 الروليت دار واختار...\n🎯 الفائز هو: {winner[ name ]}")

async def join_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in [p["id"] for p in players]:
        players.append({"id": user.id, "name": f"🕯️ {user.first_name} 🕯️"})
        await update.message.reply_text(f"تم تسجيلك بنجاح يا 🕯️ {user.first_name} 🕯️ ✅")
    else:
        await update.message.reply_text(f"أنت مسجل بالفعل يا 🕯️ {user.first_name} 🕯️ ⚠️")

async def roulette_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(players) < 2:
        await update.message.reply_text("لازم لاعبين أكثر ❌")
        return
    winner = random.choice(players)
    await update.message.reply_text(f"🎯 الفائز: {winner[ name ]}")


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("join", join_command))
app.add_handler(CommandHandler("roulette", roulette_command))

app.add_handler(CallbackQueryHandler(button_handler, pattern="^(join_game|pray_on_prophet)$"))
app.add_handler(CallbackQueryHandler(roulette_callback, pattern="run_roulette"))

app.run_polling()

