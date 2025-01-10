from flask import Blueprint, render_template, jsonify, current_app
from app.scraper.twitter import TwitterScraper
import json
from bson import json_util
from app.database import get_db

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return render_template('index.html')

@bp.route('/run_scraper')
def run_scraper():
    try:
        scraper = TwitterScraper(
            current_app.config['TWITTER_USERNAME'],
            current_app.config['TWITTER_PASSWORD'],
            None,  # No proxy username
            None   # No proxy password
        )
        record = scraper.get_trending_topics()
        return jsonify({
            "success": True,
            "data": json.loads(json_util.dumps(record))
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })