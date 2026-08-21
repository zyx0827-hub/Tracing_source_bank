# File: apps/audit/blockchain.py
import json
import hashlib
import os
from datetime import datetime
from decimal import Decimal

try:
    from web3 import Web3
    from eth_account import Account
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    print("❌ Web3包不可用，请安装: pip install web3 eth-account")

class BlockchainService:
    def __init__(self):
        # 合约地址 - 需要先在Ganache部署合约
        self.contract_address = '0xE1f0d4AEF8821B769948aDd7491fd8bBFEd65c8f'
        
        # 账户私钥 - 从Ganache获取一个账户的私钥
        self.account_private_key = '0x955e2524b0bcbeb00c820dc8c0b76e1008771e5581b76320896c21ac18be992e'
        
        # Web3相关初始化
        self.web3 = None
        self.account_address = None
        self.contract = None
        self.contract_abi = None
        
        # 初始化状态
        self.is_initialized = False
        self.initialization_error = None
        
        # 初始化Web3
        self._init_web3()
        
    def _init_web3(self):
        """初始化Web3连接"""
        try:
            if not WEB3_AVAILABLE:
                raise ImportError("Web3包未安装")
            
            print("=" * 50)
            print("🚀 初始化区块链服务...")
            print("=" * 50)
            
            # Ganache 连接配置
            self.rpc_url = 'http://127.0.0.1:7545'
            print(f"🔗 连接到: {self.rpc_url}")
            
            # 创建HTTPProvider
            self.web3 = Web3(Web3.HTTPProvider(self.rpc_url, request_kwargs={'timeout': 60}))
            
            # 测试连接
            print("📡 测试区块链连接...")
            if not self.web3.is_connected():
                raise ConnectionError(f"无法连接到区块链节点: {self.rpc_url}")
            
            print(f"✅ 区块链连接成功!")
            
            # 获取网络信息
            chain_id = self.web3.eth.chain_id
            block_number = self.web3.eth.block_number
            print(f"🔗 链ID: {chain_id}")
            print(f"📦 当前区块: {block_number}")
            
            # 从私钥获取账户地址
            try:
                if not self.account_private_key.startswith('0x'):
                    self.account_private_key = '0x' + self.account_private_key
                
                self.account = Account.from_key(self.account_private_key)
                self.account_address = self.account.address
                print(f"👤 账户地址: {self.account_address}")
                
                # 检查账户余额
                try:
                    balance = self.web3.eth.get_balance(self.account_address)
                    balance_eth = self.web3.from_wei(balance, 'ether')
                    print(f"💰 账户余额: {balance_eth} ETH")
                    
                    if balance_eth < 0.1:
                        print("⚠️  警告: 账户余额较低，可能无法支付Gas费用")
                except Exception as e:
                    print(f"⚠️  无法获取账户余额: {str(e)}")
                    
            except Exception as e:
                print(f"❌ 账户初始化失败: {str(e)}")
                raise
            
            # 合约ABI
            self.contract_abi = self._get_contract_abi()
            
            # 验证合约地址
            if not self.web3.is_address(self.contract_address):
                raise ValueError(f"无效的合约地址: {self.contract_address}")
            
            print(f"📄 合约地址: {self.contract_address}")
            
            # 创建合约实例
            self.contract = self.web3.eth.contract(
                address=self.contract_address,
                abi=self.contract_abi
            )
            
            # 测试合约连接
            try:
                print("🧪 测试合约连接...")
                
                # 尝试读取合约信息
                owner = self.contract.functions.owner().call()
                print(f"👑 合约所有者: {owner}")
                
                counter = self.contract.functions.auditIdCounter().call()
                print(f"📊 审计记录数量: {counter}")
                
                print("✅ 合约连接成功!")
                
            except Exception as e:
                print(f"⚠️  合约调用测试失败: {str(e)}")
                print("可能是合约未部署或ABI不匹配")
            
            self.is_initialized = True
            print("✅ 区块链服务初始化完成!")
            print("=" * 50)
            
        except Exception as e:
            self.initialization_error = str(e)
            print(f"❌ 区块链服务初始化失败: {str(e)}")
            self.is_initialized = False
    
    def _get_contract_abi(self):
        """获取合约ABI - 完整的ABI"""
        return [
            {
                "inputs": [],
                "stateMutability": "nonpayable",
                "type": "constructor"
            },
            {
                "anonymous": False,
                "inputs": [
                    {
                        "indexed": True,
                        "internalType": "uint256",
                        "name": "auditId",
                        "type": "uint256"
                    },
                    {
                        "indexed": True,
                        "internalType": "string",
                        "name": "transactionId",
                        "type": "string"
                    },
                    {
                        "indexed": False,
                        "internalType": "string",
                        "name": "calculatedHash",
                        "type": "string"
                    },
                    {
                        "indexed": False,
                        "internalType": "string",
                        "name": "blockchainHash",
                        "type": "string"
                    },
                    {
                        "indexed": True,
                        "internalType": "address",
                        "name": "sender",
                        "type": "address"
                    },
                    {
                        "indexed": False,
                        "internalType": "uint256",
                        "name": "timestamp",
                        "type": "uint256"
                    },
                    {
                        "indexed": False,
                        "internalType": "uint256",
                        "name": "blockNumber",
                        "type": "uint256"
                    }
                ],
                "name": "AuditHashStored",
                "type": "event"
            },
            {
                "inputs": [],
                "name": "auditIdCounter",
                "outputs": [
                    {
                        "internalType": "uint256",
                        "name": "",
                        "type": "uint256"
                    }
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {
                        "internalType": "uint256",
                        "name": "",
                        "type": "uint256"
                    }
                ],
                "name": "auditRecords",
                "outputs": [
                    {
                        "internalType": "uint256",
                        "name": "auditId",
                        "type": "uint256"
                    },
                    {
                        "internalType": "string",
                        "name": "transactionId",
                        "type": "string"
                    },
                    {
                        "internalType": "string",
                        "name": "calculatedHash",
                        "type": "string"
                    },
                    {
                        "internalType": "string",
                        "name": "blockchainHash",
                        "type": "string"
                    },
                    {
                        "internalType": "address",
                        "name": "sender",
                        "type": "address"
                    },
                    {
                        "internalType": "uint256",
                        "name": "timestamp",
                        "type": "uint256"
                    },
                    {
                        "internalType": "uint256",
                        "name": "blockNumber",
                        "type": "uint256"
                    }
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {
                        "internalType": "uint256",
                        "name": "_auditId",
                        "type": "uint256"
                    }
                ],
                "name": "getAuditRecord",
                "outputs": [
                    {
                        "internalType": "uint256",
                        "name": "",
                        "type": "uint256"
                    },
                    {
                        "internalType": "string",
                        "name": "",
                        "type": "string"
                    },
                    {
                        "internalType": "string",
                        "name": "",
                        "type": "string"
                    },
                    {
                        "internalType": "string",
                        "name": "",
                        "type": "string"
                    },
                    {
                        "internalType": "address",
                        "name": "",
                        "type": "address"
                    },
                    {
                        "internalType": "uint256",
                        "name": "",
                        "type": "uint256"
                    },
                    {
                        "internalType": "uint256",
                        "name": "",
                        "type": "uint256"
                    }
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {
                        "internalType": "string",
                        "name": "_hash",
                        "type": "string"
                    }
                ],
                "name": "getAuditIdByHash",
                "outputs": [
                    {
                        "internalType": "uint256",
                        "name": "",
                        "type": "uint256"
                    }
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {
                        "internalType": "string",
                        "name": "",
                        "type": "string"
                    }
                ],
                "name": "hashToAuditId",
                "outputs": [
                    {
                        "internalType": "uint256",
                        "name": "",
                        "type": "uint256"
                    }
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "owner",
                "outputs": [
                    {
                        "internalType": "address",
                        "name": "",
                        "type": "address"
                    }
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {
                        "internalType": "string",
                        "name": "_transactionId",
                        "type": "string"
                    },
                    {
                        "internalType": "string",
                        "name": "_calculatedHash",
                        "type": "string"
                    },
                    {
                        "internalType": "string",
                        "name": "_blockchainHash",
                        "type": "string"
                    }
                ],
                "name": "storeAuditHash",
                "outputs": [
                    {
                        "internalType": "uint256",
                        "name": "",
                        "type": "uint256"
                    }
                ],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {
                        "internalType": "address",
                        "name": "newOwner",
                        "type": "address"
                    }
                ],
                "name": "transferOwnership",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {
                        "internalType": "string",
                        "name": "_hash",
                        "type": "string"
                    }
                ],
                "name": "verifyHash",
                "outputs": [
                    {
                        "internalType": "bool",
                        "name": "",
                        "type": "bool"
                    }
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]
    
    def calculate_hash(self, trans_date, trans_money, card_number, trans_type):
        """计算交易信息的哈希值"""
        try:
            print("🧮 计算哈希值...")
            
            # 将输入转换为字符串
            if isinstance(trans_date, datetime):
                trans_date_str = trans_date.strftime('%Y-%m-%d %H:%M:%S')
            else:
                trans_date_str = str(trans_date)
            
            # 处理金额
            if isinstance(trans_money, Decimal):
                trans_money_str = str(trans_money.quantize(Decimal('0.01')))
            else:
                try:
                    trans_money_str = str(Decimal(str(trans_money)).quantize(Decimal('0.01')))
                except:
                    trans_money_str = str(trans_money)
            
            # 清理数据
            card_number_clean = str(card_number).strip()
            trans_type_clean = str(trans_type).strip()
            
            # 构建数据字符串
            data_string = f"{trans_date_str}|{trans_money_str}|{card_number_clean}|{trans_type_clean}"
            print(f"📝 原始数据: {data_string}")
            
            # 计算SHA256哈希
            sha256_hash = hashlib.sha256(data_string.encode('utf-8')).hexdigest()
            print(f"🔐 计算哈希: {sha256_hash}")
            
            return sha256_hash, data_string
            
        except Exception as e:
            print(f"❌ 计算哈希失败: {str(e)}")
            return None, None
    
    def store_on_blockchain(self, audit_id, transaction_id, calculated_hash, data_string):
        """将哈希存储到区块链"""
        print("=" * 50)
        print(f"🚀 开始上链流程 - 审计ID: {audit_id}")
        print("=" * 50)
        
        if not self.is_initialized or not self.web3 or not self.contract:
            raise Exception("区块链服务未初始化")
        
        try:
            # 检查区块链连接
            if not self.web3.is_connected():
                raise ConnectionError("区块链连接已断开")
            
            # 检查账户
            if not self.account_address:
                raise Exception("账户未初始化")
            
            # 检查账户余额
            balance = self.web3.eth.get_balance(self.account_address)
            balance_eth = self.web3.from_wei(balance, 'ether')
            print(f"💰 当前账户余额: {balance_eth} ETH")
            
            if balance_eth < 0.01:
                print("⚠️  警告: 账户余额较低，可能无法完成交易")
            
            # 生成区块链哈希（对原始哈希再进行一次哈希）
            blockchain_hash = hashlib.sha256(calculated_hash.encode('utf-8')).hexdigest()
            print(f"⛓️  生成区块链哈希: {blockchain_hash[:16]}...")
            
            # 构建交易
            print("🔄 构建交易...")
            
            # 获取nonce
            nonce = self.web3.eth.get_transaction_count(self.account_address)
            print(f"🔢 Nonce: {nonce}")
            
            # 获取当前Gas价格，增加10%作为缓冲
            gas_price = int(self.web3.eth.gas_price * 1.1)
            gas_price_gwei = self.web3.from_wei(gas_price, 'gwei')
            print(f"⛽ Gas价格: {gas_price_gwei} Gwei")
            
            # 估算Gas
            try:
                print("📊 估算Gas使用量...")
                gas_estimate = self.contract.functions.storeAuditHash(
                    str(transaction_id),
                    calculated_hash,
                    blockchain_hash
                ).estimate_gas({'from': self.account_address})
                
                # 增加20%作为缓冲
                gas_limit = int(gas_estimate * 1.2)
                gas_estimate_gwei = self.web3.from_wei(gas_estimate * gas_price, 'gwei')
                estimated_cost_eth = self.web3.from_wei(gas_estimate * gas_price, 'ether')
                
                print(f"📈 估算Gas: {gas_estimate}")
                print(f"📊 设置Gas限制: {gas_limit}")
                print(f"💰 估算费用: {estimated_cost_eth} ETH ({gas_estimate_gwei} Gwei)")
                
            except Exception as e:
                print(f"⚠️  Gas估算失败: {str(e)}")
                gas_limit = 300000  # 默认值
            
            # 构建交易
            transaction = {
                'nonce': nonce,
                'gas': gas_limit,
                'gasPrice': gas_price,
                'chainId': self.web3.eth.chain_id,
                'from': self.account_address
            }
            
            print("📝 构建交易对象...")
            
            # 构建函数调用
            store_txn = self.contract.functions.storeAuditHash(
                str(transaction_id),
                calculated_hash,
                blockchain_hash
            )
            
            # 构建交易数据
            txn_dict = store_txn.build_transaction(transaction)
            
            print("🔏 签名交易...")
            
            # 签名交易 - 使用更兼容的方式
            try:
                # 方法1: 使用web3.eth.account.sign_transaction
                signed_txn = self.web3.eth.account.sign_transaction(txn_dict, self.account_private_key)
                
                # 获取原始交易数据（兼容不同版本的web3.py）
                if hasattr(signed_txn, 'raw_transaction'):
                    raw_tx = signed_txn.raw_transaction
                elif hasattr(signed_txn, 'rawTransaction'):
                    raw_tx = signed_txn.rawTransaction
                elif isinstance(signed_txn, dict):
                    raw_tx = signed_txn.get('raw_transaction') or signed_txn.get('rawTransaction')
                else:
                    # 尝试直接发送
                    raw_tx = signed_txn
                
            except Exception as e:
                print(f"⚠️  签名方式1失败: {str(e)}")
                
                # 方法2: 使用Account.sign_transaction
                try:
                    from eth_account import Account
                    account = Account.from_key(self.account_private_key)
                    signed_txn = account.sign_transaction(txn_dict)
                    raw_tx = signed_txn.rawTransaction
                except Exception as e2:
                    print(f"⚠️  签名方式2失败: {str(e2)}")
                    
                    # 方法3: 使用备用方式
                    raise Exception(f"交易签名失败: {str(e)}")
            
            print("📤 发送交易...")
            
            # 发送交易
            try:
                tx_hash = self.web3.eth.send_raw_transaction(raw_tx)
            except Exception as e:
                print(f"⚠️  发送交易失败: {str(e)}")
                # 检查错误类型
                if "insufficient funds" in str(e).lower():
                    raise Exception(f"账户余额不足: {balance_eth} ETH，请充值")
                elif "nonce" in str(e).lower():
                    raise Exception("Nonce错误，请重试")
                else:
                    raise
            
            tx_hash_hex = tx_hash.hex()
            print(f"✅ 交易已发送! 交易哈希: {tx_hash_hex}")
            
            print("⏳ 等待交易确认...")
            
            # 等待交易确认，设置更长的超时时间
            try:
                tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300, poll_latency=2)
            except Exception as e:
                print(f"⚠️  等待交易确认超时: {str(e)}")
                # 即使超时，也尝试获取收据
                try:
                    tx_receipt = self.web3.eth.get_transaction_receipt(tx_hash)
                    if not tx_receipt:
                        raise Exception("交易可能还未被打包")
                except Exception:
                    raise Exception(f"交易确认超时，但交易已发送: {tx_hash_hex}")
            
            if tx_receipt.status == 1:
                print(f"✅ 交易已确认! 区块号: {tx_receipt.blockNumber}")
            else:
                raise Exception(f"交易失败! 状态: {tx_receipt.status}")
            
            # 获取实际使用的Gas
            gas_used = tx_receipt.gasUsed
            actual_cost_wei = gas_used * gas_price
            actual_cost_eth = self.web3.from_wei(actual_cost_wei, 'ether')
            
            print(f"📊 实际Gas使用: {gas_used}")
            print(f"💰 实际费用: {actual_cost_eth} ETH")
            
            print("=" * 50)
            print("🎉 上链成功!")
            print("=" * 50)
            
            return {
                'success': True,
                'tx_hash': tx_hash_hex,
                'block_number': tx_receipt.blockNumber,
                'gas_used': gas_used,
                'blockchain_hash': blockchain_hash,
                'stored_id': audit_id,
                'contract_address': self.contract_address,
                'sender_address': self.account_address,
                'gas_price': gas_price,
                'actual_cost_eth': float(actual_cost_eth),
                'message': '成功存储到区块链'
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 上链失败: {error_msg}")
            print("=" * 50)
            
            return {
                'success': False,
                'error': error_msg,
                'tx_hash': None,
                'block_number': None,
                'gas_used': None
            }
    
    def verify_on_blockchain(self, calculated_hash):
        """在区块链上验证哈希"""
        print(f"🔍 验证哈希: {calculated_hash[:16]}...")
        
        if not self.is_initialized or not self.web3 or not self.contract:
            raise Exception("区块链服务未初始化")
        
        try:
            # 调用合约验证函数
            print("📡 调用合约验证函数...")
            exists = self.contract.functions.verifyHash(calculated_hash).call()
            
            if exists:
                # 获取审计ID
                audit_id = self.contract.functions.getAuditIdByHash(calculated_hash).call()
                print(f"✅ 哈希存在于区块链，审计ID: {audit_id}")
                
                return {
                    'success': True,
                    'exists': True,
                    'verified': True,
                    'audit_id': audit_id
                }
            else:
                print("❌ 哈希不存在于区块链")
                
                return {
                    'success': True,
                    'exists': False,
                    'verified': False,
                    'audit_id': None
                }
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 验证失败: {error_msg}")
            
            return {
                'success': False,
                'exists': False,
                'verified': False,
                'error': error_msg
            }
    
    def get_audit_record(self, audit_id):
        """从区块链获取审计记录"""
        print(f"📖 获取审计记录 - ID: {audit_id}")
        
        if not self.is_initialized or not self.web3 or not self.contract:
            raise Exception("区块链服务未初始化")
        
        try:
            # 调用合约获取记录
            print("📡 调用合约获取记录...")
            record = self.contract.functions.getAuditRecord(audit_id).call()
            
            print(f"✅ 获取记录成功")
            
            return {
                'success': True,
                'audit_id': record[0],
                'transaction_id': record[1],
                'calculated_hash': record[2],
                'blockchain_hash': record[3],
                'sender': record[4],
                'timestamp': record[5],
                'block_number': record[6]
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 获取记录失败: {error_msg}")
            
            return {
                'success': False,
                'error': error_msg,
                'audit_id': audit_id
            }
    
    def get_contract_info(self):
        """获取合约信息"""
        print("📄 获取合约信息...")
        
        if not self.is_initialized or not self.web3 or not self.contract:
            raise Exception("区块链服务未初始化")
        
        try:
            # 获取合约计数器
            audit_id_counter = self.contract.functions.auditIdCounter().call()
            owner = self.contract.functions.owner().call()
            
            print(f"✅ 合约信息获取成功")
            print(f"📊 审计记录数量: {audit_id_counter}")
            print(f"👑 合约所有者: {owner}")
            
            return {
                'success': True,
                'audit_id_counter': audit_id_counter,
                'owner': owner,
                'contract_address': self.contract_address
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 获取合约信息失败: {error_msg}")
            
            return {
                'success': False,
                'error': error_msg
            }
    
    def get_blockchain_info(self):
        """获取区块链信息"""
        print("🌐 获取区块链信息...")
        
        if not self.is_initialized or not self.web3:
            return {
                'connected': False,
                'error': self.initialization_error or '区块链服务未初始化',
                'is_initialized': False
            }
        
        try:
            info = {
                'connected': True,
                'is_initialized': True,
                'chain_id': self.web3.eth.chain_id,
                'block_number': self.web3.eth.block_number,
                'gas_price': str(self.web3.eth.gas_price),
                'contract_address': self.contract_address,
                'contract_initialized': self.contract is not None,
                'account_address': self.account_address,
                'rpc_url': self.rpc_url
            }
            
            if self.account_address:
                try:
                    balance = self.web3.eth.get_balance(self.account_address)
                    info['account_balance'] = str(balance)
                    info['account_balance_eth'] = float(self.web3.from_wei(balance, 'ether'))
                except Exception as e:
                    info['balance_error'] = str(e)
            
            # 获取合约信息
            if self.contract:
                try:
                    contract_info = self.get_contract_info()
                    if contract_info['success']:
                        info['contract_info'] = {
                            'audit_id_counter': contract_info['audit_id_counter'],
                            'owner': contract_info['owner']
                        }
                except Exception as e:
                    info['contract_info_error'] = str(e)
            
            print(f"✅ 区块链信息获取成功")
            
            return info
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 获取区块链信息失败: {error_msg}")
            
            return {
                'connected': False,
                'error': error_msg,
                'is_initialized': False
            }

# 单例实例
blockchain_service = BlockchainService()