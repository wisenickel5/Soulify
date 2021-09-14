from flask import Flask
from config import Config
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object(Config)

import routes
bootstrap = Bootstrap(app)

if __name__ == "__main__":
    app.run(debug=True)