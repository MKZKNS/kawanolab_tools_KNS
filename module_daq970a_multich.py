from time import time, sleep
import datetime
import numpy as np
import pyvisa
import keysight_ktdaq970
import matplotlib.pyplot as plt
import csv


def list_of_channels(str_chan: str):
    list_num = str_chan.split(":")
    if len(list_num) == 1:
        return [int(list_num[0]), ]
    if len(list_num) > 2:
        raise ValueError
    list_channel = []
    for _i in range(int(list_num[0]), int(list_num[1]) + 1):
        list_channel.append(_i)
    return list_channel


class Daq970a():
    """DAQ970A
    """
    device: keysight_ktdaq970.KtDAQ970 = None
    list_resources = []
    res_man = None
    time_scan = datetime.timedelta(1.0)
    max_range = 1000e-3
    # resolution = 0.1e-3
    resolution = 0.1e-6  # 20NPLC
    nplc = 20
    str_chan = "101"

    def __init__(self, debug=False, verbose=True) -> None:
        self.debug = debug
        if debug:
            return

        self.refresh_resources()
        self.connect_device(None, verbose)
        self.device.system.module.reset_all()
        # print(self.device.utility.error_query())
        self.device.scan.clear_scan_list()
        self.configure("101", 10, 5, 1000e-3, 0.1e-3)

    def refresh_resources(self):
        self.res_man = pyvisa.ResourceManager()
        self.list_resources = self.res_man.list_resources()

    def find_device(self, verbose=True):
        num_suggest = None
        for _i, _res in enumerate(self.list_resources):
            try:
                if "192.168.11." in _res:
                    # I have no idea that the ip address exists.
                    # 31325 is 192.168.10.xxx...
                    raise pyvisa.errors.VisaIOError(0)
                _dev = self.res_man.open_resource(_res)
                _return = _dev.query("*IDN?")
                _dev.close()
            except pyvisa.errors.VisaIOError:
                _return = ""
                if verbose:
                    print("DAQ970Wrapper>> " + _res + " : Could not connect")
            if "DAQ970A" in _return:
                num_suggest = _i
                # TODO priority: hislip > inst > gpib
                if verbose:
                    print("DAQ970Wrapper>> " + _res + " : DAQ970A Found")
                break
        if num_suggest is None:
            raise FileNotFoundError("DAQ970Wrapper>> DAQ970A is not found")
        return num_suggest

    def connect_device(self, num=None, verbose=True):
        if self.res_man is None:
            raise ValueError("DAQ970Wrapper>> ResourceManager is undefined")
        if self.list_resources is None:
            raise ValueError("DAQ970Wrapper>> Resource List is undefined")

        if num is None:
            num = self.find_device(verbose)

        resource_name = self.list_resources[num]
        id_query = True
        reset = True
        options = ""

        self.device = keysight_ktdaq970.KtDAQ970(resource_name, id_query, reset, options)

    def configure(self, str_channel=None, sweep_count=None, sec_scan=None, max_range=None, resolution=None, nplc=None):
        """configure
            max_range = 1000e-3
            resolution = 0.1e-3
            nplc = 20
            str_chan = "101"
            nplc: 0.02 | 0.2 | 1 | 2 | 10 | 20 | 100 | 200

            Integration Time Resolution	Digits Bits
            0.02 PLC	<0.0001 x Range	4 1/2 Digits	15
            0.2 PLC	<0.00001 x Range	5 1/2 Digits	18
            1 PLC (Default)	<0.000003 x Range	5 1/2 Digits	20
            2 PLC	<0.0000022 x Range	6 1/2 Digits	21
            10 PLC	<0.000001 x Range	6 1/2 Digits	24
            20 PLC	<0.0000008 x Range	6 1/2 Digits	25
            100 PLC	<0.0000003 x Range	6 1/2 Digits	26
            200 PLC	<0.00000022 x Range	6 1/2 Digits	26

            Sets the measurement range in volts (0.1 | 1 | 10 | 100 | 300)
            on the specified channelList or current scan list if parameter is empty.
        """
        if self.debug:
            return
        if str_channel is not None:
            self.str_chan = str_channel
        if max_range is not None:
            self.max_range = max_range
        if resolution is not None:
            self.resolution = resolution
        if nplc is not None:
            self.nplc = nplc
        # self.device.configure.dc_voltage.configure_auto(self.str_chan)
        self.device.configure.dc_voltage.configure(self.max_range, self.resolution, self.str_chan)
        self.device.configure.dc_voltage.set_nplc(self.nplc, self.str_chan)
        self.device.scan.format.enable_all()
        if sweep_count is not None:
            self.device.scan.sweep_count = sweep_count
        if sec_scan is not None:
            self.time_scan = datetime.timedelta(sec_scan)
        if nplc is not None:
            print("DAQ970Wrapper>> NPLC List>>", self.device.configure.dc_voltage.get_nplc(self.str_chan))

    def measure(self):
        """measure

            usage: mean, std = daq.measure()
        """
        if self.debug:
            return 0, 0
        _scan = self.device.scan.read(self.time_scan)
        list_channel_set = list_of_channels(self.str_chan)
        list_channel = [[] for _i in list_channel_set]
        for _mea in _scan:
            _idx = list_channel_set.index(_mea.channel)
            list_channel[_idx].append(_mea.reading)
        list_mean = []
        list_std = []
        for _list in list_channel:
            list_mean.append(np.mean(_list))
            list_std.append(np.std(_list))
        if len(list_mean) == 1:
            return list_mean[0], list_std[0]
        return list_mean, list_std

    def close(self):
        if self.device is not None:
            self.device.close()

    def __del__(self):
        self.close()


