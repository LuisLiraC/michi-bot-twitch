from dotenv import load_dotenv
from bot import Bot
from tts_engine import TTSEngine
import locale

tts_template = '{} dice {}'
tts_engine = TTSEngine(template=tts_template)

spam_messages = [
    'Te recomiendo instalar la extensión de BetterTTV para que tengas acceso a más emojis BLANKIES blobDance',
    'Si te está gustando el stream por favor deja tu follow, te lo agradeceré muchísimo :D',
    'Puedes usar !c para ver los comandos que puedes usar en el stream',
    'Si tienes una recomendación para el bot es bienvenida GlitchCat',
    'El MichiBot puede leer tus mensajes en audio si le das PejeCoins CoolCat'
]

greeting_message = 'Hola, {}, qué gusto que participes en el stream :D'

# TODO
custom_rewards = {
    # Mensaje en audio
    'a856a173-4859-420f-baf5-fb0e8ae68237': tts_engine.read,
    # 
}

# TODO
default_rewards = {
    '': ''
}

# Time in seconds
spam_time = 60 * 10

if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, 'es_MX')
    load_dotenv()
    bot = Bot(
        spam_time=spam_time,
        spam_messages=spam_messages,
        custom_rewards=custom_rewards,
        tts_engine=tts_engine,
        greeting_message=greeting_message
    )
    bot.run()
