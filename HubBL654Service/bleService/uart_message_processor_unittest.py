import unittest
import uart_message_processor as hub_encoder
import os

class TestUartMsgProcessing(unittest.TestCase):
    def test_pub(self):
        orignal_cmd = "dev_addr/pgn/value"
        key = os.urandom(32)  # 256-bit key
        hub_encoder.set_key(key)
        ciphertext = hub_encoder.encrypt_data(bytes(orignal_cmd, 'utf-8'))
        #simulating ble write--------------------
        received_bytes = hub_encoder.decrypt_data(ciphertext)
        received_bytes_in_string = received_bytes.hex() #convert bytes to string for uart communication
        uart_message = "BL/PUB/" + received_bytes_in_string
        #simulating uart write--------------------
        result = uart_message.split("/", maxsplit=2)
        print(result[0])
        self.assertEqual(result[0], "BL")
        print(result[1])
        self.assertEqual(result[1], 'PUB')
        print(result[2])
        restored_cmd = bytes.fromhex(result[2]).decode("utf-8")
        print(restored_cmd)
        self.assertEqual(restored_cmd, orignal_cmd)
        

if __name__ == '__main__':
    unittest.main()
