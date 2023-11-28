import json

with open("promts.json", "r") as fh:
    data = json.load(fh)
    promts = data['to_gen']

with open("promts.json", 'w') as json_file:
    if len(promts) > 50:
        data['to_gen'] = promts[50:]
        promts = promts[:50]
    else:
        data['to_gen'] = []
    json.dump(data, json_file)

def get_uid(token):
    with open("tokens.json", "r") as fh:
        data = json.load(fh)
        values = list(data.values())
        keys = list(data.keys())
        return keys[values.index(token)]


def get_sorted_players():
    file_name = 'rooms/9790.json'
    with open(file_name, 'r') as file:
        file_data = json.load(file)
    players = file_data['players']
    players.sort(key=lambda item: -item['score'])
    file_data['players'] = players
    print(file_data)


print(len("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwbGF5ZXJfdWlkIjoiZDUxMTQ1ZWYyM2NlNzc1MSIsImV4cCI6MTY4Njg2NzI4OX0.8fYYiRi09qCH9RTuHYNOR4KEd2U_LPCT9adRL5tiVSw"))
