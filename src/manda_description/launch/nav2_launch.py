import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory("manda_description")
    nav2_share = get_package_share_directory("nav2_bringup")

    params_file = os.path.join(pkg_share, "config", "nav2_params.yaml")
    default_map = os.path.join(pkg_share, "..", "..", "..", "..", "map.yaml")
    map_file = LaunchConfiguration("map", default=default_map)
    use_rviz = LaunchConfiguration("use_rviz", default="true")

    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_share, "launch", "bringup_launch.py")
        ),
        launch_arguments={
            "map": map_file,
            "params_file": params_file,
            "use_sim_time": "true",
            "slam": "False",
            "use_composition": "False",
        }.items(),
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", os.path.join(
            nav2_share, "rviz", "nav2_default_view.rviz")],
        parameters=[{"use_sim_time": True}],
        condition=IfCondition(use_rviz),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "map", default_value=default_map,
                description="Path to map yaml"),
            DeclareLaunchArgument(
                "use_rviz", default_value="true",
                description="Launch RViz2"),
            nav2_bringup,
            rviz,
        ]
    )
