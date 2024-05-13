import firebase_admin
import pandas as pd
import werkzeug
import werkzeug.utils
from bson.objectid import ObjectId
from firebase_admin import credentials, storage
from flask import Flask, jsonify, request
from pymongo import MongoClient

cred = credentials.Certificate("hawkpos-cb923-firebase-adminsdk-hccml-9cecb5e2ba.json")
firebase_admin.initialize_app(cred,{
    "storageBucket":'hawkpos-cb923.appspot.com'
})
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
    print("the request for sign in has the following fields inside it"+request.json['username']+ " and "+request.json['password']+" and "+ request.json['businessId'])
    username = request.json['username']
    password = request.json['password']
    businessId = request.json['businessId']
    users = db.users
    user = users.find_one({'username':username})
    if user and user['password']==password and user['businessId']==businessId:
        return {'message':"Sign in successful."},200
    else:
        return {'message':"Invalid username, password or businessId"},401

@app.route('/registerCustomer',methods=['POST'])
def registerCustomer():
    print("the request for sign up is "+request.json['name']+" "+request.json["gender"]+" "+request.json["contact"])
    name = request.json['name']
    gender = request.json['gender']
    email = request.json['email']
    contact = request.json['contact']
    region = request.json['region']
    city= request.json['city']

    customers = db.customers
    existingCustomer = customers.find_one({'name':name,'contact':contact, 'email':email})
    if(existingCustomer is None):
        customers.insert_one({'name':name,'contact':contact,'email':email,"gender":gender,"region":region,"city":city})
        return {'message':'Customer successfully added. You can login with these credentials on your mobile device',},200 
    return {'message':'User already exists.'},230    

@app.route('/signInCustomer',methods=["POST"])
def signInCustomer():
    print("the request for sign in has the following fields inside it"+request.json['email']+ " and "+request.json['contact'])
    email = request.json['email']
    contact = request.json['contact']

    customers = db.customers
    customer = customers.find_one({'email':email})
    if customer and customer['contact']==contact:
        return {'message':"Sign in successful."},200
    else:
        return {'message':"Invalid contact or email"},401



@app.route('/addDashboardData', methods=['POST'])
def addDashboardData():

    businessId = request.json['businessId']
    topSellingProduct = request.json["topSellingProduct"]
    topCustomer = request.json["topCustomer"]
    topEmployee = request.json['topEmployee']
    totalBalance = request.json['totalBalance']
    salesToday = request.json['salesToday']
    billsForGraph = request.json['billsForGraph']
    lowOnStock = request.json['lowOnStock']
    businesses = db.businessCollection
    businesses.update_one({'_id': ObjectId
    (businessId)}, {'$set': {
            'topSellingProduct': topSellingProduct,
            'topCustomer': topCustomer,
            'topEmployee': topEmployee,
            'totalBalance':totalBalance,
            'salesToday': salesToday,
            'billsForGraph':billsForGraph,
            'lowOnStock':lowOnStock
        }})
    
    return {'message':'all data added successfully'},200 


@app.route('/fetchDashboardData', methods=['POST'])
def fetchDashboardData():
    businessId = request.json['businessId']
    businesses = db.businessCollection
    business = businesses.find_one({"_id":ObjectId(businessId)})
    if business:
        return {"business":{"billsForGraph":business["billsForGraph"],"lowOnStock":business["lowOnStock"],"salesToday":business["salesToday"],"topCustomer":business["topCustomer"],"topEmployee":business["topEmployee"],"topSellingProduct":business["topSellingProduct"],"totalBalance":business["totalBalance"]}},200
    else:
        return {"message":"business for current id does not exist"},401
@app.route('/addBill', methods=['POST'])
def addBill():
    # print("the request to add bill has this"+ request.json["products"])

    products = request.json['products']
    cashierName = request.json['cashierName']
    businessName = request.json['businessName']
    branchName = request.json['branchName']
    totalAmount = request.json['totalAmount']
    dateTime = request.json['dateTime']
    customerContact = request.json['customerContact']
    status = request.json['status']
    bills = db.bills

    bills.insert_one({'cashierName':cashierName,'businessName':businessName,'branchName':branchName,'totalAmount':totalAmount,'dateTime':dateTime,'customerContact':customerContact,'status':status,'products':products})
    return {'message':"Bill successfully added"},200


@app.route('/fetchBills',methods =['POST'])
def fetchBills():
    contact = request.json['contact']
    bills = db.bills
    billsToReturn = []
    allBills = list(bills.find({'customerContact':contact}))
    if len(allBills)==0:
        return {'message':"no bills found for the customer"},401
    else:
        customer_bills_list = []
        for bill in allBills:
            bill['_id'] = str(bill['_id'])  
            customer_bills_list.append(bill)
        print('bro i am here',allBills)
        return {'allBills':allBills},200




@app.route('/createAd',methods=['POST'])
def createAd():
    image = request.files['image']
    caption = request.form['caption']
    
    # Upload image to Firebase Storage
    bucket = storage.bucket()
    blob = bucket.blob(image.filename)
    blob.upload_from_file(image)
    blob.make_public()
    # Get URL of the uploaded image
    url = blob.public_url

    adCollection = db.ads
    ad = adCollection.insert_one({"caption":caption, "imgURL":url})
    return {'message':'Advertisement was added successfully'},200   

