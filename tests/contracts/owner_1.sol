// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;
contract Owner {

    address public owner;
    mapping(address => bool) public admins;
    mapping(address => uint) public balances;
    uint public totalSupply;

    constructor(address _owner){
        owner = _owner;
    }

    function msgSender() public view returns (address){
        address aa = msg.sender;
        return  aa;
    }

    function getOwner() public view returns (address){
        return owner;
    }

    function getFakeOwner(address addr) public pure returns (address){
        return addr;
    }

    modifier onlyOwner {
        require(msg.sender == owner, "Only owner can do this");
        _;
    }

    modifier onlyAdmin {
        require(admins[msgSender()], "Only admin can do this");
        _;
    }
    //TODO: 作为例子
    function transferOwnership(address newOwner) onlyOwner public {
        owner = newOwner;
    }

    function transferOwnership2(address newOwner) public {
        require(newOwner != address(0) && owner == msgSender(), "Owner cannot be 0x0 and only owner can do this");
        owner = newOwner;
    }

    function setAdmin(address _admin) onlyAdmin public {
        admins[_admin] = true;
    }


    function transferOwnership3(address newOwner) public {
        address fake_owner = getFakeOwner(newOwner);
        require(fake_owner == msgSender(), "Only owner can do this");
        owner = newOwner;
    }

/*
    

    function t3(address newOwner) public {

        address fake_owner = getFakeOwner(newOwner);
        require(fake_owner == msgSender(), "Only owner can do this");
        owner = newOwner;
        address t_owner = owner;
        require(t_owner == msgSender(), "Only owner can do this");
        
        owner = newOwner;
    } 


   
   
    function mint(uint _amount) onlyAdmin public {
        _amount = _amount + 1;
        totalSupply += _amount;
    }

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw(uint _amount) public {
        require(_amount <= balances[msg.sender], "Not enough balance");
        balances[msg.sender] -= _amount;
    }*/ 
}