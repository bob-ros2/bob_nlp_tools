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


class NormalizerNode(Node):
    """
    ROS 2 Node that normalizes messages into structured formats.

    Uses NlpSemanticDriver to perform normalization.
    """

    def __init__(self):
        """Initialize NormalizerNode."""
        super().__init__('normalizer')

        self.declare_parameters(
            namespace='',
            parameters=[
                ('api_key', os.getenv('NLP_API_KEY', 'not-set'),
                 ParameterDescriptor(description='API key for the NLP provider.')),

                ('base_url', os.getenv('NLP_BASE_URL', 'http://localhost:1234/v1'),
                 ParameterDescriptor(description='Base URL for the OpenAI-compatible API.')),

                ('model', os.getenv('NLP_MODEL', 'gpt-3.5-turbo'),
                 ParameterDescriptor(description='Model name to use for normalization.')),

                ('instructions', 'Transform to pure JSON format: {"action": "verb", "target": "object"}',
                 ParameterDescriptor(description='Normalization instructions for the LLM.'))
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

        self.instructions = self.get_parameter('instructions').value

        # Publishers
        self.pub = self.create_publisher(String, 'topic_out', 10)

        # Subscription
        self.subscription = self.create_subscription(
            String,
            'topic_in',
            self.input_callback,
            10
        )

        self.get_logger().info('Normalizer initialized.')

    def input_callback(self, msg):
        """Analyze message and normalize it."""
        self.get_logger().debug(f'Normalizing message: {msg.data}')

        normalized = self.driver.normalize(msg.data, self.instructions)
        if normalized:
            self.get_logger().info('Normalization successful.')
            out_msg = String()
            out_msg.data = normalized
            self.pub.publish(out_msg)
        else:
            self.get_logger().warn('Normalization failed.')


def main(args=None):
    """Run the main ROS 2 node."""
    rclpy.init(args=args)
    node = NormalizerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
