import json
import os
import requests
from flask import render_template, redirect, request,send_file
from werkzeug.utils import secure_filename
from app import app
from timeit import default_timer as timer

# Stores all the post transaction in the node
request_tx = []
#store filename
files = {}
#destiantion for upload files
UPLOAD_FOLDER = "app/static/Uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# store  address
ADDR = "http://127.0.0.1:8800"


#create a list of requests that peers has send to upload files
def get_tx_req():
    global request_tx
    chain_addr = "{0}/chain".format(ADDR)
    resp = requests.get(chain_addr)
    if resp.status_code == 200:
        content = []
        chain = json.loads(resp.content.decode())
        for block in chain["chain"]:
            for trans in block["transactions"]:
                trans["index"] = block["index"]
                trans["hash"] = block["prev_hash"]
                content.append(trans)
        request_tx = sorted(content,key=lambda k: k["hash"],reverse=True)


# Loads and runs the home page
@app.route("/")
def index():
    get_tx_req()
    return render_template("index.html",title="FileStorage",subtitle = "A Decentralized Network for File Storage/Sharing",node_address = ADDR,request_tx = request_tx)

@app.route("/submit", methods=["POST"])
def submit():
    start = timer()
    user = request.form["user"]
    up_file = request.files["v_file"]

    if up_file:  # Ensure a file was uploaded
        # Prepare the file path
        file_path = os.path.join(app.root_path, "static", "Uploads", secure_filename(up_file.filename))
        print(f"Saving file to: {file_path}")

        # Save the uploaded file
        up_file.save(file_path)
        print(f"File saved: {file_path}")

        # Add the file to the list to create a download link
        files[up_file.filename] = file_path

        # Determine the size of the file uploaded in bytes
        file_states = os.stat(files[up_file.filename]).st_size

        # Create a transaction object
        post_object = {
            "user": user,  # user name
            "v_file": up_file.filename,  # filename
            "file_data": str(up_file.stream.read()),  # file data
            "file_size": file_states  # file size
        }

        # Submit a new transaction
        address = f"{ADDR}/new_transaction"
        requests.post(address, json=post_object)
    else:
        print("No file uploaded!")

    end = timer()
    print(end - start)
    return redirect("/")

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    # Logic to find the file and send it
    return send_file(filename, as_attachment=True)