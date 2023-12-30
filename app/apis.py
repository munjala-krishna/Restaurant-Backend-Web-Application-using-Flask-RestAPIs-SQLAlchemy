from app import application
from flask import jsonify, Response, session
from app.models import *
from app import *
import uuid
import datetime
from marshmallow import Schema, fields
from flask_restful import Resource, Api
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
import json


class SignUpRequest(Schema):
    name     = fields.Str(default = 'name')
    username = fields.Str(default = 'username')
    password = fields.Str(default = 'password')
    level    = fields.Str(default = 'level')

class LoginRequest(Schema):
    username = fields.Str(default = 'username')
    password = fields.Str(default = 'password')

class AddVendorRequest(Schema):
    user_id  = fields.Str(default = 'user_id')

class APIResponse(Schema):
    message  = fields.Str(default = 'Success')

class GetVendorResponse(Schema):
    vendors  = fields.List(fields.Dict())

class AddItemRequest(Schema):
    item_id   = fields.Str(default = 'item_id')
    item_name = fields.Str(default = 'item_name')
    restaurant_name = fields.Str(default = 'restaurant_name')
    available_quantity = fields.Int(default = 0)
    unit_price =  fields.Int(default = 0)
    calories_per_gm = fields.Int(default = 0)

class ListItemsResponse(Schema):
    items = fields.List(fields.Dict())

class PlaceOrderRequest(Schema):
    order_id = fields.Str(default = 'order_id')

class CreateItemOrderRequest(Schema):
    order_id = fields.Str(default = 'order_id')
    item_id  = fields.Str(default = 'item_id')
    quantity = fields.Int(default = 0)
    
class ListOrdersByCustomerRequest(Schema):
    customer_id = fields.Str(default = 'customer_id')

class ListOrdersByCustomerResponse(Schema):
    orders = fields.List(fields.Dict())

class ListAllOrdersResponse(Schema):
    all_orders = fields.List(fields.Dict())



#  Restful way of creating APIs through Flask Restful
class SignUpAPI(MethodResource, Resource):
    @doc(decription = 'Sign Up API', tags = ['SignUp API'])
    @use_kwargs(SignUpRequest, location = ('json'))
    @marshal_with(APIResponse) 
    def post(self, **kwargs):
        try:
            user = User(
                uuid.uuid4(),
                kwargs['name'],
                kwargs['username'],
                kwargs['password'],
                kwargs['level'])
            db.session.add(user)
            db.session.commit()
            print('User Registered Successfully')
            return APIResponse().dump(dict(message = "User Registered Successfully")),200
        
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message = f'Not able to register user : {str(e)}')), 400

api.add_resource(SignUpAPI, '/signup')
docs.register(SignUpAPI)




class LoginAPI(MethodResource, Resource):
    @doc(description = 'Login API', tags = ['Login API'])
    @use_kwargs(LoginRequest, location = ('json'))
    @marshal_with(APIResponse)
    def post(self, **kwargs):
        try:
            valid_user = User.query.filter_by(username = kwargs['username'], password = kwargs['password']).first()
            if valid_user:
                print('logged in')
                session['user_id'] = valid_user.user_id
                return APIResponse().dump(dict(message = 'User Logged in Successfully')), 200
            else:
                print('user Not Found')
                return APIResponse().dump(dict(message = "User Not Found")), 404
                   
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message = f'Not able to Login user : {str(e)}')), 400
            
api.add_resource(LoginAPI, '/login')
docs.register(LoginAPI)




class LogoutAPI(MethodResource, Resource):
    @doc(description = 'Log Out API', tags = ['Logout API'])
    @marshal_with(APIResponse)
    def get(self):
        try:
            if session['user_id']:
                session['user_id'] = None
                print('logged out')
                return APIResponse().dump(dict(message = 'Used LoggedOut Successfully')), 200
            else:
                print('user not found')
                return APIResponse().dump(dict(message = 'User is not Logged In')), 401
            
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message = f'Unable to logout user: {str(e)}')), 400

api.add_resource(LogoutAPI, '/logout')
docs.register(LogoutAPI)




class AddVendorAPI(MethodResource, Resource):
    @doc(documentation = 'Add Vendor API', tags = ['Add_vendor API'])
    @use_kwargs(AddVendorRequest, location = ('json'))
    @marshal_with(APIResponse)
    def post(self, **kwargs):
        try:
            if session['user_id']:
                valid_user = User.query.filter_by(user_id = kwargs['user_id']).first()
                if valid_user:
                    valid_user.level = 1
                    db.session.commit()
                    print('Vendor added')
                    return APIResponse().dump(dict(message = 'Vendor added successfully')), 200
                else:
                    print('Invalid User/Customer')
                    return APIResponse().dump(dict(message = 'Invalid user/Customer')), 404    
            else:
                print('User Not Logged In')
                return APIResponse().dump(dict(message = 'User is not Logged In')), 401
            
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message = f'Unable to Add Vendor : {str(e)}')), 400

