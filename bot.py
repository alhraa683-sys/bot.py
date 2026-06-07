import os
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

players = []

TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلًا 👋 اكتب /join للدخول")


async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id not in [p["id"] for p in players]:
        players.append({"id": user.id, "name": user.first_name})
        await update.message.reply_text("تم تسجيلك ✅")
    else:
        await update.message.reply_text("أنت مسجل بالفعل ⚠️")


async def roulette(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(players) < 2:
        await update.message.reply_text("لازم لاعبين أكثر ❌")
        return

    winner = random.choice(players)

    await update.message.reply_text(f"🎯 الفائز: {winner[ name ]}")


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("join", join))
app.add_handler(CommandHandler("roulette", roulette))

app.run_polling()
  
