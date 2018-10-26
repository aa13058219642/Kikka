# coding=utf-8
import os
import sqlite3
import json
import logging

import binascii
import sys
import random
import base64

from sympy import nextprime
from struct import pack
from Crypto.Cipher import AES

import kikkahelper


class KikkaMemory:
    _instance = None
    isDebug = False

    def __init__(self, **kwargs):
        raise SyntaxError('KikkaMemory has only one, please use KikkaMemory.this()')

    @staticmethod
    def this():
        if KikkaMemory._instance is None:
            KikkaMemory._instance = object.__new__(KikkaMemory)
            KikkaMemory._instance._init()
        return KikkaMemory._instance

    def _init(self):
        pass

    def awake(self):
        self._filepath = 'Kikka.memory' if self.isDebug is False else 'Kikka.db'
        memoryEsists = os.path.exists(self._filepath)
        self._deepmemory = DeepMemory(sqlite3.connect(self._filepath))

        if not memoryEsists:
            logging.info("awake kikka memory")
            self._deepmemory.awake()
        logging.info("linked kikka memory")

    def read(self, key, default=''):
        return self._deepmemory.read(key, default, DeepMemory.TYPE_NORMAL)

    def readDeepMemory(self, key, default):
        return self._deepmemory.read(key, default, DeepMemory.TYPE_DEEP)

    def readInitialMemory(self, key, default):
        return self._deepmemory.read(key, default, DeepMemory.TYPE_INITIAL)

    def write(self, key, value):
        return self._deepmemory.write(key, value, DeepMemory.TYPE_NORMAL)

    def writeDeepMemory(self, key, value):
        return self._deepmemory.write(key, value, DeepMemory.TYPE_DEEP)

    def writeInitialMemory(self, key, value, _key):
        return self._deepmemory.write(key, value, DeepMemory.TYPE_INITIAL, _key)


