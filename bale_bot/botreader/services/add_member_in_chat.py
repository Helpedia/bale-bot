import logging
from datetime import datetime, timedelta

from bale_bot.settings import WELCOME_MESSAGE
from .helpers import get_or_create_user, get_or_create_chat, send_message
from ..models import Chat, User, ChatEvent, Membership

MAXIMUM_TIME_INTERVAL_BETWEEN_RECEIVING_AND_SEND_WELCOME_MESSAGE_IN_MINUTES = 10

logger = logging.getLogger(__name__)

def adding_new_member_in_chat(message):
    if not 'new_chat_members' in message:
        raise ValueError('new_chat_members object is required')
    new_chat_member = message['new_chat_members'][0]
    uid = new_chat_member['id']
    name = new_chat_member['first_name']
    username = new_chat_member['username']
    date = datetime.fromtimestamp(message['date'])
    inviterUid = message['from']['id']
    chat_id = message['chat']['id']

    # get user
    user = get_or_create_user(uid, username, name)

    # get chat
    chat = get_or_create_chat(message['chat'])

    # add user to membership
    membership, created = Membership.objects.get_or_create(chat=chat, member=user)
    membership.exited = False
    membership.last_membership_date = date
    membership.save()
    # add user to ChatEvent & send welcome message
    inviterUser = User.objects.filter(uid=inviterUid).last()
    if not ChatEvent.objects.filter(user=user.uid, chat=chat_id, date=date, event_type=ChatEvent.EventType.ENTRY).count() > 0:
        ChatEvent.objects.create(
            user=user, chat=chat, date=date, inviterUser=inviterUser, event_type=ChatEvent.EventType.ENTRY)        
        # send message if only some minutes have not passed
        if datetime.now() - date < timedelta(minutes=MAXIMUM_TIME_INTERVAL_BETWEEN_RECEIVING_AND_SEND_WELCOME_MESSAGE_IN_MINUTES):
            send_welcome_message(
                chat_id=chat.id, group_name=chat.title, member_name=user.name, member_username=user.username)


def send_welcome_message(chat_id, group_name, member_name, member_username):
    if member_username is None or len(member_username) < 2:
        username = ''
    else:
        username = '@' + member_username
    message = WELCOME_MESSAGE.format(
        user_name=member_name, user_username=username, group_name=group_name, new_line='\n')
    send_message(chat_id, message)
