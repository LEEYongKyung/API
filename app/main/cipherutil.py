import base64
from Crypto.Cipher import AES
from Crypto.Util.number import bytes_to_long
from Crypto.Util import Counter

ENCRYPTION_KEY_DEFAULT = b"#BS!_!ICRAFT21#2"
ENCRYPTION_KEY_DEFAULT_IV = b"#bsafer!icraft21"

ENCRYPTION_KEY_ANDROID = b"icrftAndAAAA0001"
ENCRYPTION_KEY_IOS = b"icrftIosBBBB0001"
ENCRYPTION_KEY_IV = b"brandsaferCOM001"

ENCRYPTION_KEY_SQR_ANDROID = b"icrftAndSQRR0001"
ENCRYPTION_KEY_SQR_IOS = b"icrftIosSQRR0001"
ENCRYPTION_KEY_SQR_WEB = b"icrftWEBSQRR0001"
ENCRYPTION_KEY_SQR_IV = b"brandsaferSQR001"

BLOCK_SIZE = 16  # Bytes
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

class CipherAgent:
    __BLOCK_SIZE_16 = BLOCK_SIZE_16 = AES.block_size

    def __init__(self, key = ENCRYPTION_KEY_DEFAULT, iv = ENCRYPTION_KEY_DEFAULT_IV):
         self.key = key       
         self.iv = iv  

    def encryptAndEncodingBase64(self, raw):
        plain = pad(raw)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        temp_data = cipher.encrypt(plain.encode('utf-8'))
        data = (base64.b64encode(temp_data)).decode('utf-8')
        return data

    def decodingBase64AndDecrypt(self, enc):
        plain = base64.b64decode(enc)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        temp_data = cipher.decrypt(plain)
        data = (unpad(temp_data)).decode('utf-8')
        return data

    def encrypt(self, raw):
        plain = pad(raw)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        data = cipher.encrypt(plain.encode('utf-8'))
        return data

    def decrypt(self, enc):
        plain = enc
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        temp_data = cipher.decrypt(plain)
        data = (unpad(temp_data)).decode('utf-8')
        return data

    def encryptNoPadding(self, raw):
        plain = raw
        counter = Counter.new(128, initial_value = bytes_to_long(self.iv))
        cipher = AES.new(self.key, AES.MODE_CTR, counter = counter)
        data = cipher.encrypt(plain.encode('utf-8'))
        return data

    def decryptNoPadding(self, enc):
        plain = enc
        counter = Counter.new(128, initial_value = bytes_to_long(self.iv))
        cipher = AES.new(self.key, AES.MODE_CTR, counter = counter)
        temp_data = cipher.decrypt(plain)
        data = temp_data.decode('utf-8')
        return data
