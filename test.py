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

print(get_uid('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwbGF5ZXJfdWlkIjoiMWI1NDI4ZWRlNGI2OTQ1OSIsImV4cCI6MTY4NjI1NzM5Mn0.JwNPlrdQ0trFUcWqi9T0gIZqBAeAsMomcHBr11Zty4Y'))

