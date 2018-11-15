# coding=utf-8

import base64

from Crypto import Random
from Crypto.Hash import SHA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Crypto.PublicKey import RSA


def create_pki(key_len=1024):
    """
    生成密钥对
    :param key_len: 密钥加密的长度
    :return:
    """
    # 伪随机数生成器 Random.new().read
    rsa = RSA.generate(key_len, Random.new().read)
    private = rsa.exportKey()
    public = rsa.publickey().exportKey()
    return {"private_pem": private, "public_pem": public}


# master ghost的秘钥对的生成
master_keys = create_pki()
ghost_keys = create_pki()
print master_keys


# 加密解密：公钥加密，私钥解密
# Master使用Ghost的公钥对内容进行rsa 加密

def encrypt_data(public_key, data):
    """
    使用公钥加密
    :param public_key:
    :param data:
    :return:
    """
    rsa_key = RSA.importKey(public_key)
    cipher = Cipher_pkcs1_v1_5.new(rsa_key)
    out_data = base64.b64encode(cipher.encrypt(data))
    return out_data


master_say = encrypt_data(ghost_keys["public_pem"], 'hello ghost, this is a plian text')


# Ghost使用自己的私钥对内容进行rsa 解密

def decrypt_data(private_key, data):
    """
    使用私钥解密
    :param private_key:
    :param data:
    :return:
    """
    rsa_key = RSA.importKey(private_key)
    cipher = Cipher_pkcs1_v1_5.new(rsa_key)
    out_data = cipher.decrypt(base64.b64decode(data), Random.new().read)
    return out_data


ghost_lin = decrypt_data(ghost_keys["private_pem"], master_say)
print ghost_lin


# 签名验签：私钥签名，公钥验签
# Master 使用自己的私钥对内容进行签名


def signature_data(private_key, data):
    """
    使用私钥签名
    :param private_key:
    :param data:
    :return:
    """
    rsa_key = RSA.importKey(private_key)
    signer = Signature_pkcs1_v1_5.new(rsa_key)
    digest = SHA.new()
    digest.update(data)
    sign = signer.sign(digest)
    return base64.b64encode(sign)


master_sign = signature_data(master_keys["private_pem"], master_say)


def is_verify(public_key, source, sign):
    """
    使用公钥验签
    :param public_key: 公钥
    :param source: 签名前数据
    :param sign: 签名后数据
    :return: bool
    """
    rsa_key = RSA.importKey(public_key)
    verifier = Signature_pkcs1_v1_5.new(rsa_key)
    digest = SHA.new()
    digest.update(source)
    return verifier.verify(digest, base64.b64decode(sign))


ghost_verify = is_verify(master_keys["public_pem"], master_say, master_sign)

print ghost_verify
