from web3 import Web3
from solcx import compile_source
from web3.middleware import geth_poa_middleware
import os

infura_url = os.getenv('INFURA_URL')
private_key = os.getenv('PRIVATE_KEY')
account_address = os.getenv('ACCOUNT_ADDRESS')

w3 = Web3(Web3.HTTPProvider(infura_url))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

assert w3.isConnected(), "Failed to connect to Ethereum node."

contract_source_code = '''
pragma solidity ^0.8.0;

contract DelayedAction {
    event ActionScheduled(uint256 actionId, address scheduledBy, uint256 dueTime);
    event ActionExecuted(uint256 actionId, address executedBy);

    struct Action {
        uint256 id;
        address scheduledBy;
        uint256 dueTime;
    }

    uint256 public nextActionId;
    mapping(uint256 => Action) public actions;

    function scheduleAction(uint256 dueTime) external returns (uint256) {
        uint256 actionId = nextActionId++;
        actions[actionId] = Action(actionId, msg.sender, dueTime);
        emit ActionScheduled(actionId, msg.sender, dueTime);
        return actionId;
    }

    function executeAction(uint256 actionId) external {
        require(block.timestamp >= actions[actionId].dueTime, "Action not due yet");
        emit ActionExecuted(actionId, msg.sender);
    }
}
'''

compiled_sol = compile_source(contract_source_code, output_values=["abi", "bin"])
contract_id, contract_interface = compiled_sol.popitem()

abi = contract_interface['abi']
bytecode = contract_interface['bin']

def deploy_contract():
    account = w3.eth.account.privateKeyToAccount(private_key)
    w3.eth.defaultAccount = account.address
    
    DelayedAction = w3.eth.contract(abi=abi, bytecode=bytecode)
    construct_txn = DelayedAction.constructor().buildTransaction({
        'from': account.address,
        'nonce': w3.eth.getTransactionCount(account.address),
        'gas': 4000000,
        'gasPrice': w3.toWei('20', 'gwei')
    })

    signed_txn = account.sign_transaction(construct_txn)

    tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    return tx_receipt.contractAddress

def schedule_action(contract_address, due_time):
    account = w3.eth.account.privateKeyToAccount(private_key)
    contract = w3.eth.contract(address=contract_address, abi=abi)
    
    transaction = contract.functions.scheduleAction(due_time).buildTransaction({
        'from': account.address,
        'nonce': w3.eth.getTransactionCount(account.address),
        'gas': 400000,
        'gasPrice': w3.toWei('20', 'gwei')
    })
    
    signed_txn = account.sign_transaction(transaction)
    tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    return w3.eth.waitForTransactionReceipt(tx_hash)

def execute_action(contract_address, action_id):
    account = w3.eth.account.privateKeyToAccount(private_key)
    contract = w3.eth.contract(address=contract_address, abi=abi)
    
    transaction = contract.functions.executeAction(action_id).buildTransaction({
        'from': account.address,
        'nonce': w3.eth.getTransactionCount(account.address),
        'gas': 400000,
        'gasPrice': w3.toWei('20', 'gwei')
    })
    
    signed_txn = account.sign_transaction(transaction)
    tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    return w3.eth.waitForTransactionReceipt(tx_hash)