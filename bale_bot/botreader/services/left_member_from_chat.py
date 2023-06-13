import datetime
import logging

from ..models import Chat, User, ChatEvent, Membership
from .helpers import get_or_create_user, get_or_create_chat

logger = logging.getLogger(__name__)



def left_member_from_chat(message):
    if not 'left_chat_member' in message:
        raise ValueError('left_chat_member object is required')
    left_chat_member = message['left_chat_member']
    uid = left_chat_member['id']
    name = left_chat_member['first_name']
    username = left_chat_member['username']
    date = datetime.datetime.fromtimestamp(message['date'])
    chat_id = message['chat']['id']

    # get user
    user = get_or_create_user(uid, username, name)

    # get chat
    chat = get_or_create_chat(message['chat'])

    # set exited in membership and log in chat event
    membership, created = Membership.objects.get_or_create(chat=chat, member=user)
    membership.exited = True
    membership.save()
    if not ChatEvent.objects.filter(user=user.uid, chat=chat_id, date=date, event_type=ChatEvent.EventType.EXIT).count() > 0:
        ChatEvent.objects.create(
            user=user, chat=chat, date=date, event_type=ChatEvent.EventType.EXIT)
