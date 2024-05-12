import werkzeug
import werkzeug.utils
from flask import Flask, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)

# app.config["MONGO_URI"] = "mongodb+srv://khanwaleedatif23:ulOAIZKK9EL5aP7W@hawkposdevelopmentclust.fuaw3dz.mongodb.net/"
client = MongoClient("mongodb+srv://khanwaleedatif23:ulOAIZKK9EL5aP7W@hawkposdevelopmentclust.fuaw3dz.mongodb.net/")
db =client.hawk_db
businesses = db.businesses
@app.route('/addBusiness', methods=['POST'])
def addBusiness():
    print("the request is "+request.json['businessName'])
    businessName = request.json['businessName']
    branchName = request.json['branchName']
    print(businessName, branchName)
    ref = db.businessCollection.insert_one({'businessName':businessName,'branchName':branchName})
    print(ref.inserted_id)
    return {'businessId':str(ref.inserted_id)},200 


@app.route('/registerAdmin',methods=['POST'])
def registerAdmin():
    print("the request for sign up is "+request.json['username']+" "+request.json["password"]+" "+request.json["businessId"])
    username = request.json['username']
    password = request.json['password']
    businessId = request.json['businessId']
    users = db.users
    existingUser = users.find_one({'username':username,'password':password})
    if(existingUser is None):
        users.insert_one({'username':username,'password':password,"businessId":businessId})
        return {'message':'User successfully added. You can login with these credentials on your mobile device',},200 
    return {'message':'User already exists.'},230

@app.route('/signInAdmin',methods=["POST"])
def signInAdmin():
    print("the request for sign in has the following fields inside it"+request.json['username']+ " and "+request.json['password'])
@app.route('/registerCustomer',methods=['POST'])
def registerCustomer():
    print("the request for sign up is "+request.json['name']+" "+request.json["gender"]+" "+request.json["contact"])
    name = request.json['name']
    gender = request.json['gender']
    contact = request.json['contact']
    region = request.json['region']
    city= request.json['city']

    customers = db.customers
    existingCustomer = customers.find_one({'name':name,'contact':contact})
    if(existingCustomer is None):
        customers.insert_one({'name':name,'contact':contact,"gender":gender,"region":region,"city":city})
        return {'message':'Customer successfully added. You can login with these credentials on your mobile device',},200 
    return {'message':'User already exists.'},230    



@app.route('/createAd',methods=['POST'])
def createAd():
    imageFile = request.files['image']
    adContent = request.form['content']
    # filename = werkzeug.utils.secure_filename(imageFile.filename)
    client.save_file(adContent,imageFile)

    # existingCustomer = customers.find_one({'name':name,'contact':contact})
    
    return {'message':'Advertisement was added successfully'},200   


if __name__=="__main__":
    app.run(debug=True)
