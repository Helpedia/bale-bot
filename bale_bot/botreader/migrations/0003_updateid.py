# Generated by Django 4.1.5 on 2023-01-29 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('botreader', '0002_alter_textmessage_chat_alter_textmessage_sender'),
    ]

    operations = [
        migrations.CreateModel(
            name='UpdateId',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_id', models.BigIntegerField()),
            ],
        ),
    ]