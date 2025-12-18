from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("ac_system", "0002_add_reserved_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="Reservation",
            fields=[
                (
                    "reservation_id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="预定ID",
                    ),
                ),
                ("name", models.CharField(max_length=50, verbose_name="预定人姓名")),
                ("phone", models.CharField(max_length=11, verbose_name="预定人手机号")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="预定时间"),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="是否有效"),
                ),
                (
                    "room",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ac_system.room",
                        verbose_name="房间",
                    ),
                ),
            ],
            options={
                "verbose_name": "房间预定",
                "verbose_name_plural": "房间预定",
                "db_table": "reservation",
            },
        ),
    ]


