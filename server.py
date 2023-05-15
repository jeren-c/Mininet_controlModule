from flask import Flask, request, jsonify
import threading
from middle import form_data_queue
from database import Database

app = Flask(__name__)
db = Database()

# global_data = []
@app.route('/')
def hello():
    return "Hello World"

@app.route('/api/submit', methods=['POST'])
def submit():
    # global global_data
    # print("...........")

    src_ip = request.form.get('src_ip')
    
    dst_ip = request.form.get('dst_ip')
    dst_port = request.form.get('dst_port')
    acc_auth = request.form.get('acc_auth')

    global_data = [src_ip, dst_ip, dst_port, acc_auth]
    # print(">>>>>>>>", global_data, ">>>>>>>>")
    form_data_queue.put(global_data)
    form_data = request.form.to_dict()
    db.insert_data(form_data)
    # send msg to queue

    return jsonify({'message': 'Data received successfully'})

def start_server():
    db.create_database()
    app.run(host='0.0.0.0', port=8081)
    



