# Generated by Django 4.1 on 2023-05-24 01:33

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("botreader", "0012_chat_members"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chat",
            name="members",
            field=models.ManyToManyField(
                blank=True,
                related_name="chats",
                through="botreader.Membership",
                to="botreader.user",
            ),
        ),
        migrations.AlterField(
            model_name="textmessage",
            name="chat",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="textmessages",
                to="botreader.chat",
            ),
        ),
        migrations.AlterField(
            model_name="textmessage",
            name="sender",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="textmessages",
                to="botreader.user",
            ),
        ),
        migrations.CreateModel(
            name="GeneratedAnswer",
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
                ("human_answer", models.TextField(blank=True)),
                ("ai_answer", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("DRAFT", "Draft"),
                            ("SENDING", "Sending"),
                            ("SENT", "Sent"),
                        ],
                        default="DRAFT",
                        max_length=7,
                    ),
                ),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "textmessage",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="generated_answer",
                        to="botreader.textmessage",
                    ),
                ),
            ],
        ),
    ]
