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
import os

from bob_nlp_tools import NlpSemanticDriver
from rcl_interfaces.msg import ParameterDescriptor
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SemanticRouterNode(Node):
    """
    ROS 2 Node that routes messages to different topics based on semantic intent.

    Uses NlpSemanticDriver to determine the best target topic.
    """

    def __init__(self):
        """Initialize SemanticRouterNode."""
        super().__init__('semantic_router')

        self.declare_parameters(
            namespace='',
            parameters=[
                ('api_key', os.getenv('ROUTER_API_KEY', 'not-set'),
                 ParameterDescriptor(description='API key (env: ROUTER_API_KEY).')),

                ('base_url', os.getenv('ROUTER_BASE_URL', 'http://localhost:1234/v1'),
                 ParameterDescriptor(description='Base URL (env: ROUTER_BASE_URL).')),

                ('model', os.getenv('ROUTER_MODEL', 'gpt-3.5-turbo'),
                 ParameterDescriptor(description='Model name (env: ROUTER_MODEL).')),

                ('targets', os.getenv('ROUTER_TARGETS', '{"default": "Default catch-all intent"}'),
                 ParameterDescriptor(description=(
                     'JSON dictionary of targets: {"topic_suffix": "Description of intent"}. '
                     'Can also be set via environment variable ROUTER_TARGETS.'))),

                ('default_target', os.getenv('ROUTER_DEFAULT_TARGET', 'unrouted'),
                 ParameterDescriptor(description=(
                     'Topic suffix to use if routing fails. '
                     'Can also be set via environment variable ROUTER_DEFAULT_TARGET.')))

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

        # Parse targets
        try:
            self.targets = json.loads(self.get_parameter('targets').value)
        except Exception as e:
            self.get_logger().error(f'Failed to parse targets JSON: {e}')
            self.targets = {}

        # Create Dynamic Publishers
        self.publishers_dict = {}
        for key in self.targets.keys():
            topic_name = f'~/out/{key}'
            self.publishers_dict[key] = self.create_publisher(String, topic_name, 10)
            self.get_logger().info(f'Created semantic gateway to: {topic_name}')

        self.default_pub = self.create_publisher(
            String, f'~/out/{self.get_parameter("default_target").value}', 10)

        # Main Subscription
        self.subscription = self.create_subscription(
            String,
            'topic_in',
            self.input_callback,
            10
        )

        self.get_logger().info('Semantic Router initialized.')

    def input_callback(self, msg):
        """Analyze message and route it."""
        if not self.targets:
            self.get_logger().warn('No targets defined. Message dropped.')
            return

        self.get_logger().debug(f'Routing message: {msg.data}')

        # Determining target key via Driver
        target_key = self.driver.route(msg.data, self.targets)

        if target_key and target_key in self.publishers_dict:
            self.get_logger().info(f'MSG ROUTE: {msg.data} -> [{target_key}]')
            self.publishers_dict[target_key].publish(msg)
        else:
            self.get_logger().warn(f'MSG UNROUTED: {msg.data} -> Using default fallback.')
            self.default_pub.publish(msg)


def main(args=None):
    """Run the main ROS 2 node."""
    rclpy.init(args=args)
    node = SemanticRouterNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
