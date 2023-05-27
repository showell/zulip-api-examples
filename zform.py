import json
import zulip

# Pass the path to your zuliprc file here.
client = zulip.Client(config_file="~/zuliprc_zform")

def send():
    choices = [
        dict(type="multiple_choice", short_name="Y", long_name="Yes, I understand", reply="yes"),
        dict(type="multiple_choice", short_name="N", long_name="No, I am confused", reply="no"),
    ]

    extra_data = dict(
        type="choices",
        heading="Please click a button",
        choices=choices,
    )

    widget_content = dict(
        widget_type="zform",
        extra_data=extra_data,
    )
    payload = json.dumps(widget_content)

    content = "(this is a widget, so it may not show up on mobile)"
    request = dict(
        type="stream",
        to="frontend",
        topic="zform fun",
        content=content,
        widget_content=payload,
    )
    result = client.send_message(request)

send()
