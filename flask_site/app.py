from flask import Flask, url_for
from threading import Thread
from dotenv import load_dotenv
import os, logging
load_dotenv()

app = Flask('')
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.ERROR)

@app.route('/')
def index():
    return """
<h1>RoastBot</h1>
<p>RoastBot is currently up and running as it should!</p>
<a href="https://discord.gg/bUtcDMnHcu">Click here to join the Discord Server</a>
"""

@app.errorhandler(404)
def page_not_found(error):
    return """
<!doctype html>
<html lang=en>
<head>
<title>Redirecting...</title>
<meta http-equiv="Refresh" content="2; url='{0}'" />
</head><body>
<h1>Redirecting...</h1>
<p>You should be redirected automatically to the target URL: <a href="{0}">{0}</a>. If not, click the link.
</body>
""".format(url_for('index'))

def _run():
    app.run(host="0.0.0.0", port=os.environ.get("PORT") if "PORT" in os.environ.keys() else 8080)

def run_app():
    server = Thread(target=_run)
    server.start()

if __name__ == "__main__":
    _run()