@app.route('/fetchAds',methods=['GET'])
def fetchAds():
    ads_collection = db.ads
    ads = list(ads_collection.find({}))  # Retrieve all ads from the collection
    # Convert ObjectId to string for JSON serialization
    for ad in ads:
        ad['_id'] = str(ad['_id'])

    return {"allAds":ads},200
@app.route('/fetchAiSuggestions',methods=['GET'])
def fetchAi():
    bills_df = pd.read_excel("Bills.xlsx")
    products_df = pd.read_excel("Products.xlsx")
    customers_df = pd.read_excel("Customers.xlsx")

    #Split Columns in Bills DataFrame
    bills_ids = bills_df['Bill Id'].astype(int)
    bills_sale_quantity = bills_df['Sale Qty'].astype(str).apply(lambda x: [int(qty) for qty in x.split(',')])
    bills_product_ids = bills_df['Product Id'].astype(str).apply(lambda x: [int(pid) for pid in x.split(',')])
    bills_date = pd.to_datetime(bills_df['Date'], format='%d-%b-%Y')
    bills_customer_ids = bills_df['Customer Id'].astype(int)
    bills_amounts = bills_df['Bill Amount'].astype(str).apply(lambda x: [int(b_amt) for b_amt in x.split(',')])

    #Split Columns in products DataFrame
    products_ids = products_df['Id'].astype(int)
    products_unit_price = products_df['Unit Price'].astype(int)
    products_name = products_df['Product'].astype(str)

    # Split Columns in customers DataFrame
    customers_ids = customers_df['Customer Id'].astype(int)
    customers_name = customers_df['Customer Name'].astype(str)

    customer_occurances = []
    # product_occurances = []
    product_quantities = []

    for c_id in customers_ids:

        cid_occurrence = [index for index, value in enumerate(bills_customer_ids) if value == c_id]
        customer_occurances.append(cid_occurrence)


    for idx, p_id in enumerate(products_ids):

        pid_occurrence = []
        product_quantities.append([])

        for index, value in enumerate(bills_product_ids):

            try:

                if p_id in value:
                    p_list = bills_product_ids[index]
                    qty_list = bills_sale_quantity[index]
                    p_idx = p_list.index(p_id)
                    p_qty = qty_list[p_idx]
                    product_quantities[idx].append(p_qty)

            except Exception as e:
                pass

    import math

    total_sales_quantity = [sum(qty_lst) for qty_lst in product_quantities]
    total_sales_amount = [qty * unit_price for qty, unit_price in zip(total_sales_quantity, products_unit_price)]

    average_sales_quantity = [math.ceil(sum(qty_lst) / len(qty_lst)) for qty_lst in product_quantities]
    average_sales_amount = [math.ceil(qty * unit_price) for qty, unit_price in zip(average_sales_quantity, products_unit_price)]

    # print(f"total_sales_quantity: {total_sales_quantity}")
    # print(f"total_sales_amount: {total_sales_amount}")

    # print(f"average_sales_quantity: {average_sales_quantity}")
    # print(f"average_sales_amount: {average_sales_amount}")

    # Define significance criteria based on total sales amount
    high_significance_amount = [p_id for p_id, amount in zip(products_ids, total_sales_amount) if amount > 10000000]
    medium_significance_amount = [p_id for p_id, amount in zip(products_ids, total_sales_amount) if 500000 < amount <= 10000000]
    low_significance_amount = [p_id for p_id, amount in zip(products_ids, total_sales_amount) if amount <= 500000]

    # Define significance criteria based on total sales quantity
    high_significance_quantity = [p_id for p_id, qty in zip(products_ids, total_sales_quantity) if qty > 10000]
    medium_significance_quantity = [p_id for p_id, qty in zip(products_ids, total_sales_quantity) if 3000 < qty <= 7000]
    low_significance_quantity = [p_id for p_id, qty in zip(products_ids, total_sales_quantity) if qty <= 3000]

    # Take intersection of products meeting both criteria
    high_significance_products = list(set(high_significance_amount) | set(high_significance_quantity))
    medium_significance_products = list(set(medium_significance_amount) | set(medium_significance_quantity))
    low_significance_products = list(set(low_significance_amount) | set(low_significance_quantity))


    common_high_medium = set(high_significance_products) & set(medium_significance_products)
    high_significance_products = list(set(high_significance_products) - common_high_medium)

    # Add removed elements to medium significance set
    medium_significance_products =list( set(medium_significance_products) | common_high_medium)

    # Remove common elements between low and medium significance sets
    common_low_medium = set(low_significance_products) & set(medium_significance_products)
    medium_significance_products = list(set(medium_significance_products) - common_low_medium)

    # Add removed elements to low significance set
    low_significance_products = list(set(low_significance_products) | common_low_medium)
    return {"topProducts":[high_significance_products[0],high_significance_products[1],high_significance_products[2]]},200
    

if __name__=="__main__":
    app.run(debug=True)
