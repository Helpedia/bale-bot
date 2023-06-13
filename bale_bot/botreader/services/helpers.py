import requests
import logging

from ..models import Chat, User
from bale_bot.settings import BALE_BOT_BASE_URL

logger = logging.getLogger(__name__)

def get_or_create_user(uid, username, name):
    # The difference between this method and Django's get_or_create method 
    # is the get method only works based on id, not all fields.    
    try:
        user = User.objects.get(uid=uid)
        # Check if name or username of this user is updated
        if user.name != name or user.username != username:
            user.name = name
            user.username = username
            user.save()
    except User.DoesNotExist as e:
        user = User.objects.create(uid=uid, name=name, username=username)
    return user


def get_or_create_chat(message_chat):
    # The difference between this method and Django's get_or_create method 
    # is the get method only works based on id, not all fields.    
    try:
        chat = Chat.objects.get(id=message_chat['id'])
    except Chat.DoesNotExist as e:
        if 'title' in message_chat:
            title = message_chat['title']
        else:
            title = ''
        Chat.objects.create(id = message_chat['id'], first_name = message_chat['first_name'], last_name = message_chat['last_name'],
            username = message_chat['username'], type = message_chat['type'], title = title)
        chat = Chat.objects.get(id=message_chat['id'])
    return chat

def get_send_message_url():
    return BALE_BOT_BASE_URL + 'sendMessage'


def send_message(chat_id, message, reply_message_id=None):
    url = get_send_message_url()

    if reply_message_id is None:
        request_data = [('chat_id', chat_id), ('text', message)]
    else:
        request_data = [('chat_id', chat_id), ('text', message), ('reply_to_message_id', reply_message_id)]

    try:
        request = requests.post(
            url=url, data=request_data)
        if request.status_code == 200:
            logger.info(
                'message sent successfully for this chat_id : ' + str(chat_id))
            return True
        else:
            logger.error(
                'message can not send successfully with this error: ' + request.text)
            return False
    except Exception as e:
        print('%s' % type(e))
