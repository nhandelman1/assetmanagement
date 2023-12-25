# Generated by Django 4.2.5 on 2023-11-11 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investing', '0032_alter_transaction_action_type_tickerhistory_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='action_type',
            field=models.CharField(choices=[('BUY', 'Buy'), ('BUY_COVER', 'Buy Cover'), ('CONVERSION', 'Conversion'), ('COUP_PMT', 'Coupon Payment'), ('DIVIDEND', 'Dividend'), ('INT_PMT', 'Interest Payment'), ('LOAN', 'Loan'), ('MERGER_OLD', 'Merger Old'), ('MERGER_NEW', 'Merger New'), ('OPT_EXER', 'Option Exercise'), ('OPT_EXP', 'Option Expire'), ('SELL', 'Sell'), ('SELL_SHORT', 'Sell Short'), ('SPINOFF', 'Spin-Off'), ('STOCK_CONS', 'Stock Consolidation'), ('STOCK_DIV', 'Stock Dividend'), ('STOCK_SPLIT', 'Stock Split'), ('TRANSFER', 'Transfer')], max_length=11),
        ),
    ]