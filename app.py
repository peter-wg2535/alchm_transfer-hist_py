from flask import Flask, jsonify, render_template, request
from forms import DataTriggerForm
import os
import json
from web3 import Web3
import requests
from dotenv import dotenv_values

config_values= dotenv_values(dotenv_path='.env')
ALCHEMY_MAIN_KEY = config_values['ALCHEMY_MAIN_KEY']
# Provideer_URL
provider_url='https://eth-mainnet.alchemyapi.io/v2/'+ALCHEMY_MAIN_KEY

# initiialize web 3  
w3 = Web3(Web3.HTTPProvider(provider_url))

# includes the standard ERC20 ABI info
# load json from file is best way
json_abi='[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_from","type":"address"},{"indexed":true,"name":"_to","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_owner","type":"address"},{"indexed":true,"name":"_spender","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Approval","type":"event"}]'
ERC20_ABI = json.loads(json_abi)  # noqa: 501

# configures web3 to point towards the AKITA token address
XToken_ADDRESS = '0x3301Ee63Fb29F863f2333Bd4466acb46CD8323E6'
AAcount_ADDRESS = '0xde21F729137C5Af1b01d73aF1dC21eFfa2B8a0d6'
xtoken = w3.eth.contract(address=XToken_ADDRESS, abi=ERC20_ABI)

app = Flask(__name__,template_folder='templates')


SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


def get_block_num():
    return str(w3.eth.get_block('latest')['number'])

def get_abc_xyz_bal():
    return str(xtoken.functions.balanceOf(AAcount_ADDRESS).call())

def get_total_xtoken():

    json_request={
        "jsonrpc": "2.0","id": 0,"method": "alchemy_getAssetTransfers",
        "params": [
            {"fromBlock": "0xC30965","toBlock": "latest",
            "fromAddress": "0xde21F729137C5Af1b01d73aF1dC21eFfa2B8a0d6",
            "toAddress": "0xDead000000000000000000000000000000000d06",
            "contractAddresses": ["0x3301Ee63Fb29F863f2333Bd4466acb46CD8323E6"],
            "category": ["external","token"]}]
    }

    data = requests.post( url=provider_url, json=json_request)
    json_response = data.json()

    items=json_response['result']['transfers']
    transfer_nums = len(items)
    burned = 0
    for i in range(transfer_nums):
        burned = burned + items[i]['value']
    return burned



@app.route('/', methods=['GET', 'POST'])
def refresh():
    #num1 = None
    block_num = get_block_num()
    balance = get_abc_xyz_bal()
    total_tokens = get_total_xtoken()

    form = DataTriggerForm()

    if request.method == 'POST':
        #num1 = form.num1.data
        block_num = get_block_num()
        balance = get_abc_xyz_bal()
        total_tokens = get_total_xtoken()

    return render_template('index.html', form=form, bal=balance, block_num=block_num, total_tokens=total_tokens)

def call_chainlink_abi(config_values):
    ALCHEMY_RINKEBY_KEY = config_values['ALCHEMY_RINKEBY_KEY']
    provider_url='https://eth-rinkeby.alchemyapi.io/v2/'+ALCHEMY_RINKEBY_KEY
    w3_test = Web3(Web3.HTTPProvider(provider_url))

    with open("chainlink_rinkeby_abi.json","r") as file:
      x = json.load(file)
      link_abi=x["result"]
      link_token = w3_test.eth.contract(address='0x01BE23585060835E02B77ef475b0Cc51aA1e0709', abi=link_abi)
      link_bal=str(link_token.functions.balanceOf("0x9130aC7AeB7e74E7C3fc64B315DbD0EcAFe69e63").call())
      print(link_bal)

if __name__ == '__main__':

    #call_chainlink_abi(config_values)



   app.run(debug=True)

   #type  cmd flask run

#  print("=========Block-Num===============")
#  print(get_block_num())
#  print("=========Balance=================")
#  print(get_abc_xyz_bal())
#  print("=========Toknen==================")
#  print(get_total_xtoken())