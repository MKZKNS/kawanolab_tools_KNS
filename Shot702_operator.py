import serial
import numpy as np
import time

# 円を描く
A = 500
f = 1
sec = 3.0
sf = 360

class shot702:

    def __init__(self):
        # シリアル通信を確立する
        self.ser = serial.Serial('COM3', baudrate=38400, bytesize=8, stopbits=1, rtscts=True, timeout=1, parity='N')

    def abs_mov(self, axis, direction):
        # 絶対移動の関数
        # axisは1か2かWを代入する（軸の指定）
        # directionは行き先を代入する。負の数もOK
        # しかし、directionは整数が望ましい
        # 正常終了すれば、0を返し、異常終了をすれば-1を返す。
        axis = str(axis) # axisを文字列にする
        if (axis != '1') and (axis != '2') and (axis != 'W'):
            # axisに意図せぬ値を入れたとき用の分岐
            # print('shot702.abs_mov error: 変数axisに入れた値が不正です。')
            return(-1)
        else: 
            if direction < 0:
                # directionが負の数のとき
                pol = '-'
            else:
                # directionが正の数のとき
                pol = '+'
            movement = str(abs(int(direction))) # 移動量を文字列にする（SHOT702には整数しか入れられない）
            comm_abs_mov = 'A:' + axis + pol + 'P' + movement + '\r\n'
            # print(comm_abs_mov)
            self.ser.write(comm_abs_mov.encode('utf-8'))
            shot_status = self.ser.read(10)
            # print('return: ' + shot_status.decode('utf-8'))
            comm_exe = 'G:' + '\r\n'
            # print(comm_exe)
            self.ser.write(comm_exe.encode('utf-8'))
            shot_status = self.ser.read(10)
            # print('return: ' + shot_status.decode('utf-8'))
            # ビジー状態かどうか取得する
            # ビジーの間、ループを抜け出せないようにする
            if_busy = '!:\r\n' # ビジーか問い合わせるコマンド
            self.ser.write(if_busy.encode('utf-8'))
            if_busy_ret = self.ser.read(10)
            # print('if_busy_ret: ' + if_busy_ret.decode('utf-8'))
            while(if_busy_ret.decode('utf-8') == 'B\r\n'):
                if_busy = '!:\r\n'
                self.ser.write(if_busy.encode('utf-8'))
                if_busy_ret = self.ser.read(10)
                # print('if_busy_ret in while: ' + if_busy_ret.decode('utf-8'))
            return(0)
        
    def abs_mov_xy(self, x_pos, y_pos):
        # 絶対座標をx_posとy_posに入力すると二つ軸が同時に動く
        # まだ動作しないので注意
        x_movement = str(abs(int(x_pos))) # 移動量を文字列にする（SHOT702には整数しか入れられない）
        y_movement = str(abs(int(y_pos)))
        # 軸番号とXY軸を関連付け
        xaxis = '1'
        yaxis = '2'
        # x軸情報を記述
        if x_pos < 0:
                # directionが負の数のとき
                x_pol = '-'
        else:
            # directionが正の数のとき
            x_pol = '+'
        shot_status = self.ser.read(10)
        # print('return: ' + shot_status.decode('utf-8'))

        # y軸情報を記述
        if y_pos < 0:
            # directionが負の数のとき
            y_pol = '-'
        else:
            # directionが正の数のとき
            y_pol = '+'
        comm_abs_mov_xy = 'A:' + 'W' + x_pol + 'P' + x_movement + y_pol + 'P' + y_movement + '\r\n'
        # print(comm_abs_mov_xy)
        self.ser.write(comm_abs_mov_xy.encode('utf-8'))
        shot_status = self.ser.read(10)
        # print('return: ' + shot_status.decode('utf-8'))

        # 実行
        comm_exe = 'G:' + '\r\n'
        # print(comm_exe)
        self.ser.write(comm_exe.encode('utf-8'))
        shot_status = self.ser.read(10)
        # print('return: ' + shot_status.decode('utf-8'))
        # ビジー状態かどうか取得する
        # ビジーの間、ループを抜け出せないようにする
        if_busy = '!:\r\n' # ビジーか問い合わせるコマンド
        self.ser.write(if_busy.encode('utf-8'))
        if_busy_ret = self.ser.read(10)
        # print('if_busy_ret: ' + if_busy_ret.decode('utf-8'))
        while(if_busy_ret.decode('utf-8') == 'B\r\n'):
            if_busy = '!:\r\n'
            self.ser.write(if_busy.encode('utf-8'))
            if_busy_ret = self.ser.read(10)
            # print('if_busy_ret in while: ' + if_busy_ret.decode('utf-8'))
        return(0)
    
    def abs_angle(self, axis, degree):
        # 角度移動をするときの関数
        self.abs_mov(axis=axis, direction=degree*1000)
        return()

        
    def rel_mov(self, axis, direction):
        # 相対移動の関数
        # axisは1か2かWを代入する（軸の指定）
        # directionは行き先を代入する。負の数もOK
        # しかし、directionは整数が望ましい
        # 正常終了すれば、0を返し、異常終了をすれば-1を返す。
        axis = str(axis) # axisを文字列にする
        if (axis != '1') and (axis != '2') and (axis != 'W'):
            # axisに意図せぬ値を入れたとき用の分岐
            # print('shot702.abs_mov error: 変数axisに入れた値が不正です。')
            return(-1)
        else: 
            if direction < 0:
                # directionが負の数のとき
                pol = '-'
            else:
                # directionが正の数のとき
                pol = '+'
            movement = str(abs(int(direction))) # 移動量を文字列にする（SHOT702には整数しか入れられない）
            comm_abs_mov = 'M:' + axis + pol + 'P' + movement + '\r\n'
            # print(comm_abs_mov)
            self.ser.write(comm_abs_mov.encode('utf-8'))
            shot_status = self.ser.read(10)
            # print('return: ' + shot_status.decode('utf-8'))
            comm_exe = 'G:' + '\r\n'
            # print(comm_exe)
            self.ser.write(comm_exe.encode('utf-8'))
            shot_status = self.ser.read(10)
            # print('return: ' + shot_status.decode('utf-8'))
            # ビジー状態かどうか取得する
            # ビジーの間、ループを抜け出せないようにする
            if_busy = '!:\r\n' # ビジーか問い合わせるコマンド
            self.ser.write(if_busy.encode('utf-8'))
            if_busy_ret = self.ser.read(10)
            # # print('if_busy_ret: ' + if_busy_ret.decode('utf-8'))
            while(if_busy_ret.decode('utf-8') == 'B\r\n'):
                if_busy = '!:\r\n'
                self.ser.write(if_busy.encode('utf-8'))
                if_busy_ret = self.ser.read(10)
                # # print('if_busy_ret in while: ' + if_busy_ret.decode('utf-8'))
            return(0)
        
    def m_org(self, axis):
        # 機械原点に戻る関数
        # 軸の指定ができる
        axis = str(axis) # axisを文字列にする
        if (axis != '1') and (axis != '2') and (axis != 'W'):
            # axisに意図せぬ値を入れたとき用の分岐
            # print('shot702.M_org error: 変数axisに入れた値が不正です。')
            return(-1)
        else: 
            comm_norstop = 'H:' + axis + '\r\n'
            self.ser.write(comm_norstop.encode('utf-8'))
            shot_status = self.ser.read(10)
            # print('return: ' + shot_status.decode('utf-8'))
            # ビジー状態かどうか取得する
            # ビジーの間、ループを抜け出せないようにする
            if_busy = '!:\r\n' # ビジーか問い合わせるコマンド
            self.ser.write(if_busy.encode('utf-8'))
            if_busy_ret = self.ser.read(10)
            # print('if_busy_ret: ' + if_busy_ret.decode('utf-8'))
            while(if_busy_ret.decode('utf-8') == 'B\r\n'):
                if_busy = '!:\r\n'
                self.ser.write(if_busy.encode('utf-8'))
                if_busy_ret = self.ser.read(10)
                # print('if_busy_ret in while: ' + if_busy_ret.decode('utf-8'))
            return(0)
    
    def normal_stop(self, axis):
        # 減速停止させる関数
        # 軸の指定ができる
        axis = str(axis) # axisを文字列にする
        if (axis != '1') and (axis != '2') and (axis != 'W'):
            # axisに意図せぬ値を入れたとき用の分岐
            # print('shot702.normal_stop error: 変数axisに入れた値が不正です。')
            return(-1)
        else: 
            comm_norstop = 'L:' + axis + '\r\n'
            self.ser.write(comm_norstop.encode('utf^8'))
            return(0)
        
    def stop(self):
        # 即停止させる関数
        comm_stop = 'L:E\r\n'
        self.ser.write(comm_stop.encode('utf-8'))
        return(0)
    
    def info(self, parameter, axis):
        # parameterは
        # V: バージョン情報 (なんかうまく反応しない（NGを返される）)
        # P: 1パルスあたりの移動量
        # S: 分割数
        # D: 移動速度
        # B: 原点復帰移動速度
        # A: 全情報を表示（本関数独自）
        # axisは軸指定（1 or 2 or W)
        axis = str(axis) # axisを文字列にする
        if (parameter != 'V') and (parameter != 'P') and (parameter != 'S') and (parameter != 'D') and (parameter != 'B') and (parameter != 'A'):
            # print('shot702.info error: 変数parameterに入れた値が不正です。')
            return(-1)
        else:
            if (axis != '1') and (axis != '2') and (axis != 'W'):
                # axisに意図せぬ値を入れたとき用の分岐
                # print('shot702.info error: 変数axisに入れた値が不正です。')
                return(-1)
            else:
                if (parameter != 'A'):
                    # 全情報表示以外のとき
                    info_comm = '?:' + parameter + axis + '\r\n'
                    self.ser.write(info_comm.encode('utf-8'))
                    # print(info_comm)
                    info_data = self.ser.read(10)
                    # print("SHOT702 said " + str(info_data.decode('utf-8')))
                    return(str(info_data.decode('utf-8')))
                else:
                    # 全情報表示のとき
                    # 情報取得parameterのリストを作成
                    parameter_list = ['V', 'P', 'S', 'D', 'B']
                    for curr_para in parameter_list:
                        info_comm = '?:' + curr_para + axis + '\r\n'
                        self.ser.write(info_comm.encode('utf-8'))
                        info_data = self.ser.read(10)
                        if curr_para == 'V':
                            desc = 'バージョン: '
                        elif curr_para == 'P':
                            desc = '1パルスあたりの移動量: '
                        elif curr_para == 'S':
                            desc = '分割数: '
                        elif curr_para == 'D':
                            desc = '移動量: '
                        elif curr_para == 'B':
                            desc = '原点復帰速度: '
                        # print(desc + str(info_data.decode('utf-8')))
                    return(1)
                
    def position(self):
        pos_comm = 'Q:\r\n'
        self.ser.write(pos_comm.encode('utf-8'))
        # print(pos_comm)
        pos_data = self.ser.read(100)
        # print("SHOT702 said " + str(pos_data.decode('utf-8')))
        return(str(pos_data.decode('utf-8')))
        
    def terminate(self):
        # シリアルポートのロックを終わらせる
        self.ser.close()
        return()


