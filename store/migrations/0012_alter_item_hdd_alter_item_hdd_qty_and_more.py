# Generated by Django 5.1.4 on 2025-02-06 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0011_alter_item_hdd_alter_item_hdd_qty_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="item",
            name="hdd",
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="item",
            name="hdd_qty",
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name="item",
            name="motherboard_replacement_description",
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="item",
            name="processor",
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="item",
            name="processor_qty",
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name="item",
            name="ram",
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="item",
            name="ram_qty",
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name="item",
            name="smps_replacement_description",
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="item",
            name="ssd",
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="item",
            name="ssd_qty",
            field=models.PositiveIntegerField(),
        ),
    ]
