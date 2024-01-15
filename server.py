from flask import Flask, Response, request
import json
import base64
import os
import zipfile
import tempfile
import shutil

app = Flask(__name__)

state = {
    "token": os.getenv("ADMIN_TOKEN"),
    "filters": [],
}

try:
    os.mkdir("onions")
except FileExistsError:
    pass


def success_response(fields={}) -> Response:
    return Response(json.dumps({"success": True} | fields), 200)


def error_response(message, code=500) -> Response:
    return Response(json.dumps({"success": False, "message": message}), code)


def not_implemented_response() -> Response:
    return error_response("Not implemented", 501)


@app.route("/status")
def get_status():
    return success_response({"status": "ok"})


@app.route("/filters", methods=["POST", "GET"])
def manage_filters():
    if request.method == "POST":
        if "token" not in request.form or state["token"] != request.form["token"]:
            return error_response("Unauthorized")
        state["filters"] = request.form["filters"].split(",")
        return success_response()
    # GET
    return success_response({"filters": state["filters"]})


@app.route("/found", methods=["POST"])
def found_onion():
    # TODO get onion from request, unpackage
    zip_content = base64.b64decode(request.json["zipfile"].encode())
    with tempfile.TemporaryDirectory() as tempdir:
        os.mkdir(f"{tempdir}/onion")
        with open(f"{tempdir}/onion.zip", "wb") as f:
            f.write(zip_content)
        with zipfile.ZipFile(f"{tempdir}/onion.zip", "r") as zf:
            zf.extractall(f"{tempdir}/onion")
        # TODO validate onion keys work
        with open(f"{tempdir}/onion/hostname", "r") as f:
            onion_name = f.read().strip()
        try:
            shutil.move(f"{tempdir}/onion", f"./onions/{onion_name}")
        except shutil.Error as e:
            if "already exists" not in str(e):
                return error_response("Failed to save key")
            print(f"Got an onion that has already been found: {onion_name}")
        # TODO possibly alert administrator of found onion
    return success_response()


@app.route("/")
def index():
    return f"""
        <form method="post" action="/filters">
            <label for="token">Token:</label>
            <input type=text name=token label="test">
            <label for="filters">Filters:</label>
            <textarea rows="3" name="filters">{",".join(state["filters"])}</textarea>
            <input type=submit value=Submit>
        </form>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
