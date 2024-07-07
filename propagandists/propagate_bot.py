import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from PIL import Image, ImageDraw, ImageFont
import io
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define conversation states
STICKER, TEXT = range(2)

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
TOKEN = os.getenv("TG_BOT_TOKEN")

def start(update: Update, context):
    update.message.reply_text('Send me a sticker to begin.')
    return STICKER

def handle_sticker(update: Update, context):
    sticker = update.message.sticker
    file = context.bot.get_file(sticker.file_id)
    
    # Download the sticker file
    sticker_file = io.BytesIO()
    file.download(out=sticker_file)
    sticker_file.seek(0)
    
    # Save the sticker in the user's context
    context.user_data['sticker'] = sticker_file
    
    update.message.reply_text('Great! Now send me the text you want to add to the sticker.')
    return TEXT

def handle_text(update: Update, context):
    text = update.message.text
    sticker_file = context.user_data['sticker']
    
    # Open the sticker image
    image = Image.open(sticker_file).convert("RGBA")
    
    # Create a drawing object
    draw = ImageDraw.Draw(image)
    
    # Choose a font (you may need to specify the path to a font file)
    font = ImageFont.truetype("path/to/font.ttf", 24)
    
    # Add text to the image
    draw.text((10, 10), text, font=font, fill=(255, 255, 255, 255))
    
    # Save the new image
    output = io.BytesIO()
    image.save(output, format='PNG')
    output.seek(0)
    
    # Send the new sticker
    update.message.reply_document(output, filename='new_sticker.png')
    
    return ConversationHandler.END

def cancel(update: Update, context):
    update.message.reply_text('Operation cancelled.')
    return ConversationHandler.END

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            STICKER: [MessageHandler(Filters.sticker, handle_sticker)],
            TEXT: [MessageHandler(Filters.text & ~Filters.command, handle_text)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()