import zulip

# Pass the path to your zuliprc file here.
client = zulip.Client(config_file="~/.zuliprc")

def send(content):
    # Send a stream message
    request = {
        "type": "stream",
        "to": "bot testing",
        "topic": "steve bot",
        "content": content,
    }
    result = client.send_message(request)

def handle_event(event):
    if event["type"] != "user_status":
        return
    user_id = event["user_id"]
    user = client.get_user_by_id(user_id)["user"]
    user_name = user["full_name"]
    send(f"{user_name} changed their status")
    print("message sent")

client.call_on_each_event(handle_event)
