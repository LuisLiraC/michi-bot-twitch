from dotenv import load_dotenv
from bot import Bot
import locale

if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, 'es_MX')
    load_dotenv()
    bot = Bot()
    bot.run()