class DeepMemory:
    TYPE_NORMAL = 0
    TYPE_DEEP = 1
    TYPE_INITIAL = 2

    def __init__(self, conn):
        self._name = 'Kikka'
        self._conn = conn
        self._cursor = conn.cursor()

        # Memory key ID
        self._key0 = 228671358270678769733151434401261
        self._key = 609416633504213051421056566850573
        self._dkey = nextprime(int(kikkahelper.getShortMD5(self._name)[:-2], 16))

    def __del__(self):
        self._cursor.close()
        self._conn.close()

    def awake(self):
        sql = 'create table if not exists T_DICT(__KEY__ text primary key not null, __TYPE__ integer, __VALUE__ text)'
        self._cursor.execute(sql)

        InitialMemory = '''
        ///6f0HWMetmDuhxXP7Mkklt06ofrDunx2B7g0pbD5tzkQUKMkRGMkNpTqKwld2WIcdm8kTS+UwVaI8h
        D/P1/aYPCqgBot06hFYatFXvGi294jcAaPWAXzgWsbrQuf5xOzWw+CkB5yZwsJkviunACws5sgGXwcDA
        IhlqChphfZH3EVJ6EKYa8GNe/VDofpzDL5i1/fwFDzomUXPdREWr+TSaznwZP6G86CvejhsckFQN2WiS
        86ZyBr1HQ6VSgzmMoNEgIs9Y2nlW73kZtxWrCQoCMep7L27Ip+XLTm6cwvU=
        '''
        js = json.loads(self.decrypt(InitialMemory, True))
        parameters = [(k, v[0], v[1]) for k, v in js.items()]
        sql = 'insert into T_DICT(__KEY__, __TYPE__, __VALUE__) values(?, ?, ?)'
        self._conn.executemany(sql, parameters)
        self._conn.commit()

    def read(self, key, default, readtype):
        try:
            value = default
            if readtype == self.TYPE_DEEP: key = "_%s_" % key
            elif readtype == self.TYPE_INITIAL: key = "__%s__" % key

            sql = 'select __VALUE__, __TYPE__ from T_DICT where __KEY__=?'
            sql_result = self._cursor.execute(sql, [key])
            f = sql_result.fetchall()
            if len(f) != 0:
                if readtype != f[0][1]:
                    logging.warning('read error: Permission denied')
                    return default
                if readtype == self.TYPE_DEEP: value = self.decrypt(f[0][0], False)
                elif readtype == self.TYPE_INITIAL: value = self.decrypt(f[0][0], True)
                else: value = f[0][0]
            else:
                return default

            if isinstance(default, str) is True: return str(value)
            elif isinstance(default, int) is True: return int(value)
            elif isinstance(default, float) is True: return float(value)
            elif isinstance(default, list) is True: return json.loads(value)
            elif isinstance(default, dict) is True: return json.loads(value)
            else: return default

        except ValueError:
            logging.warning('read memory fail: key[%s]' % key)
            return default

    def write(self, key, value, writetype, _key=''):
        try:
            value = str(value) if isinstance(value, (list, dict)) is False else json.dumps(value)
            if writetype == self.TYPE_NORMAL:
                pass
            elif writetype == self.TYPE_DEEP:
                value = self.encrypt(value)
                key = "_%s_" % key
            elif writetype == self.TYPE_INITIAL:
                value = self.encrypt(value, _key)
                key = "__%s__" % key
            else:
                return

            sql = 'select __VALUE__, __TYPE__ from T_DICT where __KEY__=?'
            sql_result = self._cursor.execute(sql, [key])
            f = sql_result.fetchall()
            if len(f) != 0:
                if writetype != f[0][1]:
                    logging.warning('Permission denied')
                    return
                if value == f[0][1]:
                    return

            sql = 'insert or replace into T_DICT(__KEY__, __TYPE__, __VALUE__) values(?, ?, ?)'
            self._cursor.execute(sql, [str(key), writetype, str(value)])
            self._conn.commit()
        except Exception:
            logging.warning('write memory fail: key[%s]' % key)
        pass

    def encrypt(self, message, key=''):
        e = self._dkey if key == '' else nextprime(int(kikkahelper.getShortMD5(key)[:-2], 16))
        n = self._key if key == '' else self._key0

        kl = self._byte_size(n)
        k = random.randint(n//2, n)
        encrypted = pow(k, e, n)
        encrypted_msg1 = self._int2bytes((~encrypted) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF, kl)

        m = str(k)
        ak = m[:8*min(max(len(m)//8, 2), 4)].encode()
        msg = self._pad(message, AES.block_size).encode()
        aes = AES.new(ak, AES.MODE_CBC, encrypted_msg1[:AES.block_size])
        encrypted_msg2 = aes.encrypt(msg)
        b_msg = base64.b64encode(encrypted_msg1 + encrypted_msg2).decode()
        return b_msg

    def decrypt(self, message, isInitial):
        n = self._key if isInitial is False else self._key0

        message = base64.b64decode(message)
        encrypted_msg1 = message[:16]
        encrypted_msg2 = message[16:]
        encrypted = (~int(binascii.hexlify(encrypted_msg1), 16)) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
        k = pow(encrypted, self._dkey, n)

        m = str(k)
        ak = m[:8*min(max(len(m)//8, 2), 4)].encode()
        aes = AES.new(ak, AES.MODE_CBC, encrypted_msg1[:AES.block_size])
        msg = aes.decrypt(encrypted_msg2)
        message = self._unpad(msg).decode()
        return message

    def _pad(self, s, blick_size):
        return s + (blick_size - len(s) % blick_size) * chr(blick_size - len(s) % blick_size)

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]

    def _byte_size(self, number):
        if number == 0:
            ret = 1
        else:
            try:
                num = number.bit_length()
            except AttributeError:
                raise TypeError('bit_size(num) only supports integers, not %r' % type(number))

            quanta, mod = divmod(num, 8)
            if mod:
                quanta += 1
            ret = quanta
        return ret

    def _int2bytes(self, number, fill_size=None, chunk_size=None):
        if number < 0: raise ValueError("Number must be an unsigned integer: %d" % number)
        if fill_size and chunk_size: raise ValueError("You can either fill or pad chunks, but not both")

        # Ensure these are integers.
        number & 1
        raw_bytes = b''

        # Pack the integer one machine word at a time into bytes.
        num = number
        word_bits, _, max_uint, pack_type = self._get_word_alignment(num)
        pack_format = ">%s" % pack_type
        while num > 0:
            raw_bytes = pack(pack_format, num & max_uint) + raw_bytes
            num >>= word_bits
        return raw_bytes

    def _get_word_alignment(self, num, force_arch=64, _machine_word_size=-1):
        MAX_INT = sys.maxsize
        MAX_INT64 = (1 << 63) - 1
        MAX_INT32 = (1 << 31) - 1
        MAX_INT16 = (1 << 15) - 1

        # Determine the word size of the processor.
        if _machine_word_size == -1:
            if MAX_INT == MAX_INT64: _machine_word_size = 64  # 64-bit processor.
            elif MAX_INT == MAX_INT32: _machine_word_size = 32  # 32-bit processor.
            else: _machine_word_size = 64 # Else we just assume 64-bit processor keeping up with modern times.

        max_uint64 = 0xffffffffffffffff
        max_uint32 = 0xffffffff
        max_uint16 = 0xffff
        max_uint8 = 0xff

        if force_arch == 64 and _machine_word_size >= 64 and num > max_uint32:
            # 64-bit unsigned integer.
            return 64, 8, max_uint64, "Q"
        elif num > max_uint16:
            # 32-bit unsigned integer
            return 32, 4, max_uint32, "L"
        elif num > max_uint8:
            # 16-bit unsigned integer.
            return 16, 2, max_uint16, "H"
        else:
            # 8-bit unsigned integer.
            return 8, 1, max_uint8, "B"



