from django.db import models
from django.contrib.postgres.fields import ArrayField
from uuid import uuid4
from django.utils import timezone


class UpdateId(models.Model):
    update_id = models.BigIntegerField()


class TextMessage(models.Model):
    TEXT_MESSAGE_TYPE = [
        ("", "----"),
        ("QUESTION", "Question"),
        ("ANSWER", "Answer"),
        ("SUGGESTION", "Suggestion"),
        ("ADVERTISEMENT", "Advertisement"),
        ("STATEMENT", "Statement"),
        ("SELL", "Sell"),
        ("TRASH", "Trash"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid4)
    message_id = models.BigIntegerField(unique=True)
    sender = models.ForeignKey(
        "User", on_delete=models.PROTECT, related_name="textmessages", null=True
    )
    chat = models.ForeignKey(
        "Chat", on_delete=models.PROTECT, related_name="textmessages", null=True
    )
    date = models.DateTimeField()
    text = models.TextField()
    type = models.CharField(
        choices=TEXT_MESSAGE_TYPE, max_length=15, default="", blank=True
    )
    reply = models.ForeignKey("TextMessage", on_delete=models.PROTECT, null=True)

    def __str__(self):
        offset = 30
        if len(self.text) > offset:
            return f"{self.text[:offset]} ..."
        return self.text


class ArchivedTextMessage(models.Model):
    sid = models.CharField(max_length=50)
    chat_id = models.CharField(max_length=250, default="")
    text = models.TextField()
    hashtags = ArrayField(models.CharField(max_length=100), blank=True)

    def __str__(self):
        offset = 30
        if len(self.text) > offset:
            return f"{self.text[:offset]} ..."
        return self.text


class GeneratedAnswer(models.Model):
    STATUS_CHOICES = [("DRAFT", "Draft"), ("SENDING", "Sending"), ("SENT", "Sent")]
    human_answer = models.TextField(blank=True)
    ai_answer = models.TextField(blank=True)
    status = models.CharField(choices=STATUS_CHOICES, default="DRAFT", max_length=7)
    created_at = models.DateTimeField(default=timezone.now)
    textmessage = models.ForeignKey(
        to=TextMessage, related_name="generated_answer", on_delete=models.CASCADE
    )


class User(models.Model):
    TYPE_CHOICES = [
        ("", "----"),
        ("MANSOOR", "Mansoor"),
        ("NASER", "Naser"),
        ("NADER", "Nader"),
    ]
    uid = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=500)
    username = models.CharField(max_length=200, null=True)
    first_name = models.CharField(max_length=60, default="")
    last_name = models.CharField(max_length=60, default="")
    mobile = models.CharField(max_length=20, default="")
    type = models.CharField(choices=TYPE_CHOICES, max_length=10, default="")

    def __str__(self) -> str:
        name = f"{self.name}@{self.username}" if self.username else self.name
        return name


class Chat(models.Model):
    id = models.BigIntegerField(primary_key=True)
    type = models.CharField(max_length=200)
    title = models.CharField(max_length=300)
    username = models.CharField(max_length=500)
    first_name = models.CharField(max_length=500)
    last_name = models.CharField(max_length=500)
    admins = models.ManyToManyField(to=User, default=[], related_name="groups_admin")
    members = models.ManyToManyField(
        to=User, through="Membership", related_name="chats", blank=True
    )

    def __str__(self) -> str:
        if self.type == "private":
            full_name = f"{self.first_name} {self.last_name}".strip()
            title = f"{full_name}@{self.username}" if self.username else full_name
        else:
            title = self.title
        return title


class Membership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    member = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name="memberships", null=False
    )
    chat = models.ForeignKey(
        to=Chat, on_delete=models.CASCADE, related_name="memberships", null=False
    )
    exited = models.BooleanField(default=False)
    last_membership_date = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.chat} | {self.member}"


class ChatEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    date = models.DateTimeField()
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="groups", null=False
    )
    chat = models.ForeignKey(
        "Chat", on_delete=models.PROTECT, related_name="users", null=False
    )
    inviterUser = models.ForeignKey(
        "User", on_delete=models.PROTECT, related_name="invitedUsers", null=True
    )

    class EventType(models.TextChoices):
        ENTRY = "ENTRY"
        EXIT = "EXIT"

    event_type = models.CharField(
        max_length=10, choices=EventType.choices, default=EventType.ENTRY
    )
