import json
import requests
import datetime
import logging
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from bale_bot.settings import BALE_BOT_BASE_URL, WELCOME_MESSAGE
from ..models import UpdateId
from ..models import TextMessage, UpdateId, Chat, GeneratedAnswer
from .helpers import get_or_create_user, get_or_create_chat, send_message
from .remove_msg_from_chat import remove_forwarded_messages_in_illegal_hours
from .add_member_in_chat import adding_new_member_in_chat
from .left_member_from_chat import left_member_from_chat

logger = logging.getLogger(__name__)

SENDING_ANSWER_STATE = "SENDING"
ANSWER_SENT_STATE = "SENT"


def new_messages_getter_scheduler():
    try:
        get_new_messages_and_save()
    except ValueError as e:
        logger.error(e)


@transaction.atomic
def get_new_messages_and_save():
    none_response_counter = 0
    while True:
        update = UpdateId.objects.all().first()
        url = get_update_message_url(update, BALE_BOT_BASE_URL)
        response = call_service(url)
        if response is None:
            logger.warning("None response is received")
            if none_response_counter == 3:
                raise ValueError(
                    "Get new messages and save failed because get None response 4 times"
                )
            else:
                none_response_counter += 1
                continue
        result = response["result"]
        if result is None:
            raise ValueError("Bad result received")
        if (
            update is not None
            and len(result) == 1
            and result[0]["update_id"] == update.update_id
        ):
            break
        update_offset(update, result)
        insert_messages(result)


def get_update_message_url(update: UpdateId, url):
    url += "getupdates"
    if update is not None:
        url += "?offset=" + str(update.update_id)
    return url


def update_offset(update, result):
    if update is None:
        if result:
            UpdateId.objects.create(update_id=result[-1]["update_id"])
    else:
        if result:
            update.update_id = result[-1]["update_id"]
        update.save()


def insert_messages(result):
    for res in result:
        if "message" in res:
            message = res["message"]
        elif "edited_message" in res:
            message = res["edited_message"]
        elif "callback_query" in res:
            message = res["callback_query"]["message"]
        else:
            raise ValueError("There is no readable content in message")

        if "message_id" in message:
            exist_message_id = TextMessage.objects.filter(
                message_id=message["message_id"]
            ).exists()
            if not exist_message_id:
                save_text_message(message)
            # if message exist and message_id is not about left or joins break
            if exist_message_id and message["message_id"] != 0:
                continue
        elif "new_chat_members" not in message and "left_chat_member" not in message:
            raise ValueError(
                "The message does not have an ID, nor is it an entry or exit message"
            )

        if "new_chat_members" in message:
            adding_new_member_in_chat(message)
        if "left_chat_member" in message:
            left_member_from_chat(message)
        if "forward_from_message_id" in message or "forward_from" in message or "forward_from_chat" in message:
            remove_forwarded_messages_in_illegal_hours(message)


def save_text_message(message):
    text_message = TextMessage()
    text_message.message_id = message["message_id"]
    text_message.date = datetime.datetime.fromtimestamp(message["date"])
    if "text" in message:
        text = message["text"]
        text = text.replace(chr(0), "") # remove null character 
        text_message.text = text
    if "caption" in message:
        text_message.text = message["caption"]
    if "from" in message:
        text_message.sender = get_or_create_user(
            uid=message["from"]["id"],
            username=message["from"]["username"],
            name=message["from"]["first_name"],
        )
    text_message.chat = get_or_create_chat(message["chat"])
    if "reply_to_message" in message:
        text_message.reply = TextMessage.objects.filter(
            message_id=message["reply_to_message"]["message_id"]
        ).first()
    text_message.save()


def save_chat(send_from):
    chat = Chat()
    chat.id = send_from["id"]
    chat.first_name = send_from["first_name"]
    chat.last_name = send_from["last_name"]
    chat.username = send_from["username"]
    chat.type = send_from["type"]
    if "title" in send_from:
        chat.title = send_from["title"]
    chat.save()
    return chat


def call_service(url):
    try:
        content = requests.post(url).text
        parsed_data = json.loads(content)
        return parsed_data
    except Exception as e:
        print("%s" % type(e))


@receiver(post_save, sender=GeneratedAnswer)
def answer_generation_handler(sender, instance, **kwargs):
    generated_answer_status = instance.status
    if generated_answer_status == SENDING_ANSWER_STATE:
        chat_id = instance.textmessage.chat.id
        main_message_id = instance.textmessage.message_id
        human_answer = instance.human_answer        
        send_result = send_message(chat_id, human_answer, main_message_id)
        if send_result:
            instance.status = ANSWER_SENT_STATE
            instance.save()
            logger.info("answer message with id [{answer_id}] sent successfully".format(answer_id = instance.id))
