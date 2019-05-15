from flask import Flask, jsonify, request, render_template
from web3 import Web3, IPCProvider, Account
from web3.middleware import geth_poa_middleware

# abi is changin when you change contract
ABI =  [{'constant': False, 'inputs': [{'name': 'data', 'type': 'string'}], 'name': 'enqueue', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': False, 'inputs': [], 'name': 'lenght', 'outputs': [{'name': '', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': False, 'inputs': [{'name': 'position', 'type': 'uint256'}], 'name': 'get_patient', 'outputs': [{'name': '', 'type': 'string'}], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': True, 'inputs': [{'name': '', 'type': 'uint256'}], 'name': 'receptionistAccts', 'outputs': [{'name': '', 'type': 'address'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': False, 'inputs': [], 'name': 'dequeue', 'outputs': [{'name': 'data', 'type': 'string'}], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': False, 'inputs': [], 'name': 'greet', 'outputs': [{'name': 'greet', 'type': 'string'}], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}]
# addres change when you deploy contract (if you not reset blockchain, old contract exists)
ADDRESS = '0xcc2b57418d1CA582D757d6F9b39Dd53817FA70B7'

app = Flask(__name__, template_folder='./templates')

def connect_to_blockchain():
    w3 = Web3(IPCProvider(ipc_path='/tmp/geth.ipc', testnet=True))
    w3.middleware_stack.inject(geth_poa_middleware, layer=0)
    queue = w3.eth.contract(address=ADDRESS, abi=ABI)
    print('Default contract greeting: {}'.format(
        queue.functions.greet().call()
    ))

    return w3, queue

def add_patient_to_queue(patient):
    tx_hash = queue.functions.enqueue(patient).transact()
    w3.eth.waitForTransactionReceipt(tx_hash)


def read_all_patient():
    patients = []
    lenght = queue.functions.lenght().call()
    print(lenght)

    for i in range(lenght+1):
        patients.append(queue.functions.get_patient(i).call())

    return patients

@app.route('/')
def index():
    return render_template('index.html', node_identifier=1, node_money=1), 200

@app.route('/list_patients', methods=['GET'])
def list_patients():
    return render_template('list_patients.html', patients=read_all_patient()), 200

@app.route('/add_patient', methods=['GET'])
def add_patient_form():
    return render_template('add_patient.html'), 200

@app.route('/add_patient', methods=['POST'])
def add_patient():
    values = request.form

    # Check that the required fields are in the POST'ed data
    required = ['patient_name']
    if not all(k in values for k in required):
        return 'Missing values', 400

    patient_name = values['patient_name']
    add_patient_to_queue(patient_name)

    return render_template('index.html', response='OK'), 201


w3, queue = connect_to_blockchain()
w3.eth.defaultAccount = w3.eth.accounts[0]

app.run(host='0.0.0.0', port=5000)