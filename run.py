import os
from flasgger import Swagger
from app import create_app


# Initialize flask_api
app = create_app(os.environ.get('FLASK_CONFIG'))

# Initialize swagger documentation plugin
Swagger(app)

if __name__ == '__main__':
    app.run()
