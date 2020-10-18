import random
import datetime
import logging

from telethon import TelegramClient, events, types, functions

from antispam_userbot.config import SESSION_PATH, API_ID, SECRET
from antispam_userbot.scheduler import scheduler
from antispam_userbot.model.known_user import KnownUser
from antispam_userbot.model.challenge import Challenge


client = TelegramClient(SESSION_PATH, API_ID, SECRET)
log = logging.getLogger("antispam_bot")

EMOJI_MAP = {
    "🤖": {
        "ru": "роботов",
        "en": "robots"
    },
    "🦈": {
        "ru": "акул",
        "en": "sharks"
    },
    "🇺🇸": {
        "ru": "флагов США",
        "en": "USA banners"
    }
}

MESSAGE = {
    "ru": "Похоже я вас не знаю, пожалуйста решите задачку:\n"
          "{challenge}\n"
          "Сколько в тексте выше {emoji_right}\nУ вас есть 1 минута, чтобы ответить на вопрос, "
          "иначе вы будете отправлены в черный список.\n",
    "en": "Seems like i dont know you, please solve this:\n"
          "{challenge}"
          "\nHow many {emoji_right} are there in line above?\n"
          "You have 1 minute to answer otherwise you will be blocked.\n"
}

SUCCESS_MESSAGE = {
    "ru": "Вы решили задачку верно! ",
    "en": "You did it! "
}

FAILURE_MESSAGE = {
    "ru": "Неверный ответ! Попробуйте еще раз.",
    "en": "Wrong answer! Please try again."
}


def challenge() -> tuple[str, int]:
    """Creates a text challenge for unknown user."""

    emoji_right = random.choice(list(EMOJI_MAP.keys()))
    emoji_right_count = None
    emojis = []
    for emoji in EMOJI_MAP:
        emoji_count = random.randrange(0, 8)
        for _ in range(emoji_count):
            emojis.append(emoji)
        if emoji == emoji_right:
            emoji_right_count = emoji_count
    random.shuffle(emojis)

    message_text = "ERROR!\n"
    for language, text in MESSAGE.items():
        message_text += text.format(challenge="".join(emojis),
                                    emoji_right=EMOJI_MAP[emoji_right][language])
    return message_text, emoji_right_count


async def check_user(event: events.NewMessage.Event):
    """Checks that either user in known users or in contacts."""

    if event.chat is None:
        contacts = await client(functions.contacts.GetContactsRequest(hash=0))
        if event.message.peer_id in [contact.user_id for contact in contacts.contacts]:
            return False
        elif await KnownUser.find_by_id(event.chat_id):
            return False
        elif await Challenge.one(event.chat_id, required=False):
            return False
        return True
    else:
        return False


async def user_with_challenge(event):
    """Checks if user with challenge."""

    if await Challenge.one(event.chat_id, required=False):
        return True
    return False


async def report_and_block_user(user_id):
    """Reports and blocks user."""

    log.info("Blocking %s", user_id)
    await client(functions.messages.ReportSpamRequest(user_id))
    await client.delete_dialog(user_id)
    await client(functions.contacts.BlockRequest(user_id))


@client.on(events.NewMessage(func=user_with_challenge, incoming=True))
async def check_challenge(event: events.NewMessage.Event):
    """Checks if user solved challenge right."""

    db_challenge = await Challenge.one(event.chat_id)
    if str(db_challenge.correct_answer) == event.message.message:
        await KnownUser.create(user_id=event.chat_id)
        scheduler.remove_job(f"{event.chat_id}.report_user")
        scheduler.remove_job(f"{event.chat_id}.delete_challenge")
        await db_challenge.delete()
        await client.send_message(event.chat_id, "\n".join(SUCCESS_MESSAGE.values()))
    else:
        await client.send_message(event.chat_id, "\n".join(FAILURE_MESSAGE.values()))
        await client.send_read_acknowledge(event.chat_id)


@client.on(events.NewMessage(func=check_user, incoming=True))
async def unknown_user_message(event: events.NewMessage.Event):
    """Sends challenge for unknown user."""

    challenge_text, correct_answer = challenge()
    await client.send_message(event.chat_id, challenge_text)
    await Challenge.create(event.chat_id, correct_answer)
    trigger_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=60)
    scheduler.add_job(Challenge.find_and_delete, "date",
                      id=f"{event.chat_id}.delete_challenge",
                      run_date=trigger_time,
                      args=[event.chat_id])
    scheduler.add_job(report_and_block_user, "date",
                      id=f"{event.chat_id}.report_user",
                      run_date=trigger_time,
                      args=[event.chat_id])
    await client.send_read_acknowledge(event.chat_id)


@client.on(events.NewMessage(outgoing=True))
async def save_known_user(event: events.NewMessage.Event):
    """Saves user to known if you write to him."""

    if event.chat is None:
        await KnownUser.find_or_create(event.chat_id)
        scheduler.remove_job(f"{event.chat_id}.report_user")

client.start()
scheduler.start()
client.run_until_disconnected()
