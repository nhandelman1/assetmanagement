# Generated by Django 4.2.5 on 2023-10-28 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investing', '0018_securitymaster_has_fidelity_lots'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='purchase_date',
            field=models.DateField(help_text='Required if broker breaks position into lots.'),
        ),
    ]