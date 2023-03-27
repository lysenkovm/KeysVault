import pyAesCrypt as crypta
import getpass


def encrypt_file(src, tgt):
    password = getpass.getpass(prompt='Password: ', stream=None)
    crypta.encryptFile(src, tgt, password)


def decrypt_file(src, tgt):
    password = getpass.getpass(prompt='Password: ', stream=None)
    crypta.decryptFile(src, tgt, password)

