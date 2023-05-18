import json
import os
import openai
from random import randint, choice
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_ngrok import run_with_ngrok

app = Flask(__name__, static_url_path='/static', static_folder='pics')
run_with_ngrok(app)

#Secret Key
app.secret_key = "ferias"
room_list = []
with open("promts.json", "r") as fh:
    list_name = json.load(fh)['already_gen']

@app.route('/', methods=['GET', 'POST'])
def index():
    return 'hello'


@app.route('/create/<string:player_name>_and_<int:avatar_id>', methods=['GET', 'POST'])
def create(player_name, avatar_id):
    if request.method == 'GET':
        session['player_name'] = player_name
        session['avatar_id'] = avatar_id
        room_id = randint(1000, 9999)
        while room_id in room_list:
            room_id = randint(1000, 9999)
        room_list.append(room_id)
        cards = {}
        for i in range(4):
            pic = choice(list_name)
            while pic in cards.keys():
                pic = choice(list_name)
            cards[pic] = []
        session['sid'] = room_id
        aDict = {"sid": room_id,
                 "players": [
                     {'id': 1,
                      "name": session.get('player_name'),
                      'score': 0,
                      'avatar_id': session.get('avatar_id')}],
                 'cards': cards,
                 'stage_game': 0
                 }
        jsonString = json.dumps(aDict)
        file_name = "./rooms/" + str(room_id) + ".json"
        jsonFile = open(file_name, "w")
        jsonFile.write(jsonString)
        jsonFile.close()

        return jsonify(aDict)


@app.route('/join/<string:player_name>_and_<int:avatar_id>', methods=['GET'])
def join(player_name, avatar_id):
    if request.method == 'GET':
        session['player_name'] = player_name
        session['avatar_id'] = avatar_id
    return "1"


@app.route('/join_room/<string:player_name>_<int:avatar_id>_<int:sid>', methods=['GET'])
def join_room(player_name, avatar_id, sid):
    if check_room(sid) != True:
        return jsonify({'code': -1})

    file_name = 'rooms/' + str(sid) + ".json"

    with open(file_name) as json_file:
        data = json.load(json_file)

    session['player_id'] = len(data['players']) + 1
    new_data = {"id": session.get('player_id'),
                "name": player_name,
                'score': 0,
                'avatar_id': avatar_id}

    with open(file_name, 'r+') as file:
        file_data = json.load(file)
        file_data["players"].append(new_data)
        file.seek(0)
        json.dump(file_data, file, indent=4)

    session['sid'] = data['sid']

    return jsonify(data)


@app.route('/room_<int:sid>')
def room(sid):
    file_name = 'rooms/' + str(sid) + ".json"
    with open(file_name) as json_file:
        data = json.load(json_file)

    return jsonify(data)


def check_room(room_id):
    path_to_json = 'rooms/'
    filename = str(room_id) + ".json"
    json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
    if filename in json_files:
        return True
    return False


@app.route('/room_<int:sid>/<int:stage>')
def change_stage(sid, stage):
    file_name = 'rooms/' + str(sid) + ".json"
    with open(file_name, 'r+') as file:
        file_data = json.load(file)
        file_data["stage_game"] = stage
        file.seek(0)
        json.dump(file_data, file, indent=4)
    return "1"


@app.route('/room_<int:sid>/stage1_<string:pic_name>_<string:phrase>', methods=['POST'])
def stage1(sid, pic_name, phrase):
    file_name = 'rooms/' + str(sid) + ".json"
    with open(file_name, 'r+') as file:
        file_data = json.load(file)
        file_data["cards"][pic_name].append(phrase)
        file.seek(0)
        json.dump(file_data, file, indent=4)
    return '1'


@app.route('/room_<int:sid>/stage2_<int:player_id>', methods=['GET'])
def stage2(sid, player_id):
    file_name = 'rooms/' + str(sid) + ".json"
    with open(file_name) as json_file:
        data = json.load(json_file)
    new_data = {'player_id': player_id,
                'card': data['cards'][player_id - 1]}
    return jsonify(new_data)


@app.route('/room_<int:sid>/changeScore_<int:player_id>', methods=['POST'])
def change_score(sid, player_id):
    file_name = 'rooms/' + str(sid) + ".json"
    with open(file_name) as json_file:
        data = json.load(json_file)
    with open(file_name, 'r+') as file:
        file_data = json.load(file)
        for i in range(len(file_data['players'])):
            if file_data['players']['id'] == player_id:
                file_data['players']['score'] += 1
                break
        file.seek(0)
        json.dump(file_data, file, indent=4)


@app.route('/room_<int:sid>/stage3')
def stage3(sid):
    file_name = 'rooms/' + str(sid) + ".json"
    with open(file_name, 'r') as json_file:
        data = json.load(json_file)
    return data['player']


@app.route('/reset')
def reset():
    print("Current game is ending.")
    session.clear()
    return redirect('/')


@app.route('/add_promt/<str:promt>')
def add_promt(promt):
    file_name = 'promts.json'
    with open(file_name, 'r') as json_file:
        data = json.load(json_file)

    with open(file_name, 'w') as json_file:
        data['to_gen'].append('promt')
        json.dump(data, json_file)
    return jsonify({'code': 1})


@app.route('generation/')
def generation():
    pass


@app.route('/exit')
def exit():
    file_name = 'rooms/' + str(session['room_id']) + ".json"
    with open(file_name, 'r+', encoding='utf-8') as json_file:
        new_data = json.load(json_file)
        for idx, obj in enumerate(new_data['players']):
            if obj['name'] == session.get('player_name'):
                new_data['players'].pop(idx)

        json.dump(new_data, json_file, indent=4)

    with open(file_name, 'w', encoding='utf-8') as json_file:
        json_file.write(json.dumps(new_data, indent=2))

    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run()
