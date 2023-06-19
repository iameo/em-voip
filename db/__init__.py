from datetime import datetime
from elasticsearch import Elasticsearch, helpers
from pymongo import MongoClient
from pymongo.operations import UpdateOne
import traceback
import os

from utils.db.db_utils import db_id_maker, str_converter



endpoint_es = os.getenv('ELASTIC_SEARCH_ENDPOINT')
es_user = os.getenv('ELASTIC_SEARCH_USERNAME')
es_pwd = os.getenv('ELASTIC_SEARCH_PASSWORD')

ELASTIC_SEARCH_CLOUD_ID = os.getenv('ELASTIC_SEARCH_CLOUD_ID')
ELASTIC_SEARCH_ENDPOINT = os.getenv('ELASTIC_SEARCH_ENDPOINT', 'http://127.0.0.1:9200')

MONGO_DB_CLIENT = os.getenv('MONGO_DB_CLIENT', 'mongodb://127.0.0.1/27017')
mongo_endpoint_local = 'mongodb://127.0.0.1/27017'


DEBUG = int(os.getenv("FLASK_DEBUG", 0))

if not DEBUG:
    es = Elasticsearch(cloud_id=f'{ELASTIC_SEARCH_CLOUD_ID}', 
    http_auth=(f'{es_user}', f'{es_pwd}'))

    client = MongoClient(MONGO_DB_CLIENT)
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(str(e), "MONGO CONNECT")
else:
    es = Elasticsearch([ELASTIC_SEARCH_ENDPOINT])
    client = MongoClient(mongo_endpoint_local)

print(es.ping(), "elasticsearch pinging..........")
db_ = client.test.testr #client.xxx.xxx




def db_fetch(index, id=None, query=None, agg=False, exclude=[]):
    if query:
        query["from"] = query.get('from', 0)
        #set default size if None
        query['size'] = query.get('size', 1000)

        if exclude and '_source' in query:
            query['_source'][exclude] = exclude
        else:
            query['_source'] = {'excludes': exclude}


    try:
        if id is not None:
            data = es.get(index=index, id=id)['_source']
            if exclude:
                for exclude_ in exclude:
                    _ = data.pop(exclude_, None)
            return data
        else:
            #log this - ping to check elasticsearch instance is running
            print(es.ping(), "id not not attached")

            data = None
            #create a new index with index and ignore ERROR 400
            es.indices.create(index=index, ignore=400)
            try:
                data = es.search(index=index, body=query, ignore=[400,404])
            except Exception as e:
                #log
                print(str(e), "<<<<>>>>>")

            if agg:
                return data
            return [hit['_source'] for hit in data['hits']['hits']]
    except:
        return None


def post_data_to_db(index=None, json_data={}, err_msg=False):
    table = db_.db[index]
    # print(table, index, "kkkkkkkkk")
    if isinstance(json_data, dict):
        try:
            _ = table.insert_one(json_data)
            json_data = str_converter(_data=json_data, type_value='ES')
            try:
                es.index(index=index, id=json_data['id'], body=json_data, refresh='wait_for')
            except Exception as e:
                print(">>>>>>", str(e))  #fuck around and find out
            return json_data
        except Exception as e:
            if err_msg:
                return {'err':str(e), 'data': []}
            return {'err':str(e), 'data': []}
    try:
        for data in json_data:
            if '_id' not in data:
                if 'id' in data:
                    data['_id'] = data['id']
                else:
                    data['_id'] = db_id_maker(index)
        table.insert_many(json_data)
        json_data = str_converter(json_data, index, 'multi')
        helpers.bulk(es, json_data, refresh='wait_for')
        if err_msg:
            return {'err':traceback.format_exc(), 'data':json_data}
        return None
    except:
        table.update_one({'_id':json_data['_id']}, {"$set": {"is_delete":1}})
        return None

def put_data_in_db(index=None, json_data=None, want_data=True, err_msg=False, on_both=True):
    table = db_.db[index]
    if isinstance(json_data, dict):
        if id is None:
            return None
        if on_both:
            try:
                table.update_one({'_id':id}, {"$set":json_data})
            except:
                try:
                    table.update_one({'_id':id}, {"$set":data})
                except:
                    pass
        if want_data:
            return db_fetch(index=index, id=id)
        return True
    else:
        try:
            bulk = table.bulk_write([])
            for data in json_data:
                lead_id = data['id'] if 'id' in data else data['_id']
                bulk.append(
                    UpdateOne({'_id': lead_id}, {"$set":data}, upsert=True)
                    )

            json_data = str_converter(json_data, index, 'multi')

            if err_msg:
                return {'err':traceback.format_exc(), 'data':data}
            return json_data
        except:
            if err_msg:
                return {'err_msg':traceback.format_exc(), 'data':[]}
            return None


def db_field(index=None, field=None, value=None):
    q_array = [{
            "match_phrase": {
                    field: value
                }
            }]
    json_query = {
        "query": {
            "bool": {
            "must": q_array
                }
            },
        'from':0,
        'size':10000
    }
    return db_fetch(index=index, query=json_query)



def db_save(index, user_id, account_id, json_data, lead_id=None, pipeline_id=None, contact_id=None):
    """
    db_save: save data to the DB
    
    args:
        index: table index being accessed
        account_id: the account currently accessing the function
        json_data: data that requires saving
    """
    time_date = datetime.utcnow()
    fixed_json = {
        'modified_by': user_id,
        'modified': time_date
    }
             

    if 'is_archived' in json_data:
        is_archived = json_data['is_archived']
        _ =  json_data.pop('is_archived')
    else:
        is_archived = 0

    if 'is_shared' in json_data:
        is_shared = json_data['is_shared']
        _ = json_data.pop('is_shared')
    else:
        is_shared = 1

    if 'status' in json_data:
        status = json_data['status']
        _ = json_data.pop('status')
    else:
        status = 1

    fixed_json_post =  {
        'status': status,
        'is_delete': 0,
        'is_archived': is_archived,
        'is_shared': is_shared,
        'created': time_date,
        'company_id': account_id,
        'user_id': user_id
    }

    if '_id' not in json_data:
        fixed_json_post['_id'] = db_id_maker(index)

    fixed_json.update(fixed_json_post)
    json_data.update(fixed_json)

    return post_data_to_db(index=index,json_data=json_data)



def delete_from_db(index=None, id=None, user_id=None):
    """
    function to delete data by id and index'
    
    args:
        index: index of table
        id: id of data
        user_id: user currently accessing the function
    """
    json_data = {
        'modified_by': user_id,
        'modified_ts': datetime.utcnow(),
        'is_delete': 1
    }
    return put_data_in_db(index=index, json_data=json_data, id=id)



