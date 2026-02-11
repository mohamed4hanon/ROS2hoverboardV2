import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import serial
import struct

class HoverboardDriver(Node):
    def __init__(self):
        super().__init__('mohamed_hover_driver')
        
        # إعدادات السيريال من كود الأردوينو
        self.port = '/dev/ttyUSB0'
        self.baud = 115200
        self.START_FRAME = 0xABCD # إطار البداية المعتمد
        
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=1)
            self.get_logger().info(f'✅ Connected to Hoverboard at {self.baud} baud')
        except Exception as e:
            self.get_logger().error(f'❌ Serial Error: {e}')
            exit()

        # الاشتراك في أوامر الحركة
        self.subscription = self.create_subscription(Twist, '/cmd_vel', self.listener_callback, 10)

    def listener_callback(self, msg):
        # تحويل سرعة ROS إلى قيم الهوفر بورد (بحد أقصى 300)
        speed = int(msg.linear.x * 300) 
        steer = int(msg.angular.z * 200)

        # حساب الـ Checksum بنفس معادلة الأردوينو: XOR
        checksum = self.START_FRAME ^ (steer & 0xFFFF) ^ (speed & 0xFFFF)
        
        # تعبئة البيانات في الهيكل الثنائي (Binary Struct)
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