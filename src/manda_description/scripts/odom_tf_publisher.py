#!/usr/bin/env python3
"""Bridge: /groundtruth_odom (nav_msgs/Odometry) → odom→base_footprint TF."""
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster


class OdomTfPublisher(Node):
    def __init__(self):
        super().__init__("odom_tf_publisher")
        self.tf_broadcaster = TransformBroadcaster(self)
        self.sub = self.create_subscription(
            Odometry, "/groundtruth_odom", self.callback, 10)
        self.get_logger().info("Publishing odom → base_footprint TF")

    def callback(self, msg: Odometry):
        t = TransformStamped()
        t.header.stamp = msg.header.stamp
        t.header.frame_id = "odom"
        t.child_frame_id = "base_footprint"
        t.transform.translation.x = msg.pose.pose.position.x
        t.transform.translation.y = msg.pose.pose.position.y
        t.transform.translation.z = msg.pose.pose.position.z
        t.transform.rotation = msg.pose.pose.orientation
        self.tf_broadcaster.sendTransform(t)


def main():
    rclpy.init()
    node = OdomTfPublisher()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        try:
            rclpy.shutdown()
        except rclpy.RCLError:
            pass


if __name__ == "__main__":
    main()
