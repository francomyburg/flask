from db import db

class TokenModel(db.Model):
    
    id = db.Column(db.Integer,primary_key=True)
    token=db.Column(db.String(),nullable=False)