# Generated by Django 4.2.5 on 2023-10-02 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('realestate', '0004_alter_electricbilldata_bs_rate'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='electricdata',
            constraint=models.UniqueConstraint(fields=('real_estate', 'year_month'), name='unique_realestate_electricdata_re_my'),
        ),
        migrations.AddConstraint(
            model_name='natgasdata',
            constraint=models.UniqueConstraint(fields=('real_estate', 'year_month'), name='unique_realestate_natgasdata_re_my'),
        ),
    ]
