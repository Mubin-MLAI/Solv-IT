# Generated by Django 5.1.4 on 2025-01-08 08:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0005_itemform"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="ItemForm",
            new_name="catogaryitem",
        ),
    ]
