# imports necessary libraries
import logging
import atexit
import json

# imports necessary telegram libraries
from telegram import Update, ForceReply, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, BotCommand, ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

# imports script PerplexityStuff which is used to call the Perplexity API
import PerplexityStuff as PPL

# Most recent news, can be replaced with method echo() by admin, sending a message starting with "NEU:"
current_news = """<b>Was heute wichtig ist</b>

<b>2024 erstes Jahr jenseits der 1,5-Grad-Grenze.</b> Seit Beginn der Aufzeichnungen war das vergangene Jahr das heißeste. Wie mehrere internationale Institutionen mitteilen, lag die globale Durchschnittstemperatur 1,6 Grad über dem vorindustriellen Niveau - und damit erstmals über der im Pariser Klimavertrag vereinbarten Grenze. <a href="https://www.sueddeutsche.de/projekte/artikel/wissen/klimawandel-2024-1-5-grad-extremwetter-el-nino-e307472/">Mehr dazu</a>

<b>Zahl der Todesopfer durch Brände in Kalifornien steigt auf sieben.</b> Die Feuer in Los Angeles sind weiterhin nicht unter Kontrolle. US-Präsident Biden bezeichnet die Brände als die verheerendsten in der Geschichte Kaliforniens. In den Fokus rückt auch das Krisenmanagement der Stadt Los Angeles. <a href="https://www.sueddeutsche.de/panorama/kalifornien-los-angeles-braende-li.3180041">Mehr dazu</a>

<b>Verkündung von Trumps Strafmaß findet statt.</b> Der Supreme Court lehnt einen Eilantrag des baldigen US-Präsidenten und seiner Anwälte ab, die Strafmaßverkündung im Schweigegeld-Prozess findet wie geplant an diesem Freitag statt. Trump hatte mit aller Kraft zu verhindern versucht, dass das Strafmaß vor seiner Vereidigung als Präsident bekannt gegeben wird. <a href="https://www.sueddeutsche.de/politik/usa-news-liveblog-trump-schweigegeld-prozess-urteilsverkuendung-supreme-court-li.3179324">Mehr dazu</a>"""

# int, the user with this ID can change current_news and send it to all subscribers
admin = 0

# string, bot token from botfather (get your own token from https://t.me/BotFather)
token = "your_token"

logger = logging.getLogger(__name__)

# Store bot screaming status
screaming = False

# Users that have subscribed. Loaded from datav1.json on start, saved to datav1.json on stop
subscribers = {}

# executed for every received message that is not a command
def reply(update: Update, context: CallbackContext) -> None:

    text = update.message.text
    user = update.message.from_user.id

    # Print to console
    print(f'{update.message.from_user.first_name} wrote {text}')

    # if the above defined admin sends a message starting with "NEU:", it's saved in the global current_news
    global admin
    if user == admin and text.startswith("NEU:"):
        global current_news
        current_news = text[4:]
        context.bot.send_message(
            update.message.chat_id,
            f"Folgender Text wurde als aktuelle News gespeichert:\n{current_news}",
            # To preserve the markdown, we attach entities (bold, italic...)
            entities=update.message.entities
        )

    # otherwise, whether the user has activated easy language is being checked,
    # the corresponding method in PerplexityStuff is called, passing the question as a parameter,
    # and the answer is sent to the user
    else:
        context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        if user in subscribers.keys() and subscribers[user]['easylan'] == True:
            answer = PPL.getEasyAnswer(current_news, text)
            print(f"EINFACHE Antwort auf die Frage: {text} :\n{answer}")

            context.bot.send_message(
                update.message.chat_id,
                answer,
                # To preserve the markdown, we attach entities (bold, italic...)
                entities=update.message.entities
            )

        else:
            answer = PPL.getAnswer(current_news, text)
            print(f"NORMALE Antwort auf die Frage: {text} :\n{answer}")

            context.bot.send_message(
                update.message.chat_id,
                answer,
                # To preserve the markdown, we attach entities (bold, italic...)
                entities=update.message.entities
            )


