from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import threading

# Replace 'YOUR_BOT_TOKEN' with the actual token obtained from the BotFather
TOKEN = '6892540965:AAGrBdHwQcnWtCQBQsPrfCT9m4B7wA5IKU8'

# Dictionary to store user-specific deletion intervals (in seconds)
user_intervals = {}

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Bot is Alive! The Messages Below will be deleted in 30 minutes')

def delete_message(update: Update, context: CallbackContext) -> None:
    message = update.message
    chat_id = message.chat_id
    message_id = message.message_id

    # Get the deletion interval for the current user, default to 30 minutes
    interval_seconds = user_intervals.get(chat_id, 1800)

    # Schedule the message deletion after the specified interval
    job = context.job_queue.run_once(lambda ctx: delete_scheduled_message(ctx, chat_id, message_id), interval_seconds)
    context.chat_data['job'] = job

def delete_scheduled_message(context: CallbackContext, chat_id: int, message_id: int) -> None:
    context.bot.delete_message(chat_id=chat_id, message_id=message_id)

def set_timer(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    try:
        # Get the timer value in minutes from the user's message
        timer_minutes = int(context.args[0])

        # Validate timer value
        if timer_minutes <= 0:
            raise ValueError("Timer value must be greater than zero.")

        # Convert minutes to seconds
        timer_seconds = timer_minutes * 60

        # Store the timer for the current chat
        user_intervals[chat_id] = timer_seconds

        # Schedule the message deletion after the specified interval
        job = context.job_queue.run_once(lambda ctx: delete_scheduled_message(ctx, chat_id, update.message.message_id), timer_seconds)
        context.chat_data['job'] = job

        update.message.reply_text(f'Timer set to {timer_minutes} minutes. Messages will be deleted after this interval.')
    except (IndexError, ValueError):
        update.message.reply_text('Please provide a valid timer value in minutes (greater than zero).')

def main() -> None:
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.all, delete_message))
    dp.add_handler(CommandHandler("settimer", set_timer, pass_args=True))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
