import re
import zulip

client = zulip.Client(config_file="~/zuliprc")
stream_list = ["test here"]

BOT_REGEX = r"(.*)-bot@chat.zulip.org$"


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

    for tagged_topic_link, tagged_stream, tagged_topic in re.findall(
        TOPIC_LINK_RE, content
    ):
        if tagged_topic_link == from_topic_link or tagged_stream not in stream_list:
            continue
        msg = f"This topic was mentioned in {from_topic_link}"
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
