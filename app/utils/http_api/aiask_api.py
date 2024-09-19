import requests
import time
import random


class AiAsk:
    def __init__(self, api_key):
        self.api_key = api_key
        self.domain = 'https://chat.hillstonenet.com'

    def stream_search(self, question, agent_name='tac_chat'):
        data = {
            'input': question
        }

        url = self.domain + f'/api/agent/{agent_name}/stream'
        header = {
            'Content-Type': 'application/json',
            'Api-Key': self.api_key
        }

        with requests.post(url, json=data, headers=header, stream=True, verify=False) as response:
            content = None
            for line in response.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("event:"):
                        content = f'{line}\n'
                        if line == 'event: end':
                            yield 'event: end\ndata: {"finish_reason":"stop"}\n\n'
                            time.sleep(round(random.uniform(0, 0.15), 2))

                    elif line.startswith("data:"):
                        content += f'{line}\n\n'
                        yield content
                        time.sleep(round(random.uniform(0, 0.15), 2))

