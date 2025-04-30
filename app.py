from api import bot
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    bot.run_telegram_bot()

if __name__ == '__main__':
    main()