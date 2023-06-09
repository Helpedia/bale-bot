# Generated by Django 4.1 on 2023-05-17 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("botreader", "0009_replace_sender_model_with_user_model"),
    ]

    operations = [
        migrations.AddField(
            model_name="chat",
            name="admins",
            field=models.ManyToManyField(
                default=[], related_name="groups_admin", to="botreader.user"
            ),
        ),
    ]