api.add_resource(AddVendorAPI, '/add_vendor')
docs.register(AddVendorAPI)




class GetVendorsAPI(MethodResource, Resource):
    @doc(description = 'Get All Vendors List API', tags = ['Get_all_vendors API'] )
    @marshal_with(GetVendorResponse)
    def get(self):
        try:
            if session['user_id']:
                all_vendors = User.query.filter_by(level = 1)
                vendors_list  = list()
                for vendor in all_vendors:
                    a_vendor_id = vendor.user_id
                    vendor_items = Item.query.filter_by(vendor_id = a_vendor_id)
                    for vendor_item in vendor_items:
                        item_dict = {}
                        item_dict['vendor_id'] = a_vendor_id
                        item_dict['vendor_name'] = User.query.filter_by(user_id = a_vendor_id).first().name
                        item_dict['restaurant_name'] = vendor_item.restaurant_name
                        item_dict['item_name'] = vendor_item.item_name

                        vendors_list.append(item_dict)
                print(vendors_list)
                return GetVendorResponse().dump(dict(vendors = vendors_list)), 200
            else:
                print('User Not Logged In')
                return APIResponse().dump(dict(message = 'User Not Logged In')), 401

        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message = f'Unable to fetch Vendors Details : {str(e)}')),400              

api.add_resource(GetVendorsAPI, '/list_vendors')
docs.register(GetVendorsAPI)




class AddItemAPI(MethodResource, Resource):
    @doc(description = 'Add Item API', tags = ['Add_item: API'])
    @use_kwargs(AddItemRequest, location = 'json')
    @marshal_with(APIResponse)
    def post(self, **kwargs):
        try:
            if session['user_id']:
                vendor_check = User.query.filter_by(user_id = session['user_id']).first().level
                if vendor_check == 1:
                    new_item = Item(
                        kwargs['item_id'],
                        session['user_id'],
                        kwargs['item_name'],
                        kwargs['calories_per_gm'],
                        kwargs['available_quantity'],
                        kwargs['restaurant_name'],
                        kwargs['unit_price'])
                    db.session.add(new_item)
                    db.session.commit()
                    print('Item Added')
                    return APIResponse().dump(dict(message = 'Item Added Successfully')), 200
                else:
                    print('Only Vendor can Add Item')
                    return APIResponse().dump(dict(message = 'Only Vendor is authorized to add Item')), 401
            else:
                print('User Not Logged In')
                return APIResponse().dump(dict(message = 'User Not Logged In')), 401
            
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message = f'Unable to Add Item : {str(e)}')), 400

api.add_resource(AddItemAPI, '/add_item')
docs.register(AddItemAPI)




class ListItemsAPI(MethodResource, Resource):
    @doc(description = 'List All Items API', tags = ['List_Items API'])
    @marshal_with(ListItemsResponse)
    def get(self):
        try:
            if session['user_id']:
                all_items = Item.query.all()
                items_list = list()
                for an_item in all_items:
                    item_dict = {}
                    item_dict['item_name'] = an_item.item_name
                    item_dict['calories_per_gm'] = an_item.calories_per_gm
                    item_dict['available_quantity'] = an_item.available_quantity
                    item_dict['restaurant_name'] = an_item.restaurant_name
                    item_dict['unit_price'] = an_item.unit_price

                    items_list.append(item_dict)
                print(items_list)
                return ListItemsResponse().dump(dict(items = items_list)), 200
            else:
                print('User Not Logged In')
                return APIResponse().dump(dict(message = 'User Not Logged In')), 401
            
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message = f'Unable to List Items : {str(e)}')), 400

api.add_resource(ListItemsAPI, '/list_items')
docs.register(ListItemsAPI)




class CreateItemOrderAPI(MethodResource, Resource):
    @doc(description = 'Create Item Order API', tags = ['Create_Item_Order API'])
    @use_kwargs(CreateItemOrderRequest)
    @marshal_with(APIResponse)
    def post(self, **kwargs):
        try:
            if session['user_id']:
                valid_customer = User.query.filter_by(user_id = session['user_id']).first().level
                if valid_customer == 0:
                    valid_order_id = Order.query.filter_by(order_id = kwargs['order_id']).first()
                    if valid_order_id:
                        if valid_order_id.user_id == session['user_id']:
                            if Item.query.filter_by(item_id = kwargs['item_id']).first():
                                new_order_item = OrderItems(
                                id       = uuid.uuid4(),
                                order_id = kwargs['order_id'],
                                item_id  = kwargs['item_id'],
                                quantity = kwargs['quantity'])
                                db.session.add(new_order_item)
                                db.session.commit()
                                print(new_order_item)
                                return APIResponse().dump(dict(message ='Order Items created Successfully')), 200
                            else:
                                print('Invalid Item Id')
                                return APIResponse().dump(dict(message = 'Invalied Item Id')), 404
                        else:
                            print('Order Id does not belong to the customer')
                            return APIResponse().dump(dict(message = 'Order Id is not of the Customer')), 401
                    else:
                        print('Invalid order Id')
                        return APIResponse().dump(dict(message = 'Invalid Order Id')), 404
                else:
                    print('Only Customer can create Item in Order')
                    return APIResponse().dump(dict(message = 'Only Customer can create Item in Order')), 401    
            else:
                print('User Not Logged In')
                return APIResponse().dump(dict(message = 'User Not Logged In')), 401
        
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message = f'Not able to Create Item Order : {str(e)}')), 400
            
