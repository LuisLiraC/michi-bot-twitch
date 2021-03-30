from dotenv import load_dotenv
from bot import Bot

if __name__ == '__main__':
    load_dotenv()
    bot = Bot()
    bot.run()
