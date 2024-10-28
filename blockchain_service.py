pragma solidity ^0.8.0;

contract DelayedActionContract {
    event ActionScheduled(uint256 indexed actionId, address indexed scheduledBy, uint256 dueTime);
    event ActionExecuted(uint256 indexed actionId, address executedBy);
    event ActionCancelled(uint256 indexed actionId, address cancelledBy);

    struct ScheduledAction {
        uint256 id;
        address initiator;
        uint256 executionTime;
        bool isCancelled;
    }

    uint256 public nextActionId = 0;
    mapping(uint256 => ScheduledAction) public scheduledActions;

    function scheduleNewAction(uint256 executionTime) external returns (uint256) {
        uint256 currentActionId = nextActionId++;
        scheduledActions[currentActionId] = ScheduledAction(currentActionId, msg.sender, executionTime, false);
        emit ActionScheduled(currentActionId, msg.sender, executionTime);
        return currentActionId;
    }

    function executeScheduledAction(uint256 actionId) external {
        require(block.timestamp >= scheduledActions[actionId].executionTime, "Scheduled action is not due yet.");
        require(!scheduledActions[actionId].isCancelled, "Scheduled action has already been cancelled.");
        emit ActionExecuted(actionId, msg.sender);
    }

    function cancelScheduledAction(uint256 actionId) external {
        require(msg.sender == scheduledActions[actionId].initiator, "Only the initiator can cancel this action.");
        require(!scheduledActions[actionId].isCancelled, "Scheduled action is already cancelled.");
        scheduledActions[actionId].isCancelled = true;
        emit ActionCancelled(actionId, msg.sender);
    }
}
```
```python
from web3 import Web3
from solcx import compile_source
from web3.middleware import geth_poa_middleware
import os

infura_url = os.getenv('INFURA_URL')
private_key = os.getenv('PRIVATE_KEY')
account_address = os.getenv('ACCOUNT_ADDRESS')

w3 = Web3(Web3.HTTPProvider(infura_url))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
assert w3.isConnected(), "Failed to connect to the Ethereum network."

contract_source_code = '''
/* Solidity code block */
'''

compiled_sol = compile_source(contract_source_code, output_values=["abi", "bin"])
contract_identifier, contract_interface = compiled_sol.popitem()

abi = contract_interface['abi']
bytecode = contract_interface['bin']

def send_transaction(contract_function_name, *args, **kwargs):
    user_account = w3.eth.account.privateKeyToAccount(private_key)
    contract_address = kwargs.get("contract_address")
    contract = w3.eth.contract(address=contract_address, abi=abi)
    
    function_invocation = getattr(contract.functions, contract_function_name)(*args)
    tx_parameters = {
        'from': user_account.address,
        'nonce': w3.eth.getTransactionCount(user_account.address),
        'gas': 400000,
        'gasPrice': w3.toWei('20', 'gwei')
    }
    
    prepared_tx = function_invocation.buildTransaction(tx_parameters)
    
    signed_tx = user_account.sign_transaction(prepared_tx)
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    return w3.eth.waitForTransactionReceipt(tx_hash)
    
def deploy_contract():
    contract_deployment_receipt = send_transaction('constructor', contract_address=None)
    return contract_deployment_receipt.contractAddress

def schedule_new_action(contract_addr, execution_time):
    return send_transaction('scheduleNewAction', execution_time, contract_address=contract_addr)

def execute_scheduled_action(contract_addr, action_id):
    return send_transaction('executeScheduledAction', action_id, contract_address=contract_addr)

def cancel_scheduled_action(contract_addr, action_id):
    return send_transaction('cancelScheduledAction', action_id, contract_address=contract_addr)

if __name__ == "__main__":
    contract_addr = deploy_contract()
    print(f"Contract deployed at: {contract_addr}")
    
    future_execution_time = 1672531200  # Specific future timestamp
    
    scheduling_receipt = schedule_new_action(contract_addr, future_execution_time)
    action_id = scheduling_receipt.logs[0]['topics'][1]
    print(f"Scheduled action ID: {int(action_id.hex(), 16)}")
    
    cancelling_receipt = cancel_scheduled_action(contract_addr, int(action_id.hex(), 16))
    print(f"Cancelled action with TX hash: {cancelling_receipt.transactionHash.hex()}")