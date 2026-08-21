from django.db import models

class CardInfo(models.Model):
    CUR_TYPE_CHOICES = [
        ("CNY", "人民币"),
        ("USD", "美元"),
        ("EUR", "欧元"),
        ("JPY", "日元"),
    ]

    # 把 card_id 设为主键，Django 就不会再自动创建 id 字段
    card_id = models.CharField(
        max_length=25,
        primary_key=True,
        verbose_name="卡号"
    )
    cur_type = models.CharField(
        max_length=3,
        choices=CUR_TYPE_CHOICES,
        default="CNY",
        verbose_name="币种"
    )
    open_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="开户日期"
    )
    open_money = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="开户金额"
    )
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="余额"
    )
    password = models.CharField(
        max_length=128,
        default="123456",
        verbose_name="密码"
    )
    customer_id = models.IntegerField(
        default=1,
        verbose_name="客户ID"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="是否激活"
    )

    class Meta:
        db_table = "card_info"
        verbose_name = "银行卡信息"

    def __str__(self):
        return str(self.card_id)