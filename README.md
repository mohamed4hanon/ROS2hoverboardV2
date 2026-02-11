# ROS2hoverboardV2
this file to creat hover borad controlling  via ROS2
# HoverBoard firmware 
you should upload a suitable firmware 

# ROS2 Path 

. الهيكل الشجري للمجلدات (Final Structure)
تأكد أن الملفات موزعة في المسار التالي داخل ros2_ws:

ros2_ws/

src/

mohamed_ros2/ (هذا هو مجلد الحزمة الذي سنقوم ببنائه)


package.xml 
+1


setup.py 
+1

resource/ (مجلد يحتوي على ملف فارغ باسم الحزمة)

mohamed_ros2

mohamed_ros2/ (المجلد البرمجي الداخلي)

__init__.py (ملف فارغ)


driver_node.py (كود البايثون الذي أعددناه) 
+1

# الانتقال لمجلد السورس
cd ~/ros2_ws/src

# إنشاء المجلدات الجديدة
mkdir -p mohamed_ros2/mohamed_ros2
mkdir -p mohamed_ros2/resource

# إنشاء الملفات الفارغة الضرورية لـ ROS2
touch mohamed_ros2/mohamed_ros2/__init__.py
touch mohamed_ros2/resource/mohamed_ros2

1. ملف الكود الرئيسي: driver_node.py
المكان: ~/ros2_ws/src/mohamed_ros2/mohamed_ros2/driver_node.py

Python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import serial
import struct

class HoverboardDriver(Node):
    def __init__(self):
        super().__init__('mohamed_hover_driver')
        
        # إعدادات السيريال من كود الأردوينو [cite: 5]
        self.port = '/dev/ttyUSB0'
        self.baud = 115200
        self.START_FRAME = 0xABCD # إطار البداية المعتمد [cite: 5, 13]
        
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=1)
            self.get_logger().info(f'✅ Connected to Hoverboard at {self.baud} baud')
        except Exception as e:
            self.get_logger().error(f'❌ Serial Error: {e}')
            exit()

        # الاشتراك في أوامر الحركة
        self.subscription = self.create_subscription(Twist, '/cmd_vel', self.listener_callback, 10)

    def listener_callback(self, msg):
        # تحويل سرعة ROS إلى قيم الهوفر بورد (بحد أقصى 300) [cite: 6]
        speed = int(msg.linear.x * 300) 
        steer = int(msg.angular.z * 200)

        # حساب الـ Checksum بنفس معادلة الأردوينو: XOR [cite: 14]
        checksum = self.START_FRAME ^ (steer & 0xFFFF) ^ (speed & 0xFFFF)
        
        # تعبئة البيانات في الهيكل الثنائي (Binary Struct) [cite: 9, 10, 15]
        # H=uint16, h=int16
        payload = struct.pack('<HhhH', self.START_FRAME, steer, speed, checksum)
        
        try:
            self.ser.write(payload)
        except Exception as e:
            self.get_logger().error(f'Send Error: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = HoverboardDriver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
2. ملف الإعداد: setup.py
المكان: ~/ros2_ws/src/mohamed_ros2/setup.py

Python
from setuptools import setup
import os
from glob import glob

package_name = 'mohamed_ros2'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'pyserial'],
    zip_safe=True,
    maintainer='mohamed',
    description='ROS2 Driver for Hoverboard',
    license='MIT',
    entry_points={
        'console_scripts': [
            'hover_drive = mohamed_ros2.driver_node:main'
        ],
    },
)
3. ملف التعريف: package.xml
المكان: ~/ros2_ws/src/mohamed_ros2/package.xml

XML
<?xml version="1.0"?>
<package format3>
  <name>mohamed_ros2</name>
  <version>1.0.0</version>
  <description>Hoverboard Serial Package</description>
  <maintainer email="mohamed@todo.todo">mohamed</maintainer>
  <license>MIT</license>

  <depend>rclpy</depend>
  <depend>geometry_msgs</depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
الخطوات النهائية للتنفيذ:
تأكد من وجود الملف الفارغ: يجب أن يكون هناك ملف باسم mohamed_ros2 داخل مجلد resource.

البناء (Build):

Bash
cd ~/ros2_ws
colcon build --packages-select mohamed_ros2
source install/setup.bash
التشغيل:

Bash
ros2 run mohamed_ros2 hover_drive

