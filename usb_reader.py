import usb.core
import usb.util
import struct
import time
from threading import Thread, Event, Lock
from collections import deque
from config import QUEUE_MAXLEN, SAMPLE_RATE

class USBReader(Thread):
    """
    USB 设备读取器类，用于从指定的 USB 设备中读取数据。

    :param vendor_id: USB 设备的厂商 ID。
    """
    
    def __init__(self, vendor_id):
        """
        初始化 USBReader 类。

        :param vendor_id: USB 设备的厂商 ID。
        """
        super().__init__()
        self.vendor_id = vendor_id  # USB 设备的厂商 ID
        self.dev = None  # USB 设备实例
        self.in_endpoint = None  # 用于接收数据的 IN 端点
        self.byte_count = 0  # 统计读取的字节数
        self.start_time = time.time()  # 记录起始时间，用于计算数据传输速率
        self.data_queue = deque(maxlen=QUEUE_MAXLEN)  # 用于存储接收到的数据的队列，长度有限制
        self.data_lock = Lock()  # 锁，用于确保线程安全的访问数据队列
        self.stop_event = Event()  # 事件，用于指示线程是否应停止

        # 初始化 USB 设备并设置通信
        self.initialize_device()

    def initialize_device(self):
        """
        初始化并配置 USB 设备，查找并设置 IN 端点。
        
        :raises ValueError: 当未找到设备或 IN 端点时抛出异常。
        """
        self.dev = usb.core.find(idVendor=self.vendor_id)
        if self.dev is None:
            raise ValueError('未找到 USB 设备')

        self.dev.set_configuration()
        cfg = self.dev.get_active_configuration()
        interface = cfg[(0, 0)]
        self.in_endpoint = usb.util.find_descriptor(
            interface,
            custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
        )
        if self.in_endpoint is None:
            raise ValueError('未找到 IN 端点')

    def run(self):
        """
        线程的主运行函数，持续从 USB 设备中读取数据并存储在数据队列中。
        
        :raises usb.core.USBError: 在 USB 通信发生错误时抛出异常。
        """
        while not self.stop_event.is_set():
            try:
                data = self.dev.read(self.in_endpoint.bEndpointAddress, self.in_endpoint.wMaxPacketSize, timeout=1000)
                self.byte_count += len(data)
                with self.data_lock:
                    for i in range(0, len(data), 4):
                        if i + 4 <= len(data):
                            float_val = struct.unpack('<f', data[i:i+4])[0]
                            self.data_queue.append(float_val)
            except usb.core.USBError as e:
                if e.errno == 110:  # 超时错误
                    pass  # 忽略超时错误，继续读取
                else:
                    raise e

    def stop(self):
        """
        停止 USBReader 线程的运行。
        """
        self.stop_event.set()

    def get_speed(self):
        """
        计算数据传输速率。

        :return: 数据传输速率，单位为 KB/s。
        """
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 0:
            return self.byte_count / elapsed_time / 1024  # 速率以 KB/s 为单位
        return 0

    def get_data(self):
        """
        获取当前存储在数据队列中的数据。

        :return: 包含浮点数的列表，表示接收到的数据。
        """
        with self.data_lock:
            return list(self.data_queue)

    def get_device_info(self):
        """
        获取 USB 设备的详细信息。

        :return: 包含设备信息的字典。
        """
        return {
            "vendor_id": f"0x{self.vendor_id:04x}",  # 厂商 ID，十六进制表示
            "product_id": f"0x{self.dev.idProduct:04x}",  # 产品 ID，十六进制表示
            "manufacturer": self.dev.manufacturer,  # 制造商字符串
            "product": self.dev.product,  # 产品字符串
            "serial_number": self.dev.serial_number,  # 序列号字符串
            "endpoint_address": f"0x{self.in_endpoint.bEndpointAddress:02x}",  # IN 端点地址，十六进制表示
            "max_packet_size": f"{self.in_endpoint.wMaxPacketSize} bytes"  # 最大数据包大小，单位为字节
        }

    def __del__(self):
        """
        清理资源，在对象销毁时释放 USB 设备的资源。
        """
        if self.dev:
            usb.util.dispose_resources(self.dev)
