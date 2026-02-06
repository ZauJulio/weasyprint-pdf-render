"""Application entry point."""

from dotenv import load_dotenv

load_dotenv()

from app.config import get_config  # noqa: E402
from app.factory import create_app  # noqa: E402

config = get_config()
app = create_app(config)

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
