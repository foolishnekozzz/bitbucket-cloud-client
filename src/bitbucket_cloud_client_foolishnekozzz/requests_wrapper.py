import requests, json

class ERROR:
    get_error = 550
    put_error = 551
    post_error = 552
    delete_error = 553

def get(URL, authen):
    res = "{}"
    code = ERROR.get_error
    try:
        response = requests.get(URL, auth=authen)
        res = response.text
        code = response.status_code
        return json.loads(response.text), response.status_code

    except Exception as e:
        return str(e) + "\n" + res, code

def put(URL, authen, data):
    res = "{}"
    code = ERROR.put_error
    try:
        response = requests.put(URL, auth=authen, data=data)
        res = response.text
        code = response.status_code
        return json.loads(response.text), response.status_code

    except Exception as e:
        return str(e) + "\n" + res, code

def delete(URL, authen):
    res = "{}"
    code = ERROR.delete_error
    try:
        response = requests.delete(URL, auth=authen)
        res = response.text
        code = response.status_code
        return json.loads(response.text), response.status_code

    except Exception as e:
        return str(e) + "\n" + res, code

def post(URL, authen, data):
    res = "{}"
    code = ERROR.post_error
    try:
        response = requests.post(URL, auth=authen, data=data)
        res = response.text
        code = response.status_code
        return json.loads(response.text), response.status_code

    except Exception as e:
        return str(e) + "\n" + res, code

def print_response(msg, returncode):
    _str = "-"*20
    if returncode in [200, 204]:
        print(f"INFO:\n{_str}")
        print(returncode)
        print("-"*20)
    else:
        print(f"ERROR:\n{_str}")
        print(returncode)
        print(msg)
        print("-"*20)