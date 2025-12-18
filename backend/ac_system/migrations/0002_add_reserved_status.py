from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ac_system", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="room",
            name="status",
            field=models.CharField(
                choices=[
                    ("available", "空闲"),
                    ("reserved", "已预定"),
                    ("occupied", "已入住"),
                    ("maintenance", "维护中"),
                ],
                default="available",
                max_length=20,
                verbose_name="房间状态",
            ),
        ),
    ]


