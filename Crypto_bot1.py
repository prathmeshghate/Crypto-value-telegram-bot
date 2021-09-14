#All Required Libraries

import logging
import telegram
import requests
from typing import Dict

from telegram import ReplyKeyboardMarkup, ChatAction, ReplyKeyboardRemove
from telegram.ext import *
from telegram import Update

#All required API

Crypto_API= "9384cde7124d164085755d6178424e6f"
bot_api= "1907053474:AAGKm4m6DidimhDBqcxdSnNGqCbLzIFw_z8"
updater = Updater(token=bot_api, use_context=True)
dispatcher = updater.dispatcher

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


COIN, CURRENCY,PERIOD,DATE = range(4)

def start(update,context): #cmd
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.ChatAction.TYPING)
    update.message.reply_text("Hi, How are you! \nI will give you any crpyto coin's value")
    #context.bot.send_message(chat_id=update.effective_chat.id, text="Getting Started!")
    update.message.reply_sticker("CAACAgUAAxkBAAEC1-dhMQQUhlYh9RiKgy3GctIzo48quwAC0wMAAv42iFWFSlAr-3D7tCAE")
    context.bot.send_message(chat_id=update.effective_chat.id, text="Which coin's value do you want?")

    return COIN

def coin(update, context): #cmd
    context.user_data['coin'] =  update.message.text
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.ChatAction.TYPING)
    update.message.reply_text("In which currency do you want price?",parse_mode=telegram.ParseMode.MARKDOWN_V2)
    
    return CURRENCY

def currency (update, context): #cmd
    context.user_data['currency']= update.message.text
    reply_keyboard = [['Live','Historic']]
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.ChatAction.TYPING)
    update.message.reply_text('Do you want live value or Historic Value?',reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Live or Historic?'
        ))
    

    return PERIOD

def period(update,context): #cmd
    context.user_data['period']=update.message.text
    if context.user_data.get('period')=='Historic':
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.ChatAction.TYPING)
        update.message.reply_text("if you are willing to get a 'HISTORIC VALUE' \n please specify date in YYYY-MM-DD format",
        reply_markup=ReplyKeyboardRemove(),)
        return DATE
    elif context.user_data.get('period')=='Live':
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.ChatAction.TYPING)
        update.message.reply_text("Value of your coin is "+str(coin_value(context.user_data)),
        reply_markup=ReplyKeyboardRemove(),)

        return ConversationHandler.END
        #return coin_value(context.user_data)
    

def date(update,context): #cmd
    context.user_data['date']=update.message.text
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.ChatAction.TYPING)
    update.message.reply_text('Value of your coin is : '+str(coin_value(context.user_data)))

    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int: #cmd
    """Cancels and ends the conversation."""
    user = update.message.from_user
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.ChatAction.TYPING)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.'
    )
    update.message.reply_sticker("CAACAgIAAxkBAAEC1-lhMQdS4PGFd0xShVTEBOldBwcbjwACQQMAAnlc4gl8tCkyAAEOsb8gBA")

    return ConversationHandler.END

#Function which will fetch the coins value

def coin_value(user_data): #func
    if user_data.get('period')== 'Live':
        response=requests.get('http://api.coinlayer.com/live?access_key='+Crypto_API,params={'symbols':user_data.get('coin'),'target':user_data.get('currency',"Invalid Currency")})
    
        price_coin=response.json()['rates'][user_data.get('coin')]

        return price_coin
    else:
        response1=requests.get('http://api.coinlayer.com/'+str(user_data.get('date'))+'?access_key='+Crypto_API,
        params={'symbols':user_data.get('coin'),'target':user_data.get('currency')})
        price_coin1=response1.json()['rates'][user_data.get('coin')]
        return price_coin1
        
    
# Telegram bot conversation handler

conv_handler= ConversationHandler( 
    entry_points=[CommandHandler('start',start)],
    states={
        COIN : [MessageHandler(Filters.text & ~Filters.command ,coin)],
        CURRENCY : [MessageHandler(Filters.text & ~Filters.command, currency )],
        PERIOD : [MessageHandler(Filters.regex('^(Live|Historic)$') & ~Filters.command,period)],
        DATE : [MessageHandler(Filters.text & ~Filters.command,date)]

    },
    fallbacks=[CommandHandler('cancel', cancel)],
    )

dispatcher.add_handler(conv_handler)


updater.start_polling(1.0)
updater.idle()