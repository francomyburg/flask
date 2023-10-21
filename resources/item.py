from flask.views import MethodView
from flask_smorest import Blueprint,abort
from flask_jwt_extended import jwt_required
from schemas import ItemSchema,ItemUpdateSchema,PlainItemSchema
from models import ItemModel
from sqlalchemy.exc import SQLAlchemyError
from db import db

blp = Blueprint("items",__name__,description="Operations on items")

@blp.route("/item")
class Item(MethodView):
    
    @jwt_required()
    @blp.arguments(ItemSchema)
    @blp.response(201,ItemSchema)
    def post(self,item_data):

        item=ItemModel(**item_data)

        try:
            db.session.add(item)
            db.session.commit()
        
        except SQLAlchemyError:
            abort(500,message="an error ocurred while inserting the item")        

        return item
    
    @jwt_required()
    @blp.response(200,ItemSchema(many=True))
    def get(self):
        items = ItemModel.query.all()
        return items
    
@blp.route("/item/<string:item_id>")
class ItemId(MethodView):
    
    @jwt_required()
    @blp.response(200,ItemSchema)
    def get(self,item_id):
        item = ItemModel.query.get_or_404(item_id)
        
        return item

    @jwt_required()
    @blp.response(204,PlainItemSchema)
    def delete(self,item_id):
        item = ItemModel.query.get_or_404(item_id)
        
        db.session.delete(item)

        db.session.commit()

        return item
    
    @blp.arguments(ItemUpdateSchema)
    @blp.response(200,ItemSchema)
    def put(self,item_data,item_id):
        item = ItemModel.query.get(item_id)
        
        if item:
            item.price = item_data["price"]
            item.name = item_data["name"]
        else:
            item=ItemModel(id=item_id,**item_data)
        
        db.session.add(item)

        db.session.commit()
        
        return item