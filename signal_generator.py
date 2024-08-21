import math
import random
import time
from threading import Thread, Event, Lock
from collections import deque
from config import QUEUE_MAXLEN, SAMPLE_RATE

class SimulatedSignalGenerator(Thread):
    """
    模拟信号生成器类，用于生成带有噪声的正弦波信号。

    :param frequency: 信号的频率，默认为 10000 Hz。
    :param noise_level: 噪声的水平，默认为 0.1。
    """
    
    def __init__(self, frequency=10000, noise_level=0.1):
        """
        初始化 SimulatedSignalGenerator 类。

        :param frequency: 信号的频率，默认为 10000 Hz。
        :param noise_level: 噪声的水平，默认为 0.1。
        """
        super().__init__()
        self.frequency = frequency  # 信号的频率
        self.sample_rate = SAMPLE_RATE  # 采样率
        self.noise_level = noise_level  # 噪声水平
        self.t = 0  # 初始化时间步
        self.byte_count = 0  # 已生成的字节数
        self.start_time = time.time()  # 起始时间
        self.data_queue = deque(maxlen=QUEUE_MAXLEN)  # 数据队列，有限长度
        self.data_lock = Lock()  # 数据队列的锁
        self.stop_event = Event()  # 停止事件

    def generate_sample(self):
        """
        生成一个模拟的信号样本，包括正弦波和噪声。

        :return: 带有噪声的信号值。
        """
        value = math.sin(2 * math.pi * self.frequency * self.t / self.sample_rate)
        noise = random.uniform(-self.noise_level, self.noise_level)
        self.t += 1
        return value + noise

    def run(self):
        """
        线程的主运行函数，持续生成信号样本并存储在数据队列中。
        """
        while not self.stop_event.is_set():
            data = [self.generate_sample() for _ in range(100)]
            self.byte_count += len(data) * 4  # 假设每个浮点数占 4 个字节
            with self.data_lock:
                self.data_queue.extend(data)
            time.sleep(0.01)  # 模拟数据生成的延迟

    def stop(self):
        """
        停止信号生成器的运行。
        """
        self.stop_event.set()

    def get_speed(self):
        """
        计算数据生成的速度。

        :return: 数据生成的速度，单位为 KB/s。
        """
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 0:
            return self.byte_count / elapsed_time / 1024  # 返回速率，单位为 KB/s
        return 0

    def get_data(self):
        """
        获取当前存储在数据队列中的信号数据。

        :return: 信号数据的列表。
        """
        with self.data_lock:
            return list(self.data_queue)

    def get_device_info(self):
        """
        获取模拟设备的信息。

        :return: 包含设备信息的字典。
        """
        return {
            "vendor_id": "N/A",  # 厂商 ID 不适用
            "product_id": "N/A",  # 产品 ID 不适用
            "manufacturer": "Simulated Signal",  # 厂商名称为 "Simulated Signal"
            "product": "Simulated Signal Generator",  # 产品名称为 "Simulated Signal Generator"
            "serial_number": "N/A",  # 序列号不适用
            "endpoint_address": "N/A",  # 端点地址不适用
            "max_packet_size": "N/A"  # 最大数据包大小不适用
        }
