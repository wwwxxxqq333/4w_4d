#!/usr/bin/env python3
"""
Four-Wheel Independent Drive & Steering (FWIDS) Kinematic Controller.

Kinematics model:
  δi     = atan2(vy + ω·xi,  vx - ω·yi)
  vwheel = sqrt((vx - ω·yi)² + (vy + ω·xi)²)

Subscribes to /cmd_vel (Twist) and publishes Float64MultiArray to each
wheel's individual steer (position) and rotor (velocity) controller topic.
"""

import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray


class FWIDSKinematicController(Node):
    def __init__(self):
        super().__init__("fwids_kinematic_controller")

        self.tire_radius = 0.2

        # Wheel positions (xi, yi) from vehicle center
        self.wheels = {
            "front_left":  ( 0.5,  0.5),
            "front_right": ( 0.5, -0.5),
            "rear_left":   (-0.5,  0.5),
            "rear_right":  (-0.5, -0.5),
        }

        self.steer_pubs = {}
        self.rotor_pubs = {}
        for name in self.wheels:
            self.steer_pubs[name] = self.create_publisher(
                Float64MultiArray, f"/{name}_steer_controller/commands", 10)
            self.rotor_pubs[name] = self.create_publisher(
                Float64MultiArray, f"/{name}_rotor_controller/commands", 10)

        # Low-pass filtered rotor velocity (per wheel) to prevent instant jumps
        self._rotor_vel = {name: 0.0 for name in self.wheels}
        self._max_accel = 2.0  # max rotor accel (rad/s²), i.e. 0.4 m/s² linear

        self.sub = self.create_subscription(
            Twist, "/cmd_vel", self.cmd_vel_callback, 10)

        self.get_logger().info(
            "FWIDS Kinematic Controller ready, listening on /cmd_vel")

    def cmd_vel_callback(self, msg: Twist):
        vx = msg.linear.x
        vy = msg.linear.y
        omega = msg.angular.z

        dt = 0.02  # ~50 Hz callback rate

        for name, (xi, yi) in self.wheels.items():
            # Steering angle
            delta = math.atan2(vy + omega * xi, vx - omega * yi)

            # Wheel linear speed
            v_wheel = math.sqrt(
                (vx - omega * yi) ** 2 + (vy + omega * xi) ** 2)

            # Target rotor angular velocity (rad/s), sign-flipped for forward
            target = -v_wheel / self.tire_radius

            # Rate-limit: clamp acceleration
            prev = self._rotor_vel[name]
            max_step = self._max_accel * dt
            limited = max(prev - max_step, min(prev + max_step, target))
            self._rotor_vel[name] = limited

            sm = Float64MultiArray()
            sm.data = [delta]
            self.steer_pubs[name].publish(sm)

            rm = Float64MultiArray()
            rm.data = [limited]
            self.rotor_pubs[name].publish(rm)

        if omega == 0.0 and vy == 0.0:
            self.get_logger().info(
                f"Forward: vx={vx:.2f} m/s, rotor={-vx / self.tire_radius:.2f} rad/s")
        elif vx == 0.0 and vy == 0.0:
            self.get_logger().info(f"Rotation: omega={omega:.2f} rad/s")


def main(args=None):
    rclpy.init(args=args)
    node = FWIDSKinematicController()
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
