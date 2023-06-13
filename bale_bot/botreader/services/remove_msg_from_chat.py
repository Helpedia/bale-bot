import json
import requests
import datetime
import logging
from bale_bot.settings import BALE_BOT_BASE_URL, LEGAL_HOURS_FOR_MESSAGE_FORWARDING

from ..models import Chat
from .helpers import get_or_create_user

logger = logging.getLogger(__name__)


def remove_forwarded_messages_in_illegal_hours(message):
    if not "forward_from_message_id" in message and not "forward_from" in message and not "forward_from_chat" in message:
        raise ValueError("forward_from_message_id object is required")

    chat_id = message["chat"]["id"]

    # check message time is invalid
    start_legal_hour, end_legal_hour = LEGAL_HOURS_FOR_MESSAGE_FORWARDING.split("-")
    start_legal_hour = int(start_legal_hour)
    end_legal_hour = int(end_legal_hour)
    date = datetime.datetime.fromtimestamp(message["date"])
    message_hour = date.time().hour
    if message_hour >= start_legal_hour and message_hour < end_legal_hour:
        return

    # check sender user is not admin
    try:
        admin_users = __get_and_update_admin_users(chat_id)
    except PermissionError as e:
        logger.error(
            "Remove forwarded message service canceled Due to lack of admin permission to the bot"
        )
        return
    sender_user_id = message["from"]["id"]
    for admin in admin_users:
        if sender_user_id == admin["user"]["id"]:
            return

    # delete forwarded message
    __delete_message(chat_id, message["message_id"])


def __delete_message(chat_id, message_id):
    delete_message_url = BALE_BOT_BASE_URL + "deletemessage"
    try:
        for i in range(0, 3):
            request = requests.post(
                url=delete_message_url,
                data=[("chat_id", chat_id), ("message_id", message_id)],
            )
            if request.status_code == 200:
                break
        if request.status_code == 200:
            logger.info(
                "message with id:[{message_id}] in chat with id:[{chat_id}] deleted successfully".format(
                    message_id=message_id, chat_id=chat_id
                )
            )
        else:
            logger.error(
                "Did not delete message with id:[{message_id}] in chat with id:[{chat_id}] with 3 times trying".format(
                    message_id=message_id, chat_id=chat_id
                )
            )
    except Exception as e:
        print("%s" % type(e))


def __get_and_update_admin_users(chat_id):
    # get chat admins
    get_admin_url = (
        BALE_BOT_BASE_URL + "getChatAdministrators" + "?chat_id=" + str(chat_id)
    )
    call_result = None
    while call_result is None or "ok" not in call_result:
        call_result = call_service(get_admin_url)
    if (
        "description" in call_result
        and call_result["description"] == "permission_denied"
    ):
        logger.error("Get group admins failed -> Bot is not admin of group")
        raise PermissionError("bot need admin access")
    admin_users = call_result.get("result", [])

    # update chat admins
    chat = Chat.objects.get(id=chat_id)
    admins = []
    for admin in admin_users:
        user = get_or_create_user(
            uid=admin["user"]["id"],
            name=admin["user"]["first_name"],
            username=admin["user"]["username"],
        )
        admins.append(user)
    chat.admins.set(admins)

    return admin_users


def call_service(url):
    try:
        content = requests.post(url).text
        parsed_data = json.loads(content)
        return parsed_data
    except Exception as e:
        print("%s" % type(e))
