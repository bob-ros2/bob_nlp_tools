#
# Copyright 2026 Bob Ros
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import json
import logging
import os

import requests


class NlpSemanticDriver:
    """A standalone, non-ROS driver for semantic NLP tasks via OpenAI-compatible APIs."""

    def __init__(self, api_key, base_url='https://api.openai.com/v1', model='gpt-3.5-turbo',
                 timeout=15):
        """Initialize semantic driver."""
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = timeout

        self.logger = logging.getLogger('NlpSemanticDriver')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def ask(self, system_prompt, user_input, temperature=0.0):
        """Perform base chat completion call."""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_input}
            ],
            'temperature': temperature
        }

        try:
            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                data=json.dumps(payload),
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content'].strip()
        except Exception as e:
            self.logger.error(f'API Request failed: {e}')
            return None

    def route(self, content, targets: dict):
        """
        Perform semantic routing.

        Given content and a dict of targets {key: description},
        returns the best matching key.
        """
        options = '\n'.join([f'- {k}: {v}' for k, v in targets.items()])
        default_prompt = (
            'You are a semantic router. Analyze the user input and choose exactly ONE key '
            'from the following list that matches best. Respond ONLY with the raw key name, '
            'nothing else.\n\n'
            'Available Keys:\n{options}'
        )
        system_prompt = os.getenv('SEMANTIC_SYSTEM_PROMPT', default_prompt).format(options=options)

        result = self.ask(system_prompt, content)
        if result and result in targets:
            return result

        # Fallback if the LLM hallucinated but the key is hidden in text
        if result:
            for k in targets:
                if k.lower() in result.lower():
                    return k
        return None

    def semantic_filter(self, content, criterion):
        """Perform semantic check. Returns True if content meets the criterion."""
        default_prompt = (
            "Analyze the following input. If it matches the criterion '{criterion}', "
            "respond with 'YES'. If it does not match, respond with 'NO'. "
            "Respond ONLY with 'YES' or 'NO'."
        )
        system_prompt = os.getenv('FILTER_SYSTEM_PROMPT', default_prompt)
        system_prompt = system_prompt.format(criterion=criterion)

        result = self.ask(system_prompt, content)
        if result:
            return 'YES' in result.upper()
        return False

    def summarize(self, content, context='', max_words=50):
        """Perform semantic summary helper."""
        default_prompt = (
            'Summarize the following content in the context of: {context}. '
            'The summary must be short, precise and not exceed {max_words} words.'
        )
        system_prompt = os.getenv('SUMMARIZE_SYSTEM_PROMPT', default_prompt).format(
            context=context, max_words=max_words)

        return self.ask(system_prompt, content)

    def normalize(self, content, instructions='Transform to valid JSON'):
        """Normalize input based on descriptive instructions."""
        default_prompt = (
            'Normalize the input according to these instructions: {instructions}. '
            'Respond ONLY with the clean output, no conversational filler.'
        )
        system_prompt = os.getenv('NORMALIZE_SYSTEM_PROMPT', default_prompt).format(
            instructions=instructions)

        return self.ask(system_prompt, content)
