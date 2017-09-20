from app import create_instance_of_flask_api

config_mode = config_mode = "development"
app = create_instance_of_flask_api(config_mode)

if __name__ == '__main__':
    app.run()
