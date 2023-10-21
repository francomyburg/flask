from flask import Flask,jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager


from db import db
from models import TokenModel
from blocklist import BLOCKLIST

from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tags import blp as TagBlueprint
from resources.user import blp as UserBlueprint
#la fx se tiene que llamar "create_app" para que inicie
def create_app(db_url=None):  
    
    app = Flask(__name__) 

    #propagate_exceptions si hay una excepcion en las extensiones se puede ver mas facil
    app.config["PROPAGATE_EXCEPTIONS"] = True
    #configuracion para ver la documentacion de swagger http://127.0.0.1:5000/swagger-ui
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "sqlite:///data.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    db.init_app(app)
    
    api = Api(app)

    app.config["JWT_SECRET_KEY"] = "franco"
    jwt= JWTManager(app)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header,jwt_payload):
        return(jsonify({"message":"The token has expired","error":"token_expired"}),401)

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return(jsonify({"message":"Signature verification failed","error":"invalid_token"}),401)
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return(jsonify({"description": "Request does not contain an access token.",
                "error": "authorization_required"}),401)
    
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header,jwt_payload):
        jwt=jwt_payload["jti"]
        token = db.session.query(TokenModel).filter_by(token=jwt).scalar()
        return token is not None
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header,jwt_payload):
        return (jsonify({"description":"the token has been revoked","error":"token_revoked"}),401)

    
    with app.app_context():
        db.create_all()



    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app

