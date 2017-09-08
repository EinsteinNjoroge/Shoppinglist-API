from app import create_instance_of_flask_api

config_name = config_name = "development"
app = create_instance_of_flask_api(config_name)

if __name__ == '__main__':
    app.run()
