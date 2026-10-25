from app import create_app
import os

app = create_app()

if __name__ == "__main__":
    puerto = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=puerto, debug=True)