if __name__ == "__main__":
    # クラスshot702のインスタンスを生成
    shot = shot702()

    shot.m_org(axis='W')
    # # リファレンス用座標
    # x_ref_abs = 20658
    # y_ref_abs = -20282
    # # infomation = shot.info('S', 1)
    # #mov = shot.abs_mov(1, 2500)
    # #mov = shot.abs_mov(2, 0)
    # # mov = shot.rel_mov(1,100)
    # # 絶対座標による移動
    # mov = shot.abs_mov_xy(-11920, 8700)
    # # ref_mov = shot.abs_mov_xy(x_ref_abs, y_ref_abs)
    # # 現在位置取得
    # position_return = shot.position()
    shot.abs_angle(axis='1', degree=45)
    # print('Current Position is', position_return)
    # for i in range(1):
    #     mov = shot.rel_mov(1, 20)
    # mov = shot.rel_mov(1, 20)
    # mov = shot.abs_mov(2, 27267)

    # A = 20000    # 振幅
    # f = 1.0    # 周波数 Hz
    # sec = 3.0  # 信号の長さ s
    # sf = 40 # サンプリング周波数 Hz

    # t = np.arange(0, sec, 1/sf) #サンプリング点の生成

    # y1 = A*np.sin(2*np.pi*f*t) # 正弦波の生成
    # y2 = A*np.cos(2*np.pi*f*t)

    # for dir in range(y1.size):
    #     mov = shot.abs_mov(1, y1[dir])
    #     #   time.sleep(1)
    #     mov = shot.abs_mov(2, y2[dir])
    #     #   time.sleep(1)

    term = shot.terminate()