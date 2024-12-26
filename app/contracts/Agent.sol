// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

interface IPancakeRouter {
    function swapExactETHForTokens(
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external payable returns (uint256[] memory amounts);

    function swapExactTokensForETH(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts);

    function swapExactTokensForTokens(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts);
}

contract Agent {
    address public owner;
    address public authorizedBackend; // 后端地址，用于执行量化交易
    IPancakeRouter public pancakeRouter;
    address public WBNB;

    uint256 public contractETHBalance;

    // 记录每个用户的 ETH 和 ERC20 代币余额
    mapping(address => uint256) public userETHBalances; // 用户地址 => ETH余额
    mapping(address => mapping(address => uint256)) public userTokenBalances; // 用户地址 => 代币地址 => 余额

    modifier onlyOwner() {
        require(msg.sender == owner, "Not the contract owner");
        _;
    }

    modifier onlyAuthorizedBackend() {
        require(msg.sender == authorizedBackend, "Not authorized backend");
        _;
    }

    event OwnershipTransferred(
        address indexed previousOwner,
        address indexed newOwner
    );
    event AuthorizedBackendChanged(
        address indexed previousBackend,
        address indexed newBackend
    );
    event TradeExecuted(
        address indexed user,
        uint256 amountIn,
        address[] path,
        uint256[] amounts
    );
    event TokenBalanceUpdated(
        address indexed user,
        address indexed token,
        uint256 newBalance
    );
    event ETHBalanceUpdated(address indexed user, uint256 newBalance);

    constructor(
        address _owner,
        address _authorizedBackend,
        address _pancakeRouter,
        address _WBNB
    ){
        owner = _owner;
        authorizedBackend = _authorizedBackend;
        pancakeRouter = IPancakeRouter(_pancakeRouter);
        WBNB = _WBNB;
    }

    // 转移合约所有权
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "New owner is the zero address");
        emit OwnershipTransferred(owner, newOwner);
        owner = newOwner;
    }

    // 修改后端授权地址
    function setAuthorizedBackend(address newBackend) external onlyOwner {
        require(
            newBackend != address(0),
            "New backend address is the zero address"
        );
        emit AuthorizedBackendChanged(authorizedBackend, newBackend);
        authorizedBackend = newBackend;
    }

    // 存入 ETH
    function depositETH() external payable {
        require(msg.value > 0, "Amount must be greater than zero");
        contractETHBalance += msg.value;
        userETHBalances[msg.sender] += msg.value; // 更新用户的ETH余额

        emit ETHBalanceUpdated(msg.sender, userETHBalances[msg.sender]);
    }

    // 存入 ERC20 代币
    function depositERC20(address tokenAddress, uint256 amount) external {
        require(amount > 0, "Amount must be greater than zero");
        IERC20 token = IERC20(tokenAddress);
        // 确保用户已经批准了代币转账
        token.transferFrom(msg.sender, address(this), amount);
        userTokenBalances[msg.sender][tokenAddress] += amount;

        emit TokenBalanceUpdated(
            msg.sender,
            tokenAddress,
            userTokenBalances[msg.sender][tokenAddress]
        );
    }

    // 提取 ETH
    function withdrawETH(uint256 _amount) external {
        // 检查用户余额是否足够
        require(
            _amount > 0 && _amount <= userETHBalances[msg.sender],
            "Invalid withdrawal amount"
        );

        // 更新用户余额和合约余额
        userETHBalances[msg.sender] -= _amount;
        contractETHBalance -= _amount;

        // 执行转账
        payable(msg.sender).transfer(_amount);

        // 触发事件
        emit ETHBalanceUpdated(msg.sender, userETHBalances[msg.sender]);
    }

    // 提取 ERC20 代币
    function withdrawERC20(address tokenAddress, uint256 amount) external {
        // 检查用户的代币余额是否足够
        require(
            userTokenBalances[msg.sender][tokenAddress] >= amount,
            "Insufficient balance"
        );

        // 更新用户的代币余额
        userTokenBalances[msg.sender][tokenAddress] -= amount;

        // 执行转账
        IERC20(tokenAddress).transfer(msg.sender, amount);

        // 触发事件
        emit TokenBalanceUpdated(
            msg.sender,
            tokenAddress,
            userTokenBalances[msg.sender][tokenAddress]
        );
    }

    // 执行交易：ETH -> Token（由合约调用 Uniswap 并更新到指定用户）
    function swapETHForTokens(
        address user, // 交易对应的用户
        uint256 amountOutMin,
        address[] calldata path,
        uint256 deadline
    ) external payable onlyAuthorizedBackend {
        require(user != address(0), "Invalid user address");
        require(path[0] == WBNB, "Path must start with WBNB");
        require(userETHBalances[user] >= msg.value, "Insufficient ETH balance"); // 确保用户有足够的ETH余额

        // 调用 Uniswap 进行交易
        uint256[] memory amounts = pancakeRouter.swapExactETHForTokens{
            value: msg.value
        }(amountOutMin, path, address(this), deadline);

        // 更新用户的 ETH 余额
        userETHBalances[user] -= msg.value;
        contractETHBalance -= msg.value;

        // 更新用户的 Token 余额
        address tokenAddress = path[path.length - 1];
        uint256 tokenAmount = amounts[amounts.length - 1];
        userTokenBalances[user][tokenAddress] += tokenAmount;

        emit TradeExecuted(user, msg.value, path, amounts);
        emit ETHBalanceUpdated(user, userETHBalances[user]);
        emit TokenBalanceUpdated(
            user,
            tokenAddress,
            userTokenBalances[user][tokenAddress]
        );
    }

    // 执行交易：Token -> ETH（由合约调用 Uniswap 并更新到指定用户）
    function swapTokensForETH(
        address user, // 交易对应的用户
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        uint256 deadline
    ) external onlyAuthorizedBackend {
        require(user != address(0), "Invalid user address");
        require(path[path.length - 1] == WBNB, "Path must end with WBNB");
        require(
            userTokenBalances[user][path[0]] >= amountIn,
            "Insufficient token balance"
        );

        // 授权 Uniswap 代币额度
        IERC20(path[0]).approve(address(pancakeRouter), amountIn);

        // 调用 Uniswap 进行交易
        uint256[] memory amounts = pancakeRouter.swapExactTokensForETH(
            amountIn,
            amountOutMin,
            path,
            address(this),
            deadline
        );

        // 交易成功后更新余额
        uint256 ethAmount = amounts[amounts.length - 1]; // 获得的 ETH 数量
        userETHBalances[user] += ethAmount;
        contractETHBalance += ethAmount;
        userTokenBalances[user][path[0]] -= amountIn;

        emit TradeExecuted(user, amountIn, path, amounts);
        emit TokenBalanceUpdated(
            user,
            path[0],
            userTokenBalances[user][path[0]]
        );
        emit ETHBalanceUpdated(user, userETHBalances[user]);
    }

    // 执行交易：Token -> Token（由合约调用 Uniswap 并更新到指定用户）
    function swapTokensForTokens(
        address user, // 交易对应的用户
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        uint256 deadline
    ) external onlyAuthorizedBackend {
        require(user != address(0), "Invalid user address");
        require(
            userTokenBalances[user][path[0]] >= amountIn,
            "Insufficient token balance"
        );

        // 授权 Uniswap 代币额度并调用交易
        IERC20(path[0]).approve(address(pancakeRouter), amountIn);
        uint256[] memory amounts = pancakeRouter.swapExactTokensForTokens(
            amountIn,
            amountOutMin,
            path,
            address(this),
            deadline
        );

        // 更新用户的目标 Token 余额
        uint256 tokenAmount = amounts[amounts.length - 1];
        address targetToken = path[path.length - 1];
        userTokenBalances[user][targetToken] += tokenAmount;

        // 更新用户的源 Token 余额
        userTokenBalances[user][path[0]] -= amountIn;

        emit TradeExecuted(user, amountIn, path, amounts);
        emit TokenBalanceUpdated(
            user,
            path[0],
            userTokenBalances[user][path[0]]
        );
        emit TokenBalanceUpdated(
            user,
            targetToken,
            userTokenBalances[user][targetToken]
        );
    }

    // 查询 Token 余额
    function getTokenBalance(
        address tokenAddress
    ) external view returns (uint256) {
        return userTokenBalances[msg.sender][tokenAddress];
    }

    // 查询 ETH 余额
    function getETHBalance() external view returns (uint256) {
        return userETHBalances[msg.sender];
    }

    // 合约接收 ETH
    receive() external payable {}
}