api.add_resource(CreateItemOrderAPI, '/create_items_order')
docs.register(CreateItemOrderAPI)




class PlaceOrderAPI(MethodResource, Resource):
    @doc(description = 'Place Order API', tags = ['Place_order API'])
    @use_kwargs(PlaceOrderRequest, location=('json'))
    @marshal_with(APIResponse)
    def post(self, **kwargs):
        try:
            if session['user_id']:
                valid_customer = User.query.filter_by(user_id = session['user_id']).first().level
                if valid_customer == 0:
                    new_order = Order(
                        order_id = kwargs['order_id'],
                        user_id = session['user_id'])
                    db.session.add(new_order)
                    db.session.commit()
                    print(new_order)
                    return APIResponse().dump(dict(messsage = 'Order Placed Successfully')), 200
                else:
                    print('Not a Customer')
                    return APIResponse().dump(dict(message = 'Only Customers can Place Order!')), 401
            else:
                print('User Not Logged In')
                return APIResponse().dump(dict(message = 'User Not LoggeD In')), 401

        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message = f'Not able to Place Order : {str(e)}')), 400    
                     
api.add_resource(PlaceOrderAPI, '/place_order')
docs.register(PlaceOrderAPI)




class ListOrdersByCustomerAPI(MethodResource, Resource):
    @doc(decription = 'List Orders By Customer API', tags = ['Get_all_orders_by_customer API'])
    @use_kwargs(ListOrdersByCustomerRequest, location = ('json'))
    @marshal_with(ListOrdersByCustomerResponse)
    def post(self, **kwargs):
        try:
            if session['user_id']:
                valid_customer = User.query.filter_by(user_id = session['user_id']).first().level
                if valid_customer == 0:
                    cust_orders = Order.query.filter_by(user_id = session['user_id'])
                    orders_list = list()
                    for an_order in cust_orders:
                        order_dict = {}
                        order_dict['order_id'] = an_order.order_id
                        order_dict['item_id'] = OrderItems.query.filter_by(order_id = an_order.order_id).first().item_id
                        order_dict['quantity'] = OrderItems.query.filter_by(order_id = an_order.order_id).first().quantity
                        
                        orders_list.append(order_dict)
                    print(orders_list)    
                    return ListOrdersByCustomerResponse().dump(dict(orders = orders_list)), 200
                else:
                    print('User is not a Customer')
                    return APIResponse().dump(dict(message = 'User is not a customer')), 401
            else:
                print('Customer Not Logged In')
                return APIResponse().dump(dict(message = 'Customer Not Logged In')), 401

        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message = 'Unable to List Customer Orders: {str(e)}')), 400         

api.add_resource(ListOrdersByCustomerAPI, '/list_orders')
docs.register(ListOrdersByCustomerAPI)




class ListAllOrdersAPI(MethodResource, Resource):
    @doc(description = 'List All Orders API', tags = ['Get_all_orders API'])
    @marshal_with(ListAllOrdersResponse)
    def get(self):
        try:
            if session['user_id']:
                valid_admin = User.query.filter_by(user_id = session['user_id']).first().level
                if valid_admin == 2:
                    total_orders = OrderItems.query.all()
                    orders_list = list()
                    for an_order in total_orders:
                        order_dict = {}
                        order_dict['order_id'] = an_order.order_id
                        order_dict['user_id'] = Order.query.filter_by(order_id = an_order.order_id).first().user_id
                        order_dict['item_id'] = an_order.item_id
                        order_dict['quantity'] = an_order.quantity
                        
                        orders_list.append(order_dict)
                    print(orders_list)
                    return ListAllOrdersResponse().dump(dict(all_orders = orders_list)), 200

                else:
                    print('Only Admin can Get All Orders List ')
                    return APIResponse().dump(dict(message = 'Only Admin can Get All Orders List')), 401
            else:
                print('User Not Logged In')
                return APIResponse().dump(dict(message = 'User Not Logged In')), 401

        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message = 'Not able to List All Orders : {str(e)}')), 400
            
api.add_resource(ListAllOrdersAPI, '/list_all_orders')
docs.register(ListAllOrdersAPI)