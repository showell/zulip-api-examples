import os
import sys

from langchain.llms import OpenAI
from langchain import LLMChain, PromptTemplate

import zulip

ZULIP_CONFIG_FILE = "~/zuliprc_issa"
PROMPT_TEMPLATE = """Question: {question}

Answer: I want you to act like you are Issa Rae.
You are doing a media tour to promote the last season
of your hit TV show "Insecure", and you may also end
up talking about upcoming projects."""

class LangChainZulip:
    def __init__(self):
        prompt = PromptTemplate(template=PROMPT_TEMPLATE, input_variables=["question"])
        self.llm_chain = LLMChain(prompt=prompt, llm=OpenAI())

    def process_message(self, message: str) -> None:
        print(message)
        response = self.llm_chain.run(message)
        print(response)
        return response


if "OPENAI_API_KEY" not in os.environ:
    raise Exception("you need a key")
print("token", os.environ["OPENAI_API_KEY"])
zulip_client = zulip.Client(config_file=ZULIP_CONFIG_FILE)
lcz = LangChainZulip()

def handle_message(msg) -> None:
    print("processing", msg)
    if msg["type"] != "stream":
        return

    message = msg["content"]
    content = lcz.process_message(message)
    request = {
        "type": "stream",
        "to": msg["display_recipient"],
        "topic": msg["subject"],
        "content": content,
    }
    print("sending", content)
    zulip_client.send_message(request)


def watch_messages() -> None:
    print("Watching for messages...")

    def handle_event(event) -> None:
        if "message" not in event:
            # ignore heartbeat events
            return
        handle_message(event["message"])

    # https://zulip.com/api/real-time-events
    narrow = [["is", "mentioned"]]
    zulip_client.call_on_each_event(
        handle_event, event_types=["message"], all_public_streams=True, narrow=narrow
    )


watch_messages()
