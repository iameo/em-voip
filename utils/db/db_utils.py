import uuid
from datetime import datetime
import timeago


def db_id_maker(title):
    #generate a UUID hex file with given title
    return f"{title}__{uuid.uuid4().hex}"



def str_converter(_data=None, type_value='MONGO', data_type='single'):
    #endpoints for microservice - to be updated
    obj_list = []

    _data_list = _data
    if data_type == 'single':
        _data_list = [_data]
    
    i = 0
    final_data = []
    while i < len(_data_list):
        
        _data = _data_list[i]
        if '_id' in _data:
            _data['id'] = db_id_maker(_data['_id'])
            _ = _data.pop('_id')
        else:
            if 'id' not in _data:
                _data['id'] = db_id_maker(type_value)


        for x in obj_list:
            if x in _data:
                if type(_data[x]) is list:
                    n_d = []
                    for y in _data[x]:
                        n_d.append(str(y))
                    _data[x] = n_d
                else:
                    _data[x] = str(_data[x])
        i += 1

        if type_value == 'MONGO':
            time_date = datetime.utcnow()    
            if 'created' in _data:
                _data['created_string'] = timeago.format(_data['created'],time_date)
            if 'modified' in _data:
                _data['modified_string'] = timeago.format(_data['modified'],time_date)
        
        if type_value == 'leads':
            final_data.append({'_index':'leads', '_id':_data['id'], '_source':_data, '_type':'_doc'})
        elif type_value == 'prospect_emails':
            final_data.append({'_index':'prospect_emails', '_id':_data['id'], '_source':_data, '_type':'_doc'})
        else:
            final_data.append(_data)

    if data_type == 'single':
        final_data = final_data[0]

    return final_data
