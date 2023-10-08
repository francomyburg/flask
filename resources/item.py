import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint,abort
from db import items,stores
from schemas import ItemUpdate,ItemSchema

blp = Blueprint("items",__name__,description="Operations on items")

@blp.route("/item")
class Item(MethodView):
    
    @blp.arguments(ItemSchema)
    @blp.response(201,ItemSchema)
    def post(self,request_data):

        for item in items.values():
            if(request_data["name"] == item["name"]
            and request_data["store_id"] == item["store_id"]):
                abort(400,messages="item already exist")
        print(stores)
        if request_data["store_id"] not in stores:
            abort(404,messages="Store not found")

        item_id = uuid.uuid4().hex
        item = {**request_data, "id": item_id}
        items[item_id] = item

        return item
    
    @blp.response(200,ItemSchema(many=True))
    def get(self):
        return items.values()
    
@blp.route("/item/<string:item_id>")
class ItemId(MethodView):
    
    @blp.response(200,ItemSchema)
    def get(self,item_id):
        try:
            return items[item_id]
        except KeyError:
            abort(404,messages="Store not found")

    def delete(self,item_id):

        try:
            del items[item_id]
            return {"message":"item deleted"}

        except KeyError:
            abort(404,message="item not found")
    
    @blp.arguments(ItemUpdate)
    @blp.response(200,ItemSchema)
    def put(self,item_data,item_id):
      
        try:
            item = items[item_id]
            item |= item_data

            return item
        except KeyError:
            abort(404, message="Item not found.")