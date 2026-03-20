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


class SemanticFilterNode(Node):
    """
    ROS 2 Node that filters messages based on semantic criteria.

    Uses NlpSemanticDriver to determine if a message matches the criterion.
    """

    def __init__(self):
        """Initialize SemanticFilterNode."""
        super().__init__('semantic_filter')

        self.declare_parameters(
            namespace='',
            parameters=[
                ('api_key', os.getenv('NLP_API_KEY', 'not-set'),
                 ParameterDescriptor(description='API key for the NLP provider.')),

                ('base_url', os.getenv('NLP_BASE_URL', 'http://localhost:1234/v1'),
                 ParameterDescriptor(description='Base URL for the OpenAI-compatible API.')),

                ('model', os.getenv('NLP_MODEL', 'gpt-3.5-turbo'),
                 ParameterDescriptor(description='Model name to use for filtering.')),

                ('criterion', 'Is a friendly greeting',
                 ParameterDescriptor(description='Semantic criterion for the filter.'))
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

        self.criterion = self.get_parameter('criterion').value

        # Publishers
        self.pub = self.create_publisher(String, 'topic_out', 10)
        self.pub_rejected = self.create_publisher(String, 'topic_rejected', 10)

        # Subscription
        self.subscription = self.create_subscription(
            String,
            'topic_in',
            self.input_callback,
            10
        )

        self.get_logger().info(f'Semantic Filter initialized with criterion: {self.criterion}')

    def input_callback(self, msg):
        """Analyze message and filter it."""
        self.get_logger().debug(f'Filtering message: {msg.data}')

        if self.driver.semantic_filter(msg.data, self.criterion):
            self.get_logger().info(f'MSG PASS: {msg.data} meets {self.criterion}')
            self.pub.publish(msg)
        else:
            self.get_logger().info(f'MSG REJECT: {msg.data} fails {self.criterion}')
            self.pub_rejected.publish(msg)


def main(args=None):
    """Run the main ROS 2 node."""
    rclpy.init(args=args)
    node = SemanticFilterNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
