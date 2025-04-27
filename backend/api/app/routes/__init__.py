from .recommend import bp_recommend
from .playlists import bp_playlists

def register_blueprints(app):
    app.register_blueprint(bp_recommend)
    app.register_blueprint(bp_playlists)
