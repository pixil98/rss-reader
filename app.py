from flask import Flask, render_template, request
from feeds import fetch_articles
from datetime import datetime
from werkzeug.middleware.proxy_fix import ProxyFix
import os

app = Flask(__name__)
if os.getenv("FLASK_PROXY", 'False').lower() in ('true', '1', 't'):
    app.logger.info("loading proxy fix")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

@app.route('/')
def index():
    # Fetch articles from the feeds
    articles = fetch_articles()
    articles.sort(key=lambda x: x["timestamp"], reverse=True)

    # Get unique sources for the filter dropdown
    sources = sorted(set(article["source"] for article in articles))
    
    # Get filter values from the request
    selected_source = request.args.get('source', '')
    selected_start_date = request.args.get('start_date', '')
    selected_end_date = request.args.get('end_date', '')

    # Apply filtering if any filter is selected
    filtered_articles = articles
    
    if selected_source:
        filtered_articles = [article for article in filtered_articles if article["source"] == selected_source]
    
    if selected_start_date:
        try:
            start_date_obj = datetime.strptime(selected_start_date, '%Y-%m-%d')
            filtered_articles = [article for article in filtered_articles if article["timestamp"].date() >= start_date_obj.date()]
        except ValueError:
            pass  # Ignore invalid date formats and show all articles
    
    if selected_end_date:
        try:
            end_date_obj = datetime.strptime(selected_end_date, '%Y-%m-%d')
            filtered_articles = [article for article in filtered_articles if article["timestamp"].date() <= end_date_obj.date()]
        except ValueError:
            pass  # Ignore invalid date formats and show all articles
    
    # Render the template with filtered articles and filter selections
    return render_template('index.html', articles=filtered_articles, sources=sources, 
                           selected_source=selected_source, selected_start_date=selected_start_date, 
                           selected_end_date=selected_end_date)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=os.getenv("FLASK_DEBUG", 'False').lower() in ('true', '1', 't'))
