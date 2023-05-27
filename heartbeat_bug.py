import zulip

client = zulip.Client(config_file="~/zuliprc")

def show_heartbeat_bug():
    print("You may need to wait a minute to see the symptom here...")
    def handle_event(event):
        if "message" not in event:
            print("HRM!!!! Do we really want a non-message event?")
            print(" Is it a heartbeat event?")
            print(event)
            return
        else:
            print("     We got an actual message, that is fine.")

    # https://zulip.com/api/real-time-events
    client.call_on_each_event(handle_event, event_types=["message"], all_public_streams=True)

show_heartbeat_bug()
