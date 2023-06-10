import re
import zulip
from urllib import parse

DEVELOPMENT = False

global client
global host

if DEVELOPMENT:
    print("In development env...")
    stream_list = ["devel dev #@-)"]
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


def encode_hash_component(id):
    return parse.quote(id)


parsed_url = parse.urlparse(client.base_url)
host = parsed_url.scheme + "://" + parsed_url.netloc
print(host)


def get_near_link(msg_id, stream_id, stream_name, topic):
    stream_name = stream_name.replace(" ", "-")
    msg_id = encode_hash_component(str(msg_id))
    stream_slug = encode_hash_component(f"{stream_id}-{stream_name}")
    topic_slug = encode_hash_component(topic)
    return host + f"/#narrow/stream/{stream_slug}/topic/{topic_slug}/near/{msg_id}"


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
    stream_id = msg["stream_id"]
    topic = msg["subject"]

    if stream not in stream_list:
        return

    from_topic_link = f"#**{stream}>{topic}**"
    user_id = msg["sender_id"]
    user_name = msg["sender_full_name"]

    sender = f"@_**{user_name}|{user_id}**"

    msg_id = msg["id"]

    near_link = get_near_link(msg_id, stream_id, stream, topic)
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


watch_messages()
