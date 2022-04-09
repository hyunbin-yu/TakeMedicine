import json
def get_token():
    with open('./parameter.json','r') as f:
        json_data = json.load(f)
    
    f.close()

    return json_data['bot-token']
    