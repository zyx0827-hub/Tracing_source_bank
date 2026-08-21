from django.db import models

# Create your models here.
class TradeInfo(models.Model):
    tid = models.AutoField(primary_key=True)
    trans_type = models.CharField(max_length=2)
    card = models.ForeignKey('cardinfo.CardInfo', models.DO_NOTHING)
    trans_date = models.DateTimeField()
    trans_money = models.DecimalField(max_digits=15, decimal_places=0)
    remark = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trade_info'