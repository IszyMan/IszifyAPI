from app_config import create_app
from dotenv import load_dotenv

# from models import Users, subscribe_for_beginner
# from logger import logger


load_dotenv()


app = create_app()


if __name__ == "__main__":
    # gunicorn -w 4 -b 0.0.0.0:7000 'app_config:create_app()'
    # subscribe for existing users
    # with app.app_context():
    #     for user in Users.query.all():
    #         if not user.subscriptions:
    #             logger.info(f"Subscribing user {user.id}")
    #             subscribe_for_beginner(user.id)
    app.run(host="0.0.0.0", port=7000)
