from flask import Flask
from app.config import Config
from app.database import init_db
from app.scraper.twitter import TwitterScraper

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database
    init_db(app)
    
    # Initialize scraper
    scraper = TwitterScraper(
        app.config['TWITTER_USERNAME'],
        app.config['TWITTER_PASSWORD'],
        None,  # No proxy username
        None   # No proxy password
    )
    
    # Register routes
    from app.routes import bp
    app.register_blueprint(bp)
    
    return app