# Generated by Django 4.1.5 on 2023-01-29 15:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('botreader', '0004_remove_chat_all_members_are_administrators'),
    ]

    operations = [
        migrations.AddField(
            model_name='textmessage',
            name='reply',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='botreader.textmessage'),
        ),
    ]
