from app import launch_app

config_mode = "development"  # Deployment mode
app = launch_app(config_mode)

if __name__ == '__main__':
    app.run()
