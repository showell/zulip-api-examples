import zulip

# Pass the path to your zuliprc file here.
client = zulip.Client(config_file="~/zuliprc")

def send(content):
    # Send a stream message
    request = {
        "type": "stream",
        "to": "bot testing",
        "topic": "status changes",
        "content": content,
    }
    client.send_message(request)
    print("sent -> ", content)

def handle_event(event):
    if event["type"] != "user_status":
        return
    user_id = event["user_id"]
    user = client.get_user_by_id(user_id)["user"]
    user_name = user["full_name"]
    status_text = event["status_text"]
    emoji_name = event["emoji_name"]
    if status_text == "" and emoji_name == "":
        send(f"@_**{user_name}|{user_id}** cleared their status.")
        return
    emoji = ""
    if emoji_name:
        emoji = f":{emoji_name}:"
    message = f"@_**{user_name}|{user_id}** changed their status to **{emoji} {status_text}**."
    send(message)

print("waiting for changes...")
client.call_on_each_event(handle_event)
