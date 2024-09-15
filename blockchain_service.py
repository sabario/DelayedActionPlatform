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

def prepare_and_send_transaction(contract_function, *args, **kwargs):
    account = w3.eth.account.privateKeyToAccount(private_key)
    contract = w3.eth.contract(address=kwargs.get("contract_address", None), abi=abi)
    function_call = getattr(contract.functions, contract_function)(*args)
    
    transaction = function_call.buildTransaction({
        'from': account.address,
        'nonce': w3.eth.getTransactionCount(account.address),
        'gas': 400000,
        'gasPrice': w3.toWei('20', 'gwei')
    })
    
    signed_txn = account.sign_transaction(transaction)
    tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    return w3.eth.waitForTransactionReceipt(tx_hash)
    
def deploy_contract():
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    transaction_receipt = prepare_and_send_transaction('constructor')
    
    return transaction_receipt.contractAddress

def schedule_action(contract_address, due_time):
    return prepare_and_send_transaction('scheduleAction', due_time, contract_address=contract_address)

def execute_action(contract_address, action_id):
    return prepare_and_send_transaction('executeAction', action_id, contract_address=contract_address)

if __name__ == "__main__":
    contract_address = deploy_contract()
    print(f"Contract deployed at address: {contract_address}")
    
    due_time = 1672531200
    schedule_receipt = schedule_action(contract_address, due_time)
    print(f"Action scheduled with transaction receipt: {schedule_receipt.transactionHash.hex()}")
    
    action_id = 0
    execute_receipt = execute_action(contract_address, action_id)
    print(f"Action executed with transaction receipt: {execute_receipt.transactionHash.hex()}")