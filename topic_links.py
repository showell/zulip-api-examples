import re
import zulip
from urllib.parse import urlparse

DEVELOPMENT = False

global client
global host

if DEVELOPMENT:
    print("In development env...")
    stream_list = ["devel"]
    client = zulip.Client(config_file="./zuliprc")
    BOT_REGEX = r"(.*)-bot@(zulipdev.com|zulip.com)$"
else:
    BOT_REGEX = r"(.*)-bot@(chat.zulip.org|zulip.com)$"
    client = zulip.Client(config_file="/home/ubuntu/zuliprc")
    stream_list = [
        "settings system",
        "api design",
        "backend",
        "chat.zulip.org",
        "design",
        "frontend",
        "feedback",
        "issues",
        "general",
    ]


parsed_url = urlparse(client.base_url)
host = parsed_url.scheme + "://" + parsed_url.netloc
print(host)


def send(content, topic, stream):
    # https://zulip.com/api/send-message
    request = {
        "type": "stream",
        "to": stream,
        "topic": topic,
        "content": content,
    }
    client.send_message(request)
    print(f"sent->{content}")


def handle_message(msg):
    if msg["type"] != "stream":
        print("Ignoring DM...")
        return
    if re.match(BOT_REGEX, msg["sender_email"]):
        return

    TOPIC_LINK_RE = r"(\#\*\*(.*?)>(.*?)\*\*)"

    content = msg["content"]

    stream = msg["display_recipient"]
    topic = msg["subject"]

    if stream not in stream_list:
        return
    from_topic_link = f"#**{stream}>{topic}**"
    user_id = msg["sender_id"]
    user_name = msg["sender_full_name"]
    sender = f"@_**{user_name}|{user_id}**"
    stream_id = msg["stream_id"]
    near_link = (
        host + f"/#narrow/stream/{stream_id}-{stream}/topic/{topic}/near/{msg['id']}"
    )
    for tagged_topic_link, tagged_stream, tagged_topic in re.findall(
        TOPIC_LINK_RE, content
    ):
        if tagged_topic_link == from_topic_link or tagged_stream not in stream_list:
            continue
        msg = (
            f"{sender} mentioned this topic in **[#{stream} > {topic}]({near_link})**."
        )
        send(msg, tagged_topic, tagged_stream)


def watch_messages():
    def handle_event(event):
        if "message" not in event:
            # ignore heartbeat events
            return
        handle_message(event["message"])

    # https://zulip.com/api/real-time-events
    client.call_on_each_event(
        handle_event, event_types=["message"], all_public_streams=True
    )


def get_recent_messages():
    # Use this as alternative to watch_messages if you want to create links for some recent
    # messages.
    narrow = [dict(operator="streams", operand="public")]
    request = dict(
        anchor="newest",
        apply_markdown=False,
        narrow=narrow,
        num_after=0,
        num_before=20,
    )
    result = client.get_messages(request)

    for message in result["messages"]:
        handle_message(message)


watch_messages()
