#!/usr/bin/env python3
"""
This is the class to encrypt/decrypt data file
"""

__author__ = "Charlie Lin"
__copyright__ = "Copyright 2024, Navico Group"
__credits__ = ["Bruce Wiatrak", "Chia-Hua Lin"]
__date__ = "1/23/2025"
__deprecated__ = False
__email__ = "charlie.lin@navicogroup.com"
__license__ = ""
__maintainer__ = "Chia-Hua(Charlie) Lin"
__status__ = "Development"
__version__ = "0.0.1"

import json
import logging
import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

logger = logging.getLogger(__name__)
logHandler = logging.StreamHandler(stream=sys.stdout)
logHandler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.DEBUG)

BLE_SECRET_AUTH_KEY_PATH = "/data/ble_secret_auth_key.json"
HEADER = bytearray([0x01, 0x02, 0x09])
key: str
raw_key: bytes
key_loaded = False

def read_secret_key_from_file():
    try:
        with open(BLE_SECRET_AUTH_KEY_PATH, "r") as f:
            json_data = json.load(f)
        return json_data['secret_key']
    except json.JSONDecodeError as e:
        logger.error("Failed to parse auth token: " + str(e))
        return None
    except FileNotFoundError as e:
        logger.error("The auth token file does not exist: " + str(e))
        return None
    except IOError as e:
        logger.error("Failed to read auth token from file: " + str(e))
        return None
    
def get_key():
    return key

# This command is only for unittesting. The key should be loaded from a local file directly
def set_key(test_key):
    global key, raw_key, key_loaded
    raw_key = test_key
    key_loaded = True

def load_key():
    logger.info("loading key")
    global key, raw_key, key_loaded
    key = read_secret_key_from_file()
    if key != None:
        logger.info("key: " + key)
        try:
            raw_key = bytes.fromhex(key)
            key_loaded = True
        except:
            logger.info("key in wrong format!!")
            key_loaded = False

def encrypt_data(data):
    if key_loaded:
        logger.info("encrypting data: " + bytes(data).hex())
        # message is a byte array
        # Out-going payload: IV(128 bits) + Encrypted Data(header 3 bytes + raw data + padding)
        iv = os.urandom(16)
        logger.info("iv: " + bytes(iv).hex())
        ciphertext = encrypt(HEADER + data, raw_key, iv)
        logger.info("encrypted data: " + bytes(ciphertext).hex())
        return iv + ciphertext
    else:
        logger.warning("key not loaded!! Cancel encrypting")
        return None

def decrypt_data(data):
    if key_loaded:
        logger.info("decrypting data: " + bytes(data).hex())
        try:
            if len(data) <= 16:
                logger.error("data length less than 17 bytes. disconnecting...")
                #TODO ble.disconnect_device()
            else:
                iv = bytearray(data[0:16])
                encrypted_data = bytearray(data[16:])
                
                # Verify IV is 16 bytes
                if len(iv) != 16:
                    logger.error(f"Invalid IV length: {len(iv)} bytes, expected 16")
                    #TODO ble.disconnect_device()
                    return None
                    
                decrypted_data = decrypt(encrypted_data, raw_key, iv)
                if len(decrypted_data) <= 3 or decrypted_data[:3] != HEADER:
                    logger.error("header does not match. disconnecting...")
                    #TODO ble.disconnect_device()
                else:
                    return decrypted_data[3:]
        except Exception as e:
            logger.error("Failed to decrypt data: " + str(e))
    else:
        logger.warning("key not loaded!! Cancel decrypting")
        return None

def encrypt(message, secret_key, iv):
    cipher = Cipher(algorithms.AES(secret_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
        # Pad the data if necessary
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(message) + padder.finalize()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return ciphertext

def decrypt(ciphertext, secret_key, iv):
    cipher = Cipher(algorithms.AES(secret_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
    # Unpad the data
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(decrypted_data) + unpadder.finalize()
    return plaintext

logger.info("Starting encryptionhelper")
