import numpy as np
import time
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from config import X_AXIS_RANGE, Y_AXIS_RANGE, SAMPLE_RATE

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.x_range = X_AXIS_RANGE
        self.fig = Figure(figsize=(8, 10), dpi=100)
        self.axes = self.fig.subplots(2, 1)
        super(PlotCanvas, self).__init__(self.fig)
        self.setParent(parent)

        # Configured sampling rate
        self.configured_sample_rate = SAMPLE_RATE

        # Variables for sampling rate estimation
        self.last_update_time = time.time()
        self.data_count = 0
        self.estimated_sample_rate = None
        self.receive_speed = None

        self.init_time_domain_plot()
        self.init_frequency_domain_plot()

        # Create a text object for metrics above the time domain plot, aligned to the left
        self.metrics_text = self.fig.text(0.01, 0.98, '', horizontalalignment='left', verticalalignment='top')

        self.fig.tight_layout(rect=[0, 0.03, 1, 0.97])  # Adjust layout to make room for metrics text

    def init_time_domain_plot(self):
        self.axes[0].set_title('Time Domain Signal')
        self.axes[0].set_xlim(0, self.x_range)
        self.axes[0].set_ylim(Y_AXIS_RANGE)
        self.axes[0].set_xlabel('Sample')
        self.axes[0].set_ylabel('Amplitude')
        self.xdata = np.linspace(0, self.x_range, self.x_range)
        self.time_line, = self.axes[0].plot(self.xdata, np.zeros(self.x_range), 'r-')

    def init_frequency_domain_plot(self):
        self.axes[1].set_title('Frequency Domain Spectrum')
        self.freq_line, = self.axes[1].plot([], [])
        self.axes[1].set_xlim(0, self.configured_sample_rate / 2)
        self.axes[1].set_ylim(0, 100)
        self.axes[1].set_xlabel('Frequency (Hz)')
        self.axes[1].set_ylabel('Magnitude')
        self.max_freq_text = self.axes[1].text(0.02, 0.95, '', transform=self.axes[1].transAxes)

    def update_plot(self, data, speed):
        self.receive_speed = speed
        self.estimate_sample_rate(len(data))
        self.update_time_domain(data)
        self.update_frequency_domain(data)
        self.update_metrics_text()
        self.draw()

    def estimate_sample_rate(self, new_data_count):
        current_time = time.time()
        time_diff = current_time - self.last_update_time
        
        if time_diff > 0:
            self.data_count += new_data_count
            if time_diff >= 1.0:  # Update estimate every second
                self.estimated_sample_rate = self.data_count / time_diff
                self.data_count = 0
                self.last_update_time = current_time

    def update_metrics_text(self):
        receive_speed_str = f'{self.receive_speed:.2f}' if self.receive_speed is not None else 'N/A'
        estimated_rate_str = f'{self.estimated_sample_rate:.2f}' if self.estimated_sample_rate is not None else 'N/A'
        
        metrics_str = (
            f'Receive Speed: {receive_speed_str} KB/s   '
            f'Configured Rate: {self.configured_sample_rate:.2f} Hz   '
            f'Estimated Rate: {estimated_rate_str} Hz'
        )
        self.metrics_text.set_text(metrics_str)

    def update_time_domain(self, data):
        ydata = np.zeros(self.x_range)
        if len(data) >= self.x_range:
            ydata[:] = data[-self.x_range:]
        else:
            ydata[-len(data):] = data
        self.time_line.set_ydata(ydata)

    def update_frequency_domain(self, data):
        if len(data) > 0:
            fft_result = np.fft.fft(data)
            fft_freq = np.fft.fftfreq(len(data), d=1/self.configured_sample_rate)
            fft_mag = np.abs(fft_result)

            positive_freq_idxs = fft_freq > 0
            positive_fft_freq = fft_freq[positive_freq_idxs]
            positive_fft_mag = fft_mag[positive_freq_idxs]

            max_idx = np.argmax(positive_fft_mag)
            max_freq = positive_fft_freq[max_idx]
            max_mag = positive_fft_mag[max_idx]

            self.max_freq_text.set_text(f'Max Frequency: {max_freq:.2f} Hz, Mag: {max_mag:.2f}')

            self.freq_line.set_data(positive_fft_freq, positive_fft_mag)
            self.axes[1].set_ylim(0, max_mag * 1.1)
            self.axes[1].relim()
            self.axes[1].autoscale_view()

    def set_x_axis_range(self, x_range):
        self.x_range = x_range
        self.axes[0].set_xlim(0, x_range)
        self.xdata = np.linspace(0, x_range, x_range)
        self.time_line.set_xdata(self.xdata)
        self.time_line.set_ydata(np.zeros(x_range))

    def set_y_axis_range(self, y_min, y_max):
        self.axes[0].set_ylim(y_min, y_max)