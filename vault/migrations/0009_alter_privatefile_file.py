# Generated by Django 5.2 on 2025-04-10 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vault', '0008_delete_fileshare'),
    ]

    operations = [
        migrations.AlterField(
            model_name='privatefile',
            name='file',
            field=models.FileField(upload_to='private_files/'),
        ),
    ]
