from bson.objectid import ObjectId
from flask import Flask
import json
import requests
from flask import request
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['MONGO_URI'] = "mongodb://Dekate.ar:cmq6amncloq66ll@mongo.servers.nferx.com:27017/anshul_dekate?authSource=admin"

mongo = PyMongo(app)

@app.route('/')
def hello_word():
    output = {"// Hello world ":"Shown below are all the api and their functionalities",
            "/copyInfo?project_id=____" : "copies datasets and models info into new collection",
            "/getInfo?project_id=____":"returns all the datasets and models related to a project",
            "/getInfo?dataset_id=____":"returns the info for that dataset_id",
            "/getInfo?model_id=____":"returns the info for that model_id",
            "/modelsTrained":"returns the list of models which have been trained using that dataset"}
    return output


@app.route('/copyInfo')
def copy_info():

    project_id = request.args.get('project_id')
    print(project_id)
    if project_id is None:
        return "Please specify project id argument"

    response = requests.get("http://sentenceapi2.servers.nferx.com:8015/tagrecorder/v3/projects/"+project_id)

    data = json.loads(response.text)
    str_of_dataset = json.dumps(data["result"]["project"]["associated_datasets"])
    str_of_models = json.dumps(data["result"]["project"]["models"])

    list_of_dataset = json.loads(str_of_dataset)
    list_of_models = json.loads(str_of_models)

    mongo.db.datasets.delete_many({})
    mongo.db.models.delete_many({})
    for doc in list_of_dataset:
        mongo.db.datasets.insert_one(doc)
    for doc in list_of_models:
        mongo.db.models.insert_one(doc)
    
    output_message = ("The info of associated dataset and models retrieved from project_id : " + 
    project_id + " is successfully copied into a new collection." 
    + " There were " + str(len(list_of_dataset)) + " datasets and " + str(len(list_of_models)) + " models.")
    return output_message

@app.route('/getInfo')
def get_info():
    project_id = request.args.get('project_id')
    dataset_id = request.args.get('dataset_id')
    model_id = request.args.get('model_id')

    if project_id is not None :
        #returns the info of all the datasets followed by all the models associated with the project id
        all_docs = []
        all_models = []
        for doc in mongo.db.datasets.find({}):
            doc['_id'] = str(doc['_id'])
            all_docs.append(doc)
        for doc in mongo.db.models.find({}):
            doc['_id'] = str(doc['_id'])
            all_models.append(doc)
        return {"datasets" : all_docs, "models":all_models}
    if dataset_id is not None :
        #assuming correct project is already copied
        doc = mongo.db.datasets.find_one({"_id":(dataset_id)})
        return {"Queried dataset":doc}
        
    if model_id is not None :
        #assuming correct project is already copied
        doc = mongo.db.models.find_one({"_id":ObjectId(model_id)})
        doc['_id'] = str(doc['_id'])
        return {"Queried model":doc}

    return "Please provide one of the project_id, dataset_id or model_id argument"

@app.route('/modelsTrained')
def models_trained():
    dataset_id = request.args.get('dataset_id')
    output = []
    for model in mongo.db.models.find({}):
        found = 0
        for dataset in model["datasets_used"]:
            if (dataset["dataset_id"] == dataset_id):
                found = 1
                break
        if (found):
            output.append(str(model["_id"]))
    return {"List of models using this dataset" : output}


if __name__ == '__main__':
    app.run(debug=True)