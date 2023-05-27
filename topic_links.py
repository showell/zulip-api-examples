import re
import zulip

# CONFIG: change these for your installation
STREAM_FOR_NOTIFICATIONS = "bot testing"
TOPIC_NAME_FOR_NOTIFICATIONS = "topic links"

client = zulip.Client(config_file="~/zuliprc")

def send(content):
    # https://zulip.com/api/send-message
    request = {
        "type": "stream",
        "to": STREAM_FOR_NOTIFICATIONS,
        "topic": TOPIC_NAME_FOR_NOTIFICATIONS,
        "content": content,
    }
    print ("sending", content)
    result = client.send_message(request)

def handle_message(msg):
    if msg["type"] != "stream":
        print("ignoring DM")
        return

    TOPIC_LINK_RE = "(\#\*\*.*?>.*?\*\*)"

    content = msg["content"]
    if "#**" in content and not "links to" in content:
        stream = msg["display_recipient"]
        topic = msg["subject"]

        if topic == TOPIC_NAME_FOR_NOTIFICATIONS:
            return

        from_topic_link = f"#**{stream}>{topic}**"

        for to_topic_link in re.findall(TOPIC_LINK_RE, content):
            new_content = f"{from_topic_link} links to {to_topic_link}"
            send(new_content)

def watch_messages():
    print("Watching for messages...")
    def handle_event(event):
        if "message" not in event:
            # ignore heartbeat events
            return
        handle_message(event["message"])

    # https://zulip.com/api/real-time-events
    client.call_on_each_event(handle_event, event_types=["message"], all_public_streams=True)

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
