#!/usr/bin/env python3
#coding: utf-8

from flask import jsonify
from flask import Flask
from flask import request
from flask import abort

app = Flask(__name__)

def test():
    result = '''{
        "action": "aaaaa",
        "params": {
            "min_speak_ms": "江冠斌"
            }
        }
        '''
    return result

@app.route("/hello", methods=['GET','POST'])
def hello():
    req = request.get_json()
    app.logger.error("requ:{}".format(req))
    app.logger.error("test:{}".format(test()))
    return  test()


if __name__ == '__main__':
    host = "0.0.0.0"
    port = 9999
    app.run( port=port, debug=True)
