import serial
import time
import sys

# -------------------------------------------------------------------
# 設定項目
# -------------------------------------------------------------------
# お使いのPCのシリアルポート名に合わせて変更してください。
# Windowsの場合: 'COM1', 'COM3' など
# Linuxの場合: '/dev/ttyS0', '/dev/ttyUSB0' など
SERIAL_PORT = 'COM3'  # <<<<< 環境に合わせて変更してください

# -------------------------------------------------------------------

def main():
    """
    pyserialを使ってHP 34401AにRS-232Cで接続し、動作確認を行う。
    """
    ser = None  # finallyブロックで使うために先に定義
    try:
        print(f"シリアルポート ({SERIAL_PORT}) を開きます...")
        
        # --- シリアルポートを初期化し、指定された設定でオープン ---
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=9600,
            bytesize=serial.SEVENBITS,     # データビット: 7
            parity=serial.PARITY_EVEN,     # パリティ: 偶数
            stopbits=serial.STOPBITS_TWO,      # ストップビット: 2
            timeout=2.0,                   # 読み取りタイムアウト（秒）
            dsrdtr=True                    # フロー制御: DTR/DSR
        )

        print("ポートを開きました。計測器との通信を試みます...")
        
        # コマンドを送信
        # SCPIコマンドの最後には改行(LF)が必要
        # pyserialではバイト列で送受信するため、.encode()でエンコードする
        command = "*IDN?\n"
        ser.write(command.encode('ascii'))
        print(f"送信: {command.strip()}")
        
        # 少し待機（計測器が応答を返すための時間）
        time.sleep(0.2)
        
        # 計測器からの応答を受信
        # readline()は改行文字までを1行として読み取る
        # 受信データはバイト列なので、.decode()で文字列に変換する
        response_bytes = ser.readline()
        response = response_bytes.decode('ascii').strip()
        
        print("\n--- 応答結果 ---")
        if response:
            print(f"受信データ: {response}")
            print("--------------------\n")
            print("正常に通信が完了しました。")
        else:
            print("エラー: 計測器から応答がありませんでした。")
            print("タイムアウトしたか、接続に問題がある可能性があります。")

    except serial.SerialException as e:
        print(f"\nエラー: シリアルポートを開けませんでした。")
        print(f"詳細: {e}")
        print("\n--- 確認してください ---")
        print(f"1. ポート名 '{SERIAL_PORT}' は正しいですか？他のプログラムが使用していませんか？")
        print("2. ケーブルは正しく接続されていますか？（ヌルモデムケーブルが必要です）")
        print("3. 計測器の電源は入っていますか？")

    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
        
    finally:
        # プログラム終了時に必ずポートを閉じる
        if ser and ser.is_open:
            ser.close()
            print("シリアルポートを閉じました。")

if __name__ == '__main__':
    main()