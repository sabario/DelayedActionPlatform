pragma solidity ^0.8.0;

contract DelayedActions {
    struct Action {
        bytes data;
        uint256 timestamp;
    }

    mapping(uint256 => Action) public actions;
    uint256 public nextActionId;

    event ActionScheduled(uint256 indexed actionId, uint256 timestamp, bytes data);
    event ActionExecuted(uint256 indexed actionId, address indexed executor, bytes result);

    function scheduleAction(uint256 _timestamp, bytes calldata _data) external returns (uint256 actionId) {
        require(_timestamp > block.timestamp, "Timestamp must be in the future");

        actionId = nextActionId++;
        actions[actionId] = Action({
            data: _data,
            timestamp: _timestamp
        });

        emit ActionScheduled(actionId, _timestamp, _data);
    }

    function executeAction(uint256 actionId) external {
        Action storage action = actions[actionId];
        require(action.timestamp != 0, "Action not found");
        require(block.timestamp >= action.timestamp, "Action cannot be executed yet");

        bytes memory data = action.data;
        delete actions[actionId];

        (bool success, bytes memory result) = address(this).delegatecall(data);
        require(success, "Action failed");

        emit ActionExecuted(actionId, msg.sender, result);
    }
}