def oscillo(nmax=100, str_chan="101"):
    from matplotlib import pyplot as plt
    global flag_continue
    global flag_autoscale
    global flag_autoscale_0

    daq = Daq970a()
    daq.configure(str_chan, 1, 0.1, 1000e-3, 0.1e-3, 2)

    test = np.zeros(nmax)
    counts = - np.arange(nmax, 0, -1)
    # times = np.ones(nmax) * - 1e-3
    times = np.ones(nmax) * np.nan
    # times = np.zeros(nmax)

    fig, ax = plt.subplots(1, 1, tight_layout=True)
    lines, = ax.plot(counts, test)
    ax.set_ylabel(
        "Voltage [mV]\n(autoscale once: y, continuous: a or 0)\nAutoscale: Off")
    ax.set_xlabel("time [sec]")
    ax.grid(True)

    def pressed(event):
        global flag_continue
        global flag_autoscale
        global flag_autoscale_0
        if event.key == "y":
            flag_autoscale_0 = False
            flag_autoscale = False
            ax.set_ylim(
                test.min() - 0.1 * (test.max() - test.min()),
                test.max() + 0.1 * (test.max() - test.min()))
            ax.set_ylabel(
                "Voltage [mV]\n(autoscale once: y, continuous: a or 0)\nAutoscale: Off")
            return
        if event.key == "0":
            flag_autoscale_0 = True
            flag_autoscale = False
            ax.set_ylabel(
                "Voltage [mV]\n(autoscale once: y, continuous: a or 0)\nAutoscale: On (Zero)")
            return
        if event.key == "a":
            flag_autoscale_0 = False
            flag_autoscale = True
            ax.set_ylabel(
                "Voltage [mV]\n(autoscale once: y, continuous: a or 0)\nAutoscale: On")
            return
        if event.key == "q":
            flag_continue = False
            return

    fig.canvas.mpl_connect("key_press_event", pressed)
    start = time()
    flag_continue = True
    flag_autoscale = False
    flag_autoscale_0 = False
    while flag_continue:
        times[0:-1] = times[1:]
        times[-1] = time() - start
        test[0:-1] = test[1:]
        test[-1] = 1000 * daq.measure()[0]
        lines.set_data(times, test)
        if flag_autoscale:
            ax.set_ylim(
                test.min() - 0.1 * (test.max() - test.min()),
                test.max() + 0.1 * (test.max() - test.min()))
        if flag_autoscale_0:
            ax.set_ylim(
                0,
                test.max() * 1.1)
        ax.set_xlim(np.nanmin(times), np.nanmax(times[-1]))
        plt.pause(0.001)


if __name__ == "__main__":
    # ユーザー定義変数 ==========
    # シーケンス測定
    sequence = True
    # 測定回数
    times = 5
    # ==========

    """Basic Usage"""
    # daq = Daq970a()
    # daq.configure("101", 1, 0.1, 1000e-3, 0.1e-3, 2)
    # print(daq.measure())

    """App: Oscillo"""
    # oscillo()

    # 使用チャネル
    ch1 = '111'
    ch2 = '112'
    ch3 = '113'
    ch4 = '114'
    ch5 = '115'
    # チャンネル配列
    chs = []
    chs.append(ch1)
    chs.append(ch2)
    chs.append(ch3)
    chs.append(ch4)
    chs.append(ch5)
    # 手動計測
    daq = Daq970a()
    # セットアップ
    daq.configure(ch1, 1, 0.1, 1000e-3, 0.1e-3, 2)
    # 計測
    # シーケンス測定でないなら、単点測定
    if sequence == False:
        for _ in range(5):
            # 平均値のみ取り出し ([1]は標準偏差)
            _dcv = daq.measure()[0]
            print('current:', _dcv)
            input('Press ENTER Key to resume measurement:')

    # シーケンス測定
    if sequence == True:
        # 描画関係のセット
        fig, ax = plt.subplots(1, 1)
        # x軸のdata
        x_ax = chs
        x = x_ax
        y = [0,1,2,3,4]
        lines, = ax.plot(x, y)
        # 測定結果を保存する配列
        result = []
        # 指定回数だけ測定を行う
        for _ in range(times):
            # 測定結果を一時保存する配列を生成
            _dcv = []
            for _i in range(len(chs)):
                # DAQをch数だけ測定を繰り返す
                # セットアップ
                daq.configure(chs[_i], 1, 0.1, 1000e-3, 0.1e-3, 2)
                # 計測
                _dcv.append(daq.measure()[0])
            # 描画
            lines.set_data(x, _dcv)
            ax.set_ylim((min(_dcv), max(_dcv)))
            ax.set_ylabel('Voltage [V]')
            ax.set_xlabel('Channel Number')
            plt.pause(1)
            # データを保存
            result.append(_dcv)

        with open('sample_writer_row.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            for _i in range(len(result)):
                writer.writerow(result[_i])
        
        print('測定が終わりました')
        plt.show()