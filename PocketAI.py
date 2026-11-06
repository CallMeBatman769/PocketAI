import subprocess
import os
import sys
import psutil
import httpx
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

TOKEN = "REPLACE_WITH_YOUR_BOT_TOKEN"

OLLAMA_BASE_URL = "http://localhost:11434/"
MODEL = "gemma4:12b"
MODELS = []

replacements = {
    "NAME": "",
    "ID": "",
    "SIZE": "",
    "MODIFIED": ""
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to PocketAI"
    )

async def question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("No question specified!")
        return

    questi = " ".join(context.args)
    url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/chat"

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": questi
            }
        ],
        "stream": False
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=120)


    response.raise_for_status()

    data = response.json()

    await update.message.reply_text(
        data['message']['content']
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Commands: \n"
        "/models - list every installed model\n"
        "/model <model name> - choose model\n"
        "/stats - computer stats such as RAM and CPU usage\n"
        "/quest <prompt> - sends the prompt to the AI\n"
        "/help - shows this message\n"
    )

async def change_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("No model specified!")
        return 
    if not MODELS:
        await update.message.reply_text("Please run /models first")
        return
    model = context.args[0]

    if not model in MODELS:
        await update.message.reply_text("This model isnt installed")
        return
    global MODEL
    MODEL = model
    await update.message.reply_text("Changed the model!")



async def installed_models(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not MODELS:
        installed = subprocess.run(
            ['ollama', 'ls'],
            capture_output=True,
            text=True,
            shell=True
        )
        temp = []
        msg = installed.stdout
        for old, new in replacements.items():
            msg = msg.replace(old, new)

        for model in msg.splitlines():
            dat = model.split(' ')
            temp.append(dat[0])
        msg = ''
        for model2 in temp:
            if not model2 == "":
                msg += f"{model2}\n"
                MODELS.append(model2)
            else:
                continue

        await update.message.reply_text(
            msg
        )
    else:
        msg = ""
        for model in MODELS:
            msg += f"{model}\n"
        await update.message.reply_text(f"{msg}")

async def pong(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "pong!"
    )

async def PCStats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    memory = psutil.virtual_memory()
    cpu_usage = psutil.cpu_percent(interval=1)


    msg = f"Total RAM: {memory.total / (1024**3):.2f} GB\n"
    msg += f"Used RAM: {memory.used / (1024**3):.2f} GB\n"
    msg += f"Available RAM: {memory.available / (1024**3):.2f} GB\n"
    msg += f"RAM Usage: {memory.percent}%\n"
    msg += f"CPU: {cpu_usage}%"

    await update.message.reply_text(
        msg
    )

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("models", installed_models))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ping", pong))
    app.add_handler(CommandHandler("stats", PCStats))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quest", question))
    app.add_handler(CommandHandler("model", change_model))

    print("[+] PocketAI is running!")
    app.run_polling()

if __name__ == "__main__":
    main()