# Generated by Django 4.2.5 on 2023-10-25 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investing', '0004_rename_tickers_newssentiment_ticker_sentiments_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvestmentAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('broker', models.CharField(choices=[('FIDELITY', 'FIDELITY')], max_length=30)),
                ('account_id', models.CharField(max_length=20)),
                ('account_name', models.CharField(max_length=30)),
            ],
        ),
    ]