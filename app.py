import os
from dotenv import load_dotenv
from app import create_app

#carga variables de entorno desde .env
load_dotenv()

app = create_app()


if __name__ == "__main__":
    puerto = int(os.getenv("PORT", "5000"))
    debug_mode = os.getenv("FLASK_DEBUG", "True").lower() in ["true", "1", "t"]
    
    app.run(host="0.0.0.0", port=puerto, debug=debug_mode)
