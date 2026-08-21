from django.db import models


class Audit(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='审计记录ID')
    audit_uuid = models.CharField(max_length=36, blank=True, null=True, db_comment='审计记录UUID')
    transaction_id = models.CharField(max_length=100, blank=True, null=True, db_comment='交易ID')
    trans_date = models.DateTimeField(db_comment='交易日期')
    trans_money = models.DecimalField(max_digits=15, decimal_places=2, db_comment='交易金额')
    card_number = models.CharField(max_length=50, db_comment='银行卡号')
    trans_type = models.CharField(max_length=20, db_comment='交易类型')
    trade_tid = models.IntegerField(blank=True, null=True, db_comment='关联交易ID')
    data_string = models.TextField(blank=True, null=True, db_comment='原始数据字符串')
    calculated_hash = models.CharField(max_length=255, blank=True, null=True, db_comment='前端计算的哈希值')
    blockchain_hash = models.CharField(max_length=255, blank=True, null=True, db_comment='区块链上存储的哈希值')
    is_valid = models.IntegerField(blank=True, null=True, db_comment='验证是否通过')
    last_verified = models.DateTimeField(blank=True, null=True, db_comment='最后验证时间')
    verification_count = models.IntegerField(blank=True, null=True, db_comment='验证次数')
    tx_hash = models.CharField(max_length=255, blank=True, null=True, db_comment='区块链交易哈希')
    block_number = models.BigIntegerField(blank=True, null=True, db_comment='区块号')
    block_hash = models.CharField(max_length=255, blank=True, null=True, db_comment='区块哈希')
    contract_address = models.CharField(max_length=255, blank=True, null=True, db_comment='智能合约地址')
    sender_address = models.CharField(max_length=255, blank=True, null=True, db_comment='发送者地址')
    gas_used = models.DecimalField(max_digits=20, decimal_places=0, blank=True, null=True, db_comment='使用的Gas数量')
    gas_price = models.DecimalField(max_digits=20, decimal_places=0, blank=True, null=True, db_comment='Gas价格')
    total_gas_cost = models.DecimalField(max_digits=30, decimal_places=0, blank=True, null=True, db_comment='总Gas费用')
    audit_status = models.CharField(max_length=20, blank=True, null=True, db_comment='审计状态')
    status_changed_at = models.DateTimeField(blank=True, null=True, db_comment='状态变更时间')
    status_changed_by = models.CharField(max_length=100, blank=True, null=True, db_comment='状态变更者')
    error_code = models.CharField(max_length=50, blank=True, null=True, db_comment='错误代码')
    error_message = models.TextField(blank=True, null=True, db_comment='错误信息')
    retry_count = models.IntegerField(blank=True, null=True, db_comment='重试次数')
    max_retries = models.IntegerField(blank=True, null=True, db_comment='最大重试次数')
    auditor = models.CharField(max_length=100, blank=True, null=True, db_comment='审计人员/系统')
    audit_notes = models.TextField(blank=True, null=True, db_comment='审计备注')
    created_at = models.DateTimeField(db_comment='创建时间')
    updated_at = models.DateTimeField(db_comment='更新时间')
    stored_at = models.DateTimeField(blank=True, null=True, db_comment='存储到区块链的时间')
    confirmed_at = models.DateTimeField(blank=True, null=True, db_comment='确认时间')
    metadata = models.TextField(blank=True, null=True, db_comment='扩展元数据')

    class Meta:
        managed = False
        db_table = 'audit'
        db_table_comment = '区块链交易审计表'