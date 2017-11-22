import datetime

from flask import Flask, request, jsonify

app = Flask(__name__)

storage = {}

HTTP_STATUS_200_OK = 200
HTTP_STATUS_404_NOT_FOUND = 404
HTTP_STATUS_409_CONFLICT = 409
HTTP_STATUS_400_BAD_REQUEST = 400


class StorageError(Exception):
    status_code = HTTP_STATUS_400_BAD_REQUEST

    def __init__(self, message, status_code=None):
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        rv = {}
        rv['error'] = self.message
        return rv


@app.errorhandler(StorageError)
def handle_invalid(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/dictionary/<key>')
def get_value(key):
    if key not in storage.keys():
        raise StorageError("key doesn't exists", HTTP_STATUS_404_NOT_FOUND)

    value = storage[key]

    status = HTTP_STATUS_200_OK
    result = value

    response = jsonify({'result': result, 'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
    response.status_code = status
    return response


@app.route('/dictionary', methods=['POST'])
def add_value():
    data_json = request.get_json()

    if not ('key' in data_json.keys() and 'value' in data_json.keys()):
        raise StorageError("bad request, you need to specify 'key' and 'value' fields")
    elif isinstance(data_json['key'], (list, dict)):
        raise StorageError("This value '{}' can't be used as a key".format(data_json['key']))
    elif data_json['key'] in storage.keys():
        raise StorageError('This key already exists', HTTP_STATUS_409_CONFLICT)

    storage[data_json['key']] = data_json['value']

    status = HTTP_STATUS_200_OK
    result = data_json

    response = jsonify({'result': result, 'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
    response.status_code = status
    return response


@app.route('/dictionary/<key>', methods=['PUT'])
def update_value(key):
    data_json = request.get_json()

    if key not in storage.keys():
        raise StorageError("key doesn't exists", HTTP_STATUS_404_NOT_FOUND)
    elif 'value' not in data_json.keys():
        raise StorageError("bad request, you need to specify 'value' field")

    storage[key] = data_json['value']

    status = HTTP_STATUS_200_OK
    result = data_json['value']

    response = jsonify({'result': result, 'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
    response.status_code = status
    return response


@app.route('/dictionary/<key>', methods=['DELETE'])
def delete_value(key):
    if key not in storage.keys():
        raise StorageError("key doesn't exists", HTTP_STATUS_404_NOT_FOUND)

    storage.pop(key)

    response = jsonify({'result': None, 'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
    response.status_code = HTTP_STATUS_200_OK
    return response
