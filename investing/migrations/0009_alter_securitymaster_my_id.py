# Generated by Django 4.2.5 on 2023-10-25 20:17

from django.db import migrations, models
import investing.models.securitymaster


class Migration(migrations.Migration):

    dependencies = [
        ('investing', '0008_alter_securitymaster_my_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='securitymaster',
            name='my_id',
            field=models.CharField(max_length=10, unique=True, validators=[investing.models.securitymaster.SecurityMaster.validate_my_id]),
        ),
    ]
