from flask.views import MethodView
from flask_smorest import Blueprint,abort
from flask_jwt_extended import create_access_token,get_jwt,jwt_required
from passlib.hash import pbkdf2_sha256

from db import db
from models import UserModel,TokenModel
from schemas import UserSchema
from blocklist import BLOCKLIST

blp = Blueprint("users",__name__,description="Operations on users")

@blp.route("/logout")
class UserLogout(MethodView):
    
    @jwt_required()
    def post(self):
        jti= get_jwt()["jti"]
        block_token= TokenModel(token=jti)
        db.session.add(block_token)
        db.session.commit()

        return {"message": "Successfully logged out"}, 200
    


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self,user_data):
        
        if UserModel.query.filter(UserModel.username==user_data["username"]).first():
            abort(409,message="A user with that username already exists")

        user = UserModel(
            username = user_data["username"],
            password = pbkdf2_sha256.hash(user_data["password"]) 
        )

        db.session.add(user)
        db.session.commit()

        return {"message":"user created succesfully"},201

@blp.route("/user/<int:user_id>")
class User(MethodView):

    def delete(self,user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()

        return {"message":"User deleted"},200

    @blp.response(200,UserSchema)
    def get(self,user_id):
        user = UserModel.query.get_or_404(user_id)

        return user
    
    
@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self,user_data):
        user = UserModel.query.filter(UserModel.username == user_data["username"]).first()

        if user and pbkdf2_sha256.verify(user_data["password"],user.password):
            acces_token = create_access_token(identity=user.id)
            return {"acces_token":acces_token},200
        
        abort(401,message="invalid credentials")


    

        

        
