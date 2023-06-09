import json
import os
from random import randint, choice
from flask import Flask, request, redirect, session, jsonify, make_response
from websockets.sync.client import connect
import config
import jwt
import datetime
from functools import wraps

app = Flask(__name__, static_url_path='/static', static_folder='output')

#Secret Key
app.secret_key = config.SECRET_KEY
room_list = []
# app.permanent_session_lifetime = datetime.timedelta(days=1)
# session.permanent = True


def load_name():
    with open("promts.json", "r") as fh:
        return json.load(fh)['already_gen']


def get_uid(token):
    with open("tokens.json", "r") as fh:
        data = json.load(fh)
        values = list(data.values())
        keys = list(data.keys())
        return keys[values.index(token)]


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'a valid token is missing'})
        try:
            uid = get_uid(token)
        except:
            return jsonify({'message': 'token is invalid'})

        return f(uid, *args, **kwargs)

    return decorator


@app.route('/', methods=['GET'])
def index():
    return 'hello'


@app.route('/get_token/<string:uid>', methods=['POST'])
def get_token(uid):
    with open("tokens.json", "r") as fh:
        data = json.load(fh)
    if uid not in data:
        token = jwt.encode({'player_uid': uid, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=45)},
            app.config['SECRET_KEY'], "HS256")
        with open("tokens.json", "r") as fh:
            data = json.load(fh)

        with open("tokens.json", 'w') as json_file:
            data[uid] = token
            json.dump(data, json_file)
        return jsonify({'token': token})
    return make_response('could not verify', 401, {'Authentication': '"login required"'})


@app.route('/create/<string:player_name>_and_<int:avatar_id>', methods=['GET', 'POST'])
@token_required
def create(uid, player_name, avatar_id):
    if request.method == 'GET':
        room_id = randint(1000, 9999)
        while room_id in room_list:
            room_id = randint(1000, 9999)
        room_list.append(room_id)
        cards = {}
        for i in range(4):
            pic = choice(load_name())
            while pic in cards.keys():
                pic = choice(load_name())
            cards[pic] = []
        aDict = {"sid": room_id,
                 "players": [
                     {'player_uid': uid,
                      "name": player_name,
                      'score': 0,
                      'avatar_id': avatar_id}],
                 'cards': cards,
                 'stage_game': 'paintWaiting'
                 }
        jsonString = json.dumps(aDict)
        file_name = "./rooms/" + str(room_id) + ".json"
        jsonFile = open(file_name, "w")
        jsonFile.write(jsonString)
        jsonFile.close()
        return jsonify(aDict)


# @app.route('/join/<string:player_name>_and_<int:avatar_id>', methods=['GET'])
# def join(player_name, avatar_id):
#     if request.method == 'GET':
#         session['player_name'] = player_name
#         session['avatar_id'] = avatar_id
#     return "1"


@app.route('/join_room/<string:player_name>_<int:avatar_id>_<int:sid>', methods=['GET'])
@token_required
def join_room(uid, player_name, avatar_id, sid):
    if check_room(sid) != True:
        return jsonify({'code': -1})

    file_name = 'rooms/' + str(sid) + ".json"

    with open(file_name) as json_file:
        data = json.load(json_file)

    new_data = {"player_uid": uid,
                "name": player_name,
                'score': 0,
                'avatar_id': avatar_id}

    with open(file_name, 'r+') as file:
        file_data = json.load(file)
        file_data["players"].append(new_data)
        file.seek(0)
        json.dump(file_data, file, indent=4)

    message = '{"sid": "'+str(sid)+'", "newPlayer": {"player_uid": "'+uid+'", "name":"'+player_name+'", "iconId":"'+str(avatar_id)+'", "score":"0"}}'
    with connect(config.socket_url) as websocket:
        websocket.send(message)

    return jsonify(file_data)


# @app.route('/room_<int:sid>')
# def room(sid):
#     file_name = 'rooms/' + str(sid) + ".json"
#     with open(file_name) as json_file:
#         data = json.load(json_file)
#
#     return jsonify(data)


def check_room(room_id):
    path_to_json = 'rooms/'
    filename = str(room_id) + ".json"
    json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
    if filename in json_files:
        return True
    return False


game_stage = {
    0: 'paintWaiting',
    1: 'paintDescrition',
    2: 'answerChoose',
    3: 'liderBoard'
}


