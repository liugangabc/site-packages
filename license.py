# coding=utf-8

import base64
import json

from Crypto import Random
from Crypto.Hash import SHA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Crypto.PublicKey import RSA


def create_pki(key_len=2048):
    """
    生成密钥对
    :param key_len: 密钥加密的长度
    :return:
    """
    # 伪随机数生成器 Random.new().read
    rsa = RSA.generate(key_len, Random.new().read)
    private = rsa.exportKey()
    public = rsa.publickey().exportKey()
    return {"private_key": private, "public_key": public}


# master ghost的秘钥对的生成
# master_keys = create_pki()
# ghost_keys = create_pki()
# print master_keys


# 加密解密：公钥加密，私钥解密
# Master使用Ghost的公钥对内容进行rsa 加密

def encrypt(public_key, data):
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


# master_say = encrypt(ghost_keys["public_pem"], 'hello ghost, this is a plian text')
# Ghost使用自己的私钥对内容进行rsa 解密

def decrypt(private_key, data):
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


# ghost_lin = decrypt(ghost_keys["private_pem"], master_say)


# 签名验签：私钥签名，公钥验签
# Master 使用自己的私钥对内容进行签名


def signature(private_key, data):
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


# master_sign = signature(master_keys["private_pem"], master_say)


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


# ghost_verify = is_verify(master_keys["public_pem"], master_say, master_sign)


def create_license(data, public_key, private_key):
    json_data = json.dumps(data)
    encrypt_data = encrypt(public_key, json_data)
    signature_data = signature(private_key, encrypt_data)
    out = {
        "data": encrypt_data,
        "license": signature_data
    }
    return base64.b64encode(json.dumps(out))


def verify_license(data, public_key, private_key):
    source = json.loads(base64.b64decode(data))
    license = source.pop("license")
    data = source.pop("data")
    if not is_verify(public_key, data, license):
        return "license verify failed!"
    info_data = decrypt(private_key, data)
    return info_data


__all__ = [
    "create_license",
    "verify_license"
]

if __name__ == "__main__":
    master_keys = create_pki()
    data = {
        "name": "Tim",
        "expires": "2020-03-01T23:59:59Z",
        "level": "super"
    }
    lic = create_license(data, **master_keys)
    verify_license(lic, **master_keys)
    print "ok"
