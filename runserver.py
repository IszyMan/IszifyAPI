from app_config import create_app
from dotenv import load_dotenv


load_dotenv()


app = create_app()

if __name__ == "__main__":
    # gunicorn -w 4 -b 0.0.0.0:7000 'app_config:create_app()'
    app.run(host="0.0.0.0", port=7000)
