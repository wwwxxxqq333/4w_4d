import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory("manda_description")

    # ---- URDF ---------------------------------------------------------------
    urdf_path = os.path.join(pkg_share, "urdf", "fwids_vehicle.urdf")
    with open(urdf_path, "r") as f:
        robot_description = f.read()

    # Replace relative config path with absolute install path
    controller_yaml = os.path.join(pkg_share, "config", "fwids_controllers_ros2.yaml")
    robot_description = robot_description.replace(
        "config/fwids_controllers_ros2.yaml", controller_yaml)

    # ---- launch arguments ---------------------------------------------------
    use_gui = LaunchConfiguration("use_gui", default="true")
    use_rviz = LaunchConfiguration("use_rviz", default="false")
    world = LaunchConfiguration("world", default=os.path.join(
        pkg_share, "worlds", "empty.world"))

    # ---- Gazebo server (headless)--------------------------------------------
    gzserver = ExecuteProcess(
        cmd=["gzserver", "--verbose", "-s", "libgazebo_ros_factory.so",
             "-s", "libgazebo_ros_init.so", world],
        output="screen",
    )

    # ---- Gazebo client (GUI) -----------------------------------------------
    gzclient = ExecuteProcess(
        cmd=["gzclient", "--verbose"],
        output="screen",
        condition=IfCondition(use_gui),
    )

    # ---- robot_state_publisher ----------------------------------------------
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[{"robot_description": robot_description,
                     "use_sim_time": True}],
    )

    # ---- spawn robot in Gazebo ----------------------------------------------
    spawn_entity = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        name="spawn_fwids_vehicle",
        output="screen",
        arguments=["-topic", "robot_description",
                   "-entity", "fwids_vehicle",
                   "-x", "0.0", "-y", "0.0", "-z", "0.05"],
    )

    # ---- joint_state_broadcaster spawner ------------------------------------
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        name="joint_state_broadcaster_spawner",
        output="screen",
        arguments=["joint_state_broadcaster",
                   "--controller-manager", "/controller_manager"],
    )

    # ---- steering controller spawner ----------------------------------------
    steering_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        name="steering_controller_spawner",
        output="screen",
        arguments=["steering_controller",
                   "--controller-manager", "/controller_manager"],
    )

    # ---- wheel velocity controller spawner ----------------------------------
    wheel_velocity_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        name="wheel_velocity_controller_spawner",
        output="screen",
        arguments=["wheel_velocity_controller",
                   "--controller-manager", "/controller_manager"],
    )

    # ---- rviz2 --------------------------------------------------------------
    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        parameters=[{"use_sim_time": True}],
        condition=IfCondition(use_rviz),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_gui",
                default_value="true",
                description="Launch Gazebo client GUI",
            ),
            DeclareLaunchArgument(
                "use_rviz",
                default_value="false",
                description="Launch RViz2",
            ),
            DeclareLaunchArgument(
                "world",
                default_value=os.path.join(pkg_share, "worlds", "empty.world"),
                description="Path to the Gazebo world file",
            ),
            gzserver,
            gzclient,
            robot_state_publisher,
            spawn_entity,
            joint_state_broadcaster_spawner,
            steering_controller_spawner,
            wheel_velocity_controller_spawner,
            rviz,
        ]
    )