# Adds the user ID to the global subscription list "users" and sends a welcome message
def subscribe(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user.id
    firstname = update.message.from_user.first_name
    global subscribers
    if user not in subscribers.keys():
        subscriber = {
            "subscribed": True,
            "easylan": False
        }
        subscribers[user] = subscriber
    context.bot.send_message(
        user,
        f"Hallo {firstname}, danke für dein Abo <3",
        # To preserve the markdown, we attach entities (bold, italic...)
        entities=update.message.entities
    )
    print(f"Nutzer {firstname} aka {user} als neuen Abonnenten hinzugefügt.")


# Removes the user ID from the global subscription list "users" and sends a goodbye message
def unSubscribe(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user.id
    global subscribers
    if user in subscribers.keys():
        subscribers[user]['subscribed'] = False
    context.bot.send_message(
        user,
        f"Wir haben dein Abo beendet.",
        # To preserve the markdown, we attach entities (bold, italic...)
        entities=update.message.entities
    )
    print(f"Abo für User Nummer {user} beendet.")


# Activates easy language for the user. If the user is not in the global subscription list "users", it is added,
# since easy language is a user-specific feature saved within the user database
# sends a message to the user that easy language is activated
def actEasyLan(update: Update, context: CallbackContext):
    user = update.message.from_user.id
    global subscribers
    if user in subscribers.keys():
        subscribers[user]['easylan'] = True
    else:
        subscriber = {
            "subscribed": False,
            "easylan": True
        }
        subscribers[user] = subscriber

    context.bot.send_message(
        user,
        f"Wir haben leichte Sprache aktiviert.",
        entities=update.message.entities
    )
    print(f"Leicht Sprache für User Nummer {user} aktiviert.")


# Deactivates easy language for the user if he has activated it
# if the user is not in the global subscription list "users", which would have been necessary to activate easy language,
# nothing happens
# anywise: sends a message to the user that easy language is deactivated
def deactEasyLan(update: Update, context: CallbackContext):
    user = update.message.from_user.id
    global subscribers
    if user in subscribers.keys():
        subscribers[user]['easylan'] = False

    context.bot.send_message(
        user,
        f"Wir haben leichte Sprache deaktiviert.",
        # To preserve the markdown, we attach entities (bold, italic...)
        entities=update.message.entities
    )
    print(f"Leicht Sprache für User Nummer {user} deaktiviert.")


#    Sends the global current_news to the requesting user
def getLatestNews(update: Update, context: CallbackContext) -> None:
    global current_news
    context.bot.send_message(
        update.message.from_user.id,
        current_news,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
        # To preserve the markdown, we attach entities (bold, italic...)
        entities=update.message.entities
    )


# Sends the global current_news to all user ids in global subscribers if executed by an admin
def sendToSubscribers(update: Update, context: CallbackContext) -> None:
    global admin
    if update.message.from_user.id == admin:
        global subscribers
        global current_news
        for subscriber in subscribers.keys():
            if subscribers[subscriber]["subscribed"]:
                context.bot.send_message(
                    subscriber,
                    current_news,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                    # To preserve the markdown, we attach entities (bold, italic...)
                    entities=update.message.entities
                )


# called when this script is stopped. It saves the global subscriber database
def stopBot():
    global subscribers
    with open('datav1.json', 'w') as f:
        json.dump(subscribers, f)
    print(f"Der Bot wurde beendet und die Abonnenten-Datenbank gespeichert.")

atexit.register(stopBot)


# main function, which starts the bot
def main() -> None:

    # loads the global subscriber database from file datav1.json if it exists
    try:
        global subscribers
        with open('datav1.json', 'r') as f:
            data = json.load(f)
            for key, value in data.items():
                subscribers[int(key)] = value
        print(f"Folgende Abonnenten-Datenbank wurde geladen:\n{subscribers}")
    except:
        print("Fehler beim Laden der Subscriber-Datenbank.")

    # Starts the bot, using the token from the botfather
    global token
    updater = Updater(token)

    # list of commands
    commands = [
        BotCommand("subscribe", "Get Started! Abonniere den Newsletter."),
        BotCommand("unsubscribe", "Beende dein Abo."),
        BotCommand("acteasylan", "Aktiviere leichte Sprache"),
        BotCommand("deacteasylan", "Deaktiviere leichte Sprache"),
        BotCommand("getlatestnews", "Empfange das aktuellste Nachrichten-Update.")

    ]

    # making the commands available
    updater.bot.set_my_commands(commands)

    # Get the dispatcher to register handlers
    # Then, we register each handler and the conditions the update must meet to trigger it
    dispatcher = updater.dispatcher

    # Register commands, connecting them to the respective functions
    dispatcher.add_handler(CommandHandler("subscribe", subscribe))
    dispatcher.add_handler(CommandHandler("unsubscribe", unSubscribe))
    dispatcher.add_handler(CommandHandler("acteasylan", actEasyLan))
    dispatcher.add_handler(CommandHandler("deacteasylan", deactEasyLan))
    dispatcher.add_handler(CommandHandler("getlatestnews", getLatestNews))
    dispatcher.add_handler(CommandHandler("sendtosubscribers", sendToSubscribers))


    # any other message is sent to the reply function
    dispatcher.add_handler(MessageHandler(~Filters.command, reply))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()


if __name__ == '__main__':
    main()