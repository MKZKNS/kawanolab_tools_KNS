import numpy as np
import serial
import time
import ntplib
import datetime

class e8257d:

    def __init__(self):
        # シリアル通信を確立する
        self.ser = serial.Serial('COM9',
                                 baudrate=57600,
                                 bytesize=8,
                                 stopbits=1,
                                 rtscts=True,
                                 timeout=1,
                                 parity='N')
    
    def send(self, text, echo=False):
        # シリアルで文字列を送信するコマンド
        # LFをtextに付与
        text = text + '\n'
        self.ser.write(text.encode('utf-8'))
        ret_text = self.ser.read(50)
        if echo:
            print(ret_text.decode('utf-8'), end="")
    
    def receive(self, size=50):
        # 受信するプログラム
        ret_text = self.ser.read(size)
        print(ret_text.decode('utf-8'), end="")
        return ret_text.decode('utf-8')

    def phase_reference_set(self, echo=False):
        # 位相を基準信号源とシンクロさせるコマンド？
        self.send(':PHASE:REFERENCE', echo)

    def rf_on(self, freq, power, phase, output=True, echo=False):
        # RFを出力するコマンド
        self.send(f':FREQ {freq}GHZ', echo)
        self.send(f':POWER {power}DBM', echo)
        self.send(f':PHASE {phase}DEG', echo)
        # RFを出力するか分岐
        if output:
            self.send(":OUTPUT ON", echo)
        
    def rf_off(self, echo=False):
        # RF出力を切る
        self.send(':OUTPUT OFF', echo)


    def set_time(self, ntp_server="ntp.nict.jp"):
        """
        指定されたNTPサーバーから時刻を取得し、GHz波源に時刻を設定する。

        :param ntp_server: 接続するNTPサーバーのアドレス
        """
        try:
            # 1. NTPサーバーから時刻を取得
            client = ntplib.NTPClient()
            response = client.request(ntp_server, timeout=5)
            
            # response.tx_time は Unix時間 (UTC) です。
            unix_time = response.tx_time
            
            dt_object = datetime.datetime.fromtimestamp(unix_time)
            
            # 3. 必要な情報を抽出
            year = dt_object.year
            month = dt_object.month
            day = dt_object.day
            hour = dt_object.hour
            minute = dt_object.minute
            second = dt_object.second
            
            # 時刻を送信
            print("date setting")
            self.send(f':SYSTEM:DATE {year}, {month}, {day}')
            self.send(f':SYSTEM:DATE?')
            self.receive()
            self.send(f':SYSTEM:TIME {hour}, {minute}, {second}')
            self.send(f':SYSTEM:TIME?')
            self.receive()

            
        except ntplib.NTPException as e:
            print(f"エラー: NTPサーバー {ntp_server} との通信に失敗しました。")
            print(f"詳細: {e}")
        except Exception as e:
            print(f"予期せぬエラーが発生しました: {e}")

    def terminate(self):
        # シリアルポートのロックを終わらせる
        self.ser.close()
        return()

if __name__ == '__main__':
    ghz = e8257d()

    freq = 10   # GHz
    phase = 0   # degree
    power = -20 #dBm

    ghz.set_time()

    ghz.rf_on(freq, power, phase, output=True, echo=True)
    time.sleep(1)
    ghz.rf_off(echo=True)