@app.route('/room_<int:sid>/<int:stage>', methods=['POST'])
@token_required
def change_stage(uid, sid, stage):
    file_name = 'rooms/' + str(sid) + ".json"
    with open(file_name, 'r') as file:
        file_data = json.load(file)
    with open(file_name, 'w') as file:
        file_data["stage_game"] = game_stage[stage]
        file.seek(0)
        json.dump(file_data, file, indent=4)
        if stage == 2:
            with connect(config.socket_url) as websocket:
                file_data['sid'] = str(file_data['sid'])
                websocket.send(json.dumps(file_data))
        else:
            message = '{"sid": "' + str(sid) + '", "GameStage": "' + file_data['stage_game'] + '"}'
            with connect(config.socket_url) as websocket:
                websocket.send(message)
    return jsonify({'status': 'ok'})


@app.route('/room_<int:sid>/stage1_<string:pic_name>_<string:phrase>', methods=['POST'])
@token_required
def stage1(uid, sid, pic_name, phrase):
    file_name = 'rooms/' + str(sid) + ".json"
    with open(file_name, 'r') as file:
        file_data = json.load(file)
    with open(file_name, 'w') as file:
        file_data["cards"][pic_name].append(phrase)
        json.dump(file_data, file)
    return '1'


# @app.route('/room_<int:sid>/stage2_<int:player_id>', methods=['GET'])
# def stage2(sid, player_id):
#     file_name = 'rooms/' + str(sid) + ".json"
#     with open(file_name) as json_file:
#         data = json.load(json_file)
#     new_data = {'player_id': player_id,
#                 'card': data['cards'][player_id - 1]}
#     return jsonify(new_data)


@app.route('/room_<int:sid>/changeScore', methods=['POST'])
@token_required
def change_score(uid, sid):
    file_name = 'rooms/' + str(sid) + ".json"
    with open(file_name, 'r') as file:
        file_data = json.load(file)
    with open(file_name, 'w') as file:
        for i in range(len(file_data['players'])):
            if file_data['players']['player_uid'] == uid:
                file_data['players']['score'] += 1
                break
        file.seek(0)
        json.dump(file_data, file)
    return jsonify({'status': 'ok'})


@app.route('/room_<int:sid>/stage3', methods=['POST'])
@token_required
def stage3(uid, sid):
    file_name = 'rooms/' + str(sid) + ".json"
    with open(file_name, 'r') as json_file:
        data = json.load(json_file)
    return data['player']


# @app.route('/reset')
# def reset():
#     print("Current game is ending.")
#     session.clear()
#     return redirect('/')


@app.route('/add_promt/<string:promt>', methods=['POST'])
@token_required
def add_promt(uid, promt):
    file_name = 'promts.json'
    with open(file_name, 'r') as json_file:
        data = json.load(json_file)

    with open(file_name, 'w') as json_file:
        data['to_gen'].append(promt)
        json.dump(data, json_file)
    return jsonify({'code': 1})


@app.route('/generation')
@token_required
def generation():
    pass


@app.route('/exit_admin_<int:sid>', methods=['GET', 'POST'])
@token_required
def exit_admin(uid, sid):
    file_name = 'rooms/' + str(sid) + ".json"
    with open(file_name, 'r+', encoding='utf-8') as json_file:
        new_data = json.load(json_file)
    os.remove(file_name)

    message = '{"sid": "'+str(new_data['sid'])+'", "status": "end_game"}'
    with connect(config.socket_url) as websocket:
        websocket.send(message)

    return jsonify({'status': 'ok'})


@app.route('/exit_player_<int:sid>', methods=['GET', 'POST'])
@token_required
def exit_player(uid, sid):
    file_name = 'rooms/' + str(sid) + ".json"
    with open(file_name, 'r+', encoding='utf-8') as json_file:
        new_data = json.load(json_file)
        for idx, obj in enumerate(new_data['players']):
            if obj['player_uid'] == uid:
                new_data['players'].pop(idx)

        json.dump(new_data, json_file, indent=4)

    with open(file_name, 'w', encoding='utf-8') as json_file:
        json_file.write(json.dumps(new_data, indent=2))

    message = '{"sid": "'+str(new_data['sid'])+'", "delPlayer": {"player_uid": "'+uid+'"}}'
    with connect(config.socket_url) as websocket:
        websocket.send(message)

    return jsonify({'status': 'ok'})


@app.route('/exit_app', methods=['POST'])
@token_required
def exit_app(uid):
    with open("tokens.json", "r") as fh:
        data = json.load(fh)

    with open("tokens.json", 'w') as json_file:
        data.pop(uid)
        json.dump(data, json_file)

    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run()
