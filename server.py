from functools import wraps
from flask import request, Response, Flask, jsonify
from cloudflare import DDNS_updater
import toml
import os

app = Flask(__name__)

CONFIG_PATH=os.path.join(os.path.abspath('.'),'config.toml')
CONFIG=None
ddnser = None

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == CONFIG["auth"]["username"] and password == CONFIG["auth"]["password"]

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def load_config(file_path: str):
    global CONFIG
    CONFIG = toml.load(file_path)

@app.route('/')
@requires_auth
def index():
    return "This a basic test page"

@app.route('/ddns/<subdomain>', methods=["POST"])
@requires_auth
def ddns(subdomain):
    assert request.method == "POST"
    dns_type = request.form['type']
    subdomain_request = request.form['subdomain']
    content = request.form['content']
    if subdomain_request == subdomain:
       return jsonify(ddnser.update_record(subdomain, dns_type, content))
    else:
        return Response("postfix and post content dismatch! {post}!={url}".format(
            post=subdomain_request,
            url=subdomain,
        ), 404)

if __name__ == "__main__":
    load_config(CONFIG_PATH)
    ddnser = DDNS_updater(CONFIG['cloudflare']['email'], CONFIG['cloudflare']['api_key'])
    app.run(host="0.0.0.0", port=8888)