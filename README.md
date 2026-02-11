hi

# change dir to your ROS2 directory

cd ~/ros2_ws/src


git clone https://github.com/mohamed4hanon/hoverboard_ros2.git
# chinge dir again
cd ~/ros2_ws

colcon build --packages-select mohamed_ros2

source install/setup.bash


ros2 run mohamed_ros2 hover_drive
