// SPDX-License-Identifier: MIT

pragma solidity ^0.7.0;

import "../../introspection/IERC165Upgradeable.sol";
import "../../proxy/Initializable.sol";

/**
 * https://eips.ethereum.org/EIPS/eip-214#specification
 * From the specification:
 * > Any attempts to make state-changing operations inside an execution instance with STATIC set to true will instead
 * throw an exception.
 * > These operations include [...], LOG0, LOG1, LOG2, [...]
 *
 * therefore, because this contract is staticcall'd we need to not emit events (which is how solidity-coverage works)
 * solidity-coverage ignores the /mocks folder, so we duplicate its implementation here to avoid instrumenting it
 */
contract SupportsInterfaceWithLookupMockUpgradeable is Initializable, IERC165Upgradeable {
    /*
     * bytes4(keccak256('supportsInterface(bytes4)')) == 0x01ffc9a7
     */
    bytes4 public constant INTERFACE_ID_ERC165 = 0x01ffc9a7;

    /**
     * @dev A mapping of interface id to whether or not it's supported.
     */
    mapping(bytes4 => bool) private _supportedInterfaces;

    /**
     * @dev A contract implementing SupportsInterfaceWithLookup
     * implement ERC165 itself.
     */
    function __SupportsInterfaceWithLookupMock_init() internal initializer {
        __SupportsInterfaceWithLookupMock_init_unchained();
    }

    function __SupportsInterfaceWithLookupMock_init_unchained() internal initializer {
        _registerInterface(INTERFACE_ID_ERC165);
    }

    /**
     * @dev Implement supportsInterface(bytes4) using a lookup table.
     */
    function supportsInterface(bytes4 interfaceId) public view override returns (bool) {
        return _supportedInterfaces[interfaceId];
    }

    /**
     * @dev Private method for registering an interface.
     */
    function _registerInterface(bytes4 interfaceId) internal {
        require(interfaceId != 0xffffffff, "ERC165InterfacesSupported: invalid interface id");
        _supportedInterfaces[interfaceId] = true;
    }
    uint256[49] private __gap;
}

contract ERC165InterfacesSupportedUpgradeable is Initializable, SupportsInterfaceWithLookupMockUpgradeable {
    function __ERC165InterfacesSupported_init(bytes4[] memory interfaceIds) internal initializer {
        __SupportsInterfaceWithLookupMock_init_unchained();
        __ERC165InterfacesSupported_init_unchained(interfaceIds);
    }

    function __ERC165InterfacesSupported_init_unchained(bytes4[] memory interfaceIds) internal initializer {
        for (uint256 i = 0; i < interfaceIds.length; i++) {
            _registerInterface(interfaceIds[i]);
        }
    }
    uint256[50] private __gap;
}
