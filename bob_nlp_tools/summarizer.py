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

import os

from bob_nlp_tools import NlpSemanticDriver
from rcl_interfaces.msg import ParameterDescriptor
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SummarizerNode(Node):
    """
    ROS 2 Node that summarizes messages based on semantic criteria.

    Uses NlpSemanticDriver to generate summarizes.
    """

    def __init__(self):
        """Initialize SummarizerNode."""
        super().__init__('summarizer')

        self.declare_parameters(
            namespace='',
            parameters=[
                ('api_key', os.getenv('SUMMARIZER_API_KEY', 'not-set'),
                 ParameterDescriptor(description='API key (env: SUMMARIZER_API_KEY).')),

                ('base_url', os.getenv('SUMMARIZER_BASE_URL', 'http://localhost:1234/v1'),
                 ParameterDescriptor(description='Base URL (env: SUMMARIZER_BASE_URL).')),

                ('model', os.getenv('SUMMARIZER_MODEL', 'gpt-3.5-turbo'),
                 ParameterDescriptor(description='Model name (env: SUMMARIZER_MODEL).')),

                ('context', 'Latest system activity',
                 ParameterDescriptor(description='Context of the summarization task.')),

                ('max_words', 50,
                 ParameterDescriptor(description='Maximum number of words for the summary.'))
            ]
        )

        # Initialize Driver
        api_key = self.get_parameter('api_key').value
        base_url = self.get_parameter('base_url').value
        model = self.get_parameter('model').value

        self.driver = NlpSemanticDriver(
            api_key=api_key,
            base_url=base_url,
            model=model
        )

        self.context = self.get_parameter('context').value
        self.max_words = self.get_parameter('max_words').value

        # Publishers
        self.pub = self.create_publisher(String, 'topic_out', 10)

        # Subscription
        self.subscription = self.create_subscription(
            String,
            'topic_in',
            self.input_callback,
            10
        )

        self.get_logger().info(f'Summarizer initialized with context: {self.context}')

    def input_callback(self, msg):
        """Analyze message and summarize it."""
        self.get_logger().debug(f'Summarizing message of {len(msg.data)} chars.')

        summary = self.driver.summarize(msg.data, self.context, self.max_words)
        if summary:
            self.get_logger().info('Summary generated.')
            out_msg = String()
            out_msg.data = summary
            self.pub.publish(out_msg)
        else:
            self.get_logger().warn('Summarizer returned no content.')


def main(args=None):
    """Run the main ROS 2 node."""
    rclpy.init(args=args)
    node = SummarizerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
