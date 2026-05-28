#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    mppi_h_pkg = get_package_share_directory("mppi_h")
    config_file = os.path.join(mppi_h_pkg, "config", "mppi_h.yaml")

    mppi_h_node = Node(
        package="mppi_h",
        executable="mppi_h_node",
        name="mppi_h",
        output="screen",
        parameters=[config_file],
    )

    ld = LaunchDescription()
    ld.add_action(mppi_h_node)
    return ld