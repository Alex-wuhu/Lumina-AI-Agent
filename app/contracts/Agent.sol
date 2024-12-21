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
    address public authorizedBackend; // ��˵�ַ������ִ����������
    IPancakeRouter public pancakeRouter;
    address public WBNB;

    uint256 public contractETHBalance;

    // ��¼ÿ���û��� ETH �� ERC20 �������
    mapping(address => uint256) public userETHBalances; // �û���ַ => ETH���
    mapping(address => mapping(address => uint256)) public userTokenBalances; // �û���ַ => ���ҵ�ַ => ���

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

    // ת�ƺ�Լ����Ȩ
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "New owner is the zero address");
        emit OwnershipTransferred(owner, newOwner);
        owner = newOwner;
    }

    // �޸ĺ����Ȩ��ַ
    function setAuthorizedBackend(address newBackend) external onlyOwner {
        require(
            newBackend != address(0),
            "New backend address is the zero address"
        );
        emit AuthorizedBackendChanged(authorizedBackend, newBackend);
        authorizedBackend = newBackend;
    }

    // ���� ETH
    function depositETH() external payable {
        require(msg.value > 0, "Amount must be greater than zero");
        contractETHBalance += msg.value;
        userETHBalances[msg.sender] += msg.value; // �����û���ETH���

        emit ETHBalanceUpdated(msg.sender, userETHBalances[msg.sender]);
    }

    // ���� ERC20 ����
    function depositERC20(address tokenAddress, uint256 amount) external {
        require(amount > 0, "Amount must be greater than zero");
        IERC20 token = IERC20(tokenAddress);
        // ȷ���û��Ѿ���׼�˴���ת��
        token.transferFrom(msg.sender, address(this), amount);
        userTokenBalances[msg.sender][tokenAddress] += amount;

        emit TokenBalanceUpdated(
            msg.sender,
            tokenAddress,
            userTokenBalances[msg.sender][tokenAddress]
        );
    }

    // ��ȡ ETH
    function withdrawETH(uint256 _amount) external {
        // ����û�����Ƿ��㹻
        require(
            _amount > 0 && _amount <= userETHBalances[msg.sender],
            "Invalid withdrawal amount"
        );

        // �����û����ͺ�Լ���
        userETHBalances[msg.sender] -= _amount;
        contractETHBalance -= _amount;

        // ִ��ת��
        payable(msg.sender).transfer(_amount);

        // �����¼�
        emit ETHBalanceUpdated(msg.sender, userETHBalances[msg.sender]);
    }

    // ��ȡ ERC20 ����
    function withdrawERC20(address tokenAddress, uint256 amount) external {
        // ����û��Ĵ�������Ƿ��㹻
        require(
            userTokenBalances[msg.sender][tokenAddress] >= amount,
            "Insufficient balance"
        );

        // �����û��Ĵ������
        userTokenBalances[msg.sender][tokenAddress] -= amount;

        // ִ��ת��
        IERC20(tokenAddress).transfer(msg.sender, amount);

        // �����¼�
        emit TokenBalanceUpdated(
            msg.sender,
            tokenAddress,
            userTokenBalances[msg.sender][tokenAddress]
        );
    }

    // ִ�н��ף�ETH -> Token���ɺ�Լ���� Uniswap �����µ�ָ���û���
    function swapETHForTokens(
        address user, // ���׶�Ӧ���û�
        uint256 amountOutMin,
        address[] calldata path,
        uint256 deadline
    ) external payable onlyAuthorizedBackend {
        require(user != address(0), "Invalid user address");
        require(path[0] == WBNB, "Path must start with WBNB");
        require(userETHBalances[user] >= msg.value, "Insufficient ETH balance"); // ȷ���û����㹻��ETH���

        // ���� Uniswap ���н���
        uint256[] memory amounts = pancakeRouter.swapExactETHForTokens{
            value: msg.value
        }(amountOutMin, path, address(this), deadline);

        // �����û��� ETH ���
        userETHBalances[user] -= msg.value;
        contractETHBalance -= msg.value;

        // �����û��� Token ���
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

    // ִ�н��ף�Token -> ETH���ɺ�Լ���� Uniswap �����µ�ָ���û���
    function swapTokensForETH(
        address user, // ���׶�Ӧ���û�
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

        // ��Ȩ Uniswap ���Ҷ��
        IERC20(path[0]).approve(address(pancakeRouter), amountIn);

        // ���� Uniswap ���н���
        uint256[] memory amounts = pancakeRouter.swapExactTokensForETH(
            amountIn,
            amountOutMin,
            path,
            address(this),
            deadline
        );

        // ���׳ɹ���������
        uint256 ethAmount = amounts[amounts.length - 1]; // ��õ� ETH ����
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

    // ִ�н��ף�Token -> Token���ɺ�Լ���� Uniswap �����µ�ָ���û���
    function swapTokensForTokens(
        address user, // ���׶�Ӧ���û�
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

        // ��Ȩ Uniswap ���Ҷ�Ȳ����ý���
        IERC20(path[0]).approve(address(pancakeRouter), amountIn);
        uint256[] memory amounts = pancakeRouter.swapExactTokensForTokens(
            amountIn,
            amountOutMin,
            path,
            address(this),
            deadline
        );

        // �����û���Ŀ�� Token ���
        uint256 tokenAmount = amounts[amounts.length - 1];
        address targetToken = path[path.length - 1];
        userTokenBalances[user][targetToken] += tokenAmount;

        // �����û���Դ Token ���
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

    // ��ѯ Token ���
    function getTokenBalance(
        address tokenAddress
    ) external view returns (uint256) {
        return userTokenBalances[msg.sender][tokenAddress];
    }

    // ��ѯ ETH ���
    function getETHBalance() external view returns (uint256) {
        return userETHBalances[msg.sender];
    }

    // ��Լ���� ETH
    receive() external payable {}
}
