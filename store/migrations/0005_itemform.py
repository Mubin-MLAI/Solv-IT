# Generated by Django 5.1.4 on 2025-01-08 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0004_remove_item_m_2_remove_item_nvme_remove_sdd_capcity_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ItemForm",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("ssd", "SSD"),
                            ("processor", "Processor"),
                            ("hdd", "HDD"),
                            ("ram", "RAM"),
                        ],
                        max_length=20,
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("serial_no", models.CharField(max_length=100)),
                ("quantity", models.IntegerField()),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                "verbose_name_plural": "category",
            },
        ),
    ]
