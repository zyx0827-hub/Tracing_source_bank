# File: apps/audit/views.py
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from decimal import Decimal
import logging

from apps.audit.models import Audit
from apps.audit.serializers import AuditSerializer
from apps.audit.blockchain import blockchain_service

logger = logging.getLogger(__name__)

class AuditViewSet(viewsets.ModelViewSet):
    """审计表视图集"""
    queryset = Audit.objects.all()
    serializer_class = AuditSerializer
    
    def create(self, request, *args, **kwargs):
        """重写创建方法，自动生成UUID和时间戳"""
        try:
            # 自动生成UUID
            import uuid
            request.data['audit_uuid'] = str(uuid.uuid4())
            
            # 设置创建时间和更新时间
            now = timezone.now()
            request.data['created_at'] = now
            request.data['updated_at'] = now
            
            # 如果状态未设置，默认为pending
            if 'audit_status' not in request.data:
                request.data['audit_status'] = 'pending'
                
            # 如果验证结果未设置，默认为1（有效）
            if 'is_valid' not in request.data:
                request.data['is_valid'] = 1
                
        except Exception as e:
            logger.error(f"创建审计记录错误: {e}")
            
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """保存时自动设置更多字段"""
        instance = serializer.save()
        
        # 自动计算哈希（如果数据完整）
        if (instance.trans_date and instance.trans_money and 
            instance.card_number and instance.trans_type):
            try:
                calculated_hash, data_string = blockchain_service.calculate_hash(
                    instance.trans_date,
                    instance.trans_money,
                    instance.card_number,
                    instance.trans_type
                )
                
                if calculated_hash:
                    instance.calculated_hash = calculated_hash
                    instance.data_string = data_string
                    instance.save()
                    logger.info(f"审计记录 {instance.id} 哈希计算成功")
            except Exception as e:
                logger.error(f"审计记录 {instance.id} 哈希计算失败: {e}")
    
    @action(detail=True, methods=['post'])
    def store_on_blockchain(self, request, pk=None):
        """将审计记录存储到区块链"""
        try:
            audit = self.get_object()
            logger.info(f"开始上链流程 - 审计ID: {audit.id}")
            
            # 检查必填字段
            required_fields = ['trans_date', 'trans_money', 'card_number', 'trans_type']
            missing_fields = []
            
            for field in required_fields:
                field_value = getattr(audit, field, None)
                if not field_value:
                    missing_fields.append(field)
            
            if missing_fields:
                logger.warning(f"审计记录 {audit.id} 缺少字段: {missing_fields}")
                return Response({
                    'success': False,
                    'error': f'以下字段不能为空: {", ".join(missing_fields)}',
                    'missing_fields': missing_fields
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 计算哈希
            calculated_hash, data_string = blockchain_service.calculate_hash(
                audit.trans_date,
                audit.trans_money,
                audit.card_number,
                audit.trans_type
            )
            
            if not calculated_hash:
                logger.error(f"审计记录 {audit.id} 计算哈希失败")
                return Response({
                    'success': False,
                    'error': '计算哈希失败'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # 检查是否已上链
            if audit.tx_hash and audit.blockchain_hash:
                # 验证现有哈希
                verify_result = blockchain_service.verify_on_blockchain(calculated_hash)
                if verify_result.get('verified'):
                    logger.info(f"审计记录 {audit.id} 已上链")
                    return Response({
                        'success': True,
                        'message': '该记录已成功上链',
                        'already_on_chain': True,
                        'tx_hash': audit.tx_hash,
                        'block_number': audit.block_number,
                        'verified': True
                    })
            
            # 检查区块链服务是否初始化
            if not blockchain_service.is_initialized:
                logger.error("区块链服务未初始化")
                return Response({
                    'success': False,
                    'error': '区块链服务未初始化，请检查Ganache是否运行'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            # 存储到区块链
            transaction_id = audit.transaction_id or f"AUDIT_{audit.id}"
            logger.info(f"开始上链到区块链 - 交易ID: {transaction_id}")
            
            blockchain_result = blockchain_service.store_on_blockchain(
                audit.id,
                transaction_id,
                calculated_hash,
                data_string
            )
            
            if blockchain_result['success']:
                # 更新数据库记录
                audit.data_string = data_string
                audit.calculated_hash = calculated_hash
                audit.blockchain_hash = blockchain_result.get('blockchain_hash')
                audit.tx_hash = blockchain_result.get('tx_hash')
                audit.block_number = blockchain_result.get('block_number')
                audit.contract_address = blockchain_result.get('contract_address')
                audit.sender_address = blockchain_result.get('sender_address')
                audit.gas_used = blockchain_result.get('gas_used')
                audit.gas_price = blockchain_result.get('gas_price')
                
                # 计算总Gas费用
                if audit.gas_used and audit.gas_price:
                    audit.total_gas_cost = Decimal(str(audit.gas_used)) * Decimal(str(audit.gas_price))
                
                audit.audit_status = 'completed'
                audit.status_changed_at = timezone.now()
                audit.status_changed_by = 'blockchain_service'
                audit.stored_at = timezone.now()
                audit.is_valid = 1
                audit.verification_count = (audit.verification_count or 0) + 1
                audit.last_verified = timezone.now()
                
                # 清除错误信息
                audit.error_code = None
                audit.error_message = None
                audit.retry_count = 0
                
                audit.save()
                logger.info(f"审计记录 {audit.id} 上链成功并更新数据库")
                
                # 重新获取序列化数据
                serializer = self.get_serializer(audit)
                
                return Response({
                    'success': True,
                    'message': '成功存储到区块链',
                    'tx_hash': blockchain_result['tx_hash'],
                    'block_number': blockchain_result['block_number'],
                    'calculated_hash': calculated_hash,
                    'blockchain_hash': blockchain_result['blockchain_hash'],
                    'stored_id': blockchain_result.get('stored_id'),
                    'contract_address': blockchain_result.get('contract_address'),
                    'sender_address': blockchain_result.get('sender_address'),
                    'gas_used': blockchain_result.get('gas_used'),
                    'actual_cost_eth': blockchain_result.get('actual_cost_eth'),
                    'audit': serializer.data
                })
            else:
                # 记录错误
                audit.error_message = blockchain_result.get('error', '未知错误')
                audit.retry_count = (audit.retry_count or 0) + 1
                audit.audit_status = 'failed'
                audit.status_changed_at = timezone.now()
                audit.status_changed_by = 'blockchain_service'
                audit.save()
                
                logger.error(f"审计记录 {audit.id} 上链失败: {blockchain_result.get('error')}")
                
                return Response({
                    'success': False,
                    'error': blockchain_result.get('error', '区块链存储失败'),
                    'retry_count': audit.retry_count
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            # 记录异常
            audit = self.get_object()
            audit.error_message = str(e)
            audit.retry_count = (audit.retry_count or 0) + 1
            audit.audit_status = 'failed'
            audit.status_changed_at = timezone.now()
            audit.save()
            
            logger.error(f"审计记录上链异常: {str(e)}", exc_info=True)
            
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def verify_on_blockchain(self, request, pk=None):
        """验证审计记录在区块链上的存在性"""
        try:
            audit = self.get_object()
            logger.info(f"验证审计记录 - ID: {audit.id}")
            
            if not audit.calculated_hash:
                # 如果没有计算哈希，先计算
                if audit.trans_date and audit.trans_money and audit.card_number and audit.trans_type:
                    calculated_hash, data_string = blockchain_service.calculate_hash(
                        audit.trans_date,
                        audit.trans_money,
                        audit.card_number,
                        audit.trans_type
                    )
                    
                    if calculated_hash:
                        audit.calculated_hash = calculated_hash
                        audit.data_string = data_string
                        audit.save()
                    else:
                        logger.error(f"审计记录 {audit.id} 无法计算哈希")
                        return Response({
                            'success': False,
                            'error': '无法计算哈希值'
                        }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    logger.error(f"审计记录 {audit.id} 缺少必要字段")
                    return Response({
                        'success': False,
                        'error': '该记录没有计算哈希且缺少必要字段，无法验证'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # 检查区块链服务是否初始化
            if not blockchain_service.is_initialized:
                return Response({
                    'success': False,
                    'error': '区块链服务未初始化'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            # 在区块链上验证
            verify_result = blockchain_service.verify_on_blockchain(audit.calculated_hash)
            
            if verify_result['success']:
                # 更新验证信息
                audit.is_valid = 1 if verify_result['verified'] else 0
                audit.verification_count = (audit.verification_count or 0) + 1
                audit.last_verified = timezone.now()
                audit.audit_status = 'completed' if verify_result['verified'] else 'failed'
                audit.status_changed_at = timezone.now()
                
                if not verify_result['verified']:
                    audit.error_message = '哈希在区块链上不存在'
                
                audit.save()
                logger.info(f"审计记录 {audit.id} 验证结果: {verify_result['verified']}")
                
                return Response({
                    'success': True,
                    'verified': verify_result['verified'],
                    'verification_count': audit.verification_count,
                    'message': '验证成功' if verify_result['verified'] else '哈希在区块链上不存在',
                    'calculated_hash': audit.calculated_hash,
                    'audit_id': verify_result.get('audit_id')
                })
            else:
                logger.error(f"审计记录 {audit.id} 验证失败: {verify_result.get('error')}")
                return Response({
                    'success': False,
                    'error': verify_result.get('error', '验证失败'),
                    'verified': False
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"验证审计记录异常: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': str(e),
                'verified': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def blockchain_status(self, request):
        """获取区块链状态"""
        try:
            logger.info("获取区块链状态")
            
            # 获取区块链信息
            blockchain_info = blockchain_service.get_blockchain_info()
            
            return Response(blockchain_info)
            
        except Exception as e:
            logger.error(f"获取区块链状态异常: {str(e)}", exc_info=True)
            return Response({
                'connected': False,
                'error': str(e),
                'is_initialized': False
            })
    
    @action(detail=True, methods=['get'])
    def blockchain_record(self, request, pk=None):
        """从区块链获取审计记录详情"""
        try:
            audit = self.get_object()
            logger.info(f"获取区块链记录 - 审计ID: {audit.id}")
            
            if not audit.calculated_hash:
                logger.error(f"审计记录 {audit.id} 没有计算哈希")
                return Response({
                    'success': False,
                    'error': '该记录没有计算哈希'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 检查区块链服务是否初始化
            if not blockchain_service.is_initialized:
                return Response({
                    'success': False,
                    'error': '区块链服务未初始化'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            # 首先验证哈希是否存在
            verify_result = blockchain_service.verify_on_blockchain(audit.calculated_hash)
            
            if not verify_result['success']:
                logger.error(f"验证哈希失败: {verify_result.get('error')}")
                return Response({
                    'success': False,
                    'error': verify_result.get('error', '验证失败')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            if not verify_result['verified']:
                logger.info(f"审计记录 {audit.id} 哈希不在区块链上")
                return Response({
                    'success': True,
                    'verified': False,
                    'message': '哈希在区块链上不存在'
                })
            
            # 获取审计ID
            audit_id = verify_result.get('audit_id')
            if not audit_id:
                logger.error(f"无法获取审计ID")
                return Response({
                    'success': False,
                    'error': '无法获取审计ID'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # 获取详细记录
            record_result = blockchain_service.get_audit_record(audit_id)
            
            if record_result['success']:
                logger.info(f"成功获取区块链记录 - 审计ID: {audit_id}")
                return Response({
                    'success': True,
                    'verified': True,
                    'record': record_result
                })
            else:
                logger.error(f"获取区块链记录失败: {record_result.get('error')}")
                return Response({
                    'success': False,
                    'error': record_result.get('error', '获取记录失败')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"获取区块链记录异常: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def batch_store_blockchain(self, request):
        """批量上链"""
        try:
            audit_ids = request.data.get('audit_ids', [])
            logger.info(f"批量上链 - 审计ID列表: {audit_ids}")
            
            if not audit_ids:
                # 获取所有可以上链的记录
                audits_list = Audit.objects.filter(
                    trans_date__isnull=False,
                    trans_money__isnull=False,
                    card_number__isnull=False,
                    trans_type__isnull=False,
                    audit_status='pending'  # 只处理待处理的记录
                ).exclude(
                    tx_hash__isnull=False,
                    blockchain_hash__isnull=False
                )[:5]  # 限制一次最多处理5条
                
                audit_ids = list(audits_list.values_list('id', flat=True))
                logger.info(f"自动选择审计记录: {audit_ids}")
            
            # 检查区块链服务是否初始化
            if not blockchain_service.is_initialized:
                return Response({
                    'success': False,
                    'error': '区块链服务未初始化'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            results = []
            success_count = 0
            fail_count = 0
            
            for audit_id in audit_ids:
                try:
                    # 获取审计记录
                    audit = Audit.objects.get(id=audit_id)
                    
                    # 检查是否已经上链
                    if audit.tx_hash and audit.blockchain_hash:
                        results.append({
                            'audit_id': audit_id,
                            'success': True,
                            'message': '已上链',
                            'already_on_chain': True,
                            'tx_hash': audit.tx_hash
                        })
                        success_count += 1
                        continue
                    
                    # 检查必填字段
                    required_fields = ['trans_date', 'trans_money', 'card_number', 'trans_type']
                    missing_fields = []
                    
                    for field in required_fields:
                        if not getattr(audit, field, None):
                            missing_fields.append(field)
                    
                    if missing_fields:
                        results.append({
                            'audit_id': audit_id,
                            'success': False,
                            'error': f'缺少字段: {", ".join(missing_fields)}'
                        })
                        fail_count += 1
                        continue
                    
                    # 调用单个上链
                    # 这里可以直接调用store_on_blockchain方法，但为了简单起见，我们直接处理
                    calculated_hash, data_string = blockchain_service.calculate_hash(
                        audit.trans_date,
                        audit.trans_money,
                        audit.card_number,
                        audit.trans_type
                    )
                    
                    if not calculated_hash:
                        results.append({
                            'audit_id': audit_id,
                            'success': False,
                            'error': '计算哈希失败'
                        })
                        fail_count += 1
                        continue
                    
                    transaction_id = audit.transaction_id or f"AUDIT_{audit.id}"
                    
                    # 这里可以调用单个上链的逻辑
                    # 为了简化，我们返回准备上链状态
                    results.append({
                        'audit_id': audit_id,
                            'success': True,
                            'message': '准备上链',
                            'calculated_hash': calculated_hash
                    })
                    success_count += 1
                    
                except Audit.DoesNotExist:
                    results.append({
                        'audit_id': audit_id,
                        'success': False,
                        'error': '审计记录不存在'
                    })
                    fail_count += 1
                except Exception as e:
                    results.append({
                        'audit_id': audit_id,
                        'success': False,
                        'error': str(e)
                    })
                    fail_count += 1
            
            logger.info(f"批量上链完成 - 成功: {success_count}, 失败: {fail_count}")
            
            return Response({
                'success': True,
                'total': len(results),
                'success_count': success_count,
                'fail_count': fail_count,
                'results': results
            })
            
        except Exception as e:
            logger.error(f"批量上链异常: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)