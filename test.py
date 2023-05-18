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

