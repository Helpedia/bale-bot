# Generated by Django 4.1 on 2023-05-23 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('botreader', '0011_add_membership'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='members',
            field=models.ManyToManyField(blank=True, through='botreader.Membership', to='botreader.user'),
        ),
    ]