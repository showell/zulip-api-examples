import re
import zulip

# CONFIG: change these for your installation
STREAM_FOR_NOTIFICATIONS = "bot testing"
TOPIC_NAME_FOR_NOTIFICATIONS = "topic links"

client = zulip.Client(config_file="~/zuliprc_zform")

def handle_message(msg):
    if msg["type"] != "stream":
        return

    message = msg["content"]
    topic = msg["subject"]
    stream = msg["display_recipient"]
    link = f"#**{stream}>{topic}**"

    content = f"""
I saw that recently mentioned me on {link} with
the message of "{message}".  You must clicked a button, and Zulip
must have sent an automated reply **from** you.

While I appreciate you pinging me, my human overlord unfortunately
has re-tasked me with reading the entire works of Shakespeare, so
I cannnot follow up at this time.

Please contact him if you have any concerns.
"""
    request = {
        "type": "private",
        "to": [msg["sender_id"]],
        "content": content,
    }
    client.send_message(request)

def watch_messages():
    print("Watching for messages...")
    def handle_event(event):
        if "message" not in event:
            # ignore heartbeat events
            return
        handle_message(event["message"])

    # https://zulip.com/api/real-time-events
    client.call_on_each_event(handle_event, event_types=["message"])

def get_recent_messages():
    # Use this as alternative to watch_messages if you want to create links for some recent
    # messages.
    narrow = [dict(operator="streams", operand="public"), dict(operator="is", operand="mentioned")]
    request = dict(
        anchor="newest",
        apply_markdown=False,
        narrow=narrow,
        num_after=0,
        num_before=30,
    )
    result = client.get_messages(request)

    for message in result["messages"]:
        handle_message(message)

watch_messages()
