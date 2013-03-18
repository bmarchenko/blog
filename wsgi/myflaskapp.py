import os
from flask import Flask
from flask import request
import pymongo
import json
from bson import json_util
from bson import objectid
import re

app = Flask(__name__)
#add this so that flask doesn't swallow error messages
app.config['PROPAGATE_EXCEPTIONS'] = True

#a base urls that returns all the posts in the collection (of course in the future we would implement paging)
@app.route("/ws/posts")
def posts():
    #setup the connection
    conn = pymongo.Connection(os.environ['OPENSHIFT_MONGODB_DB_URL'])
    db = conn[os.environ['OPENSHIFT_APP_NAME']]

    #query the DB for all the postpoints
    result = db.postpoints.find()

    #Now turn the results into valid JSON
    return str(json.dumps({'results':list(result)},default=json_util.default))


#return a specific post given it's mongo _id
@app.route("/ws/posts/post/<postId>")
def onepost(postId):
    #setup the connection
    conn = pymongo.Connection(os.environ['OPENSHIFT_MONGODB_DB_URL'])
    db = conn[os.environ['OPENSHIFT_APP_NAME']]

    #query based on the objectid
    result = db.postpoints.find({'_id': objectid.ObjectId(postId)})

    #turn the results into valid JSON
    return str(json.dumps({'results' : list(result)},default=json_util.default))


#find posts near a lat and long passed in as query parameters (near?lat=45.5&lon=-82)
@app.route("/ws/posts/near")
def near():
    #setup the connection
    conn = pymongo.Connection(os.environ['OPENSHIFT_MONGODB_DB_URL'])
    db = conn[os.environ['OPENSHIFT_APP_NAME']]

    #get the request parameters
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))

    #use the request parameters in the query
    result = db.postpoints.find({"pos" : { "$near" : [lon,lat]}})

    #turn the results into valid JSON
    return str(json.dumps({'results' : list(result)},default=json_util.default))


#find posts with a certain name (use regex) near a lat long pair such as above
@app.route("/ws/posts/name/near/<name>")
def nameNear(name):
    #setup the connection
    conn = pymongo.Connection(os.environ['OPENSHIFT_MONGODB_DB_URL'])
    db = conn[os.environ['OPENSHIFT_APP_NAME']]

    #get the request parameters
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))

    #compile the regex we want to search for and make it case insensitive
    myregex = re.compile(name, re.I)

    #use the request parameters in the query along with the regex
    result = db.postpoints.find({"Name" : myregex, "pos" : { "$near" : [lon,lat]}})

    #turn the results into valid JSON
    return str(json.dumps({'results' : list(result)},default=json_util.default))


@app.route("/test")
def test():
    return "<strong>It actually worked</strong>"

if __name__ == "__main__":
    app.run()

