# -*- coding: utf-8 -*-
from string import ascii_uppercase, ascii_lowercase, digits

# string codes
BASE64_STR_CODES = '{}{}{}+/='.format(ascii_uppercase, ascii_lowercase, digits)
URL_STR_CODES = '{}{}{}+-$'.format(ascii_uppercase, ascii_lowercase, digits)

REVERSE_BASE64_STR_CODES = {}
REVERSE_URL_STR_CODES = {}

for i in range(len(BASE64_STR_CODES)):
    REVERSE_BASE64_STR_CODES[BASE64_STR_CODES[i]] = i

for i in range(len(URL_STR_CODES)):
    REVERSE_URL_STR_CODES[URL_STR_CODES[i]] = i

get_reverse_uri_code = lambda c : REVERSE_URL_STR_CODES[c]
get_reverse_base64_code = lambda c : REVERSE_BASE64_STR_CODES[c]

# data structure for lzw

class LZW_CDICT(dict):

    def __init__(self, word_bits : int=2, capacity : int=2, size : int=2):
        super(LZW_CDICT, self).__init__()
        self.word_bits = word_bits
        self.capacity = capacity
        self.size = size

    # put a new key in LZW_DICT
    def put(self, key : str):
        if key not in self:
            self.size += 1
            self.update({ key : self.size })

    '''
        check whether capacity of current word_bits is 0
        if 0 => expand word_bits to add capacity
    '''
    def reduce_capacity(self):
        self.capacity -= 1
        if self.capacity == 0:
            self.capacity = 2 ** self.word_bits
            self.word_bits += 1

class LZW_CDATA(list):
    def __init__(self, pos : int=0, val : int=0, char_bits : int=16, getChr=chr):
        super(LZW_CDATA, self).__init__()
        self.pos = pos
        self.val = val
        self.char_bits = char_bits
        self.getChr = getChr

    def update(self, val : int):
        self.val = val
        if (self.pos+1) == self.char_bits:
            self.append(self.getChr(self.val))
            self.pos = 0
            self.val = 0
        else:
            self.pos += 1

    def __str__(self):
        return ''.join(self)

    @property
    def text(self):
        return str(self)

# TODO
class LZW_DDICT(LZW_CDICT):
    def __init__(self, word_bits : int=2, capacity : int=2, size : int=2):
        super(LZW_DDICT, self).__init__(word_bits, capacity, size)

        # special word for encode byte and end
        for i in range(3):
            self[i] = i

    # put a new val in LZW_DICT
    def put(self, val : str) -> int:
        if val not in self:
            self.size += 1
            self.update({ self.size : val })
        return self.size

class LZW_DDATA(list):
    def __init__(self, getVal, length : int=0, char_size : int=16):
        '''
            getVal is a function to get next char in data and convert to origin data
        '''
        super(LZW_DDATA, self).__init__()
        self.max_mask = 1 << (char_size-1)
        self.mask = self.max_mask
        self.getVal = getVal
        self.index = 0
        self.length = length

        self.val = self.get()

    def get(self) -> int:
        val = 0
        if self.index < self.length:
            val = self.getVal(self.index)
            self.index += 1
        return val

    def get_chunk(self, bits : int=2) -> int:
        chunk = 0
        pos = 1
        for _ in range(bits):
            if (self.val & self.mask) != 0:
                chunk |= pos
            pos <<= 1
            self.mask >>= 1
            if self.mask == 0:
                self.val = self.get()
                self.mask = self.max_mask

        return chunk

    def get_char(self, char_bits : int=8) -> str:
        '''
            get bits from encode data reverse,
            since we put data reverse.
            B = 100010, we put order 010001

            chunk 0 => next is a 1 byte char
            chunk 1 => next is a 2 byte char
        '''
        val = 0
        pos = 1
        for _ in range(char_bits):
            if (self.val & self.mask) != 0:
                val |= pos
            pos <<= 1
            self.mask >>= 1
            if self.mask == 0:
                self.val = self.get()
                self.mask = self.max_mask
        return chr(val)

    def empty(self) -> bool:
        return self.index>self.length
            
    def __str__(self):
        return ''.join(self)

    @property
    def text(self):
        return str(self)

def _compress(data : str='', char_size : int=16, getChr=chr) -> str:
    '''
        data : string to be compress by lzw algorithm
        char_size:
            normal = 16
            utf-16 = 15
            base64 = 6
            uri encode = 16
        getChr: function to convert encoded data to char
    '''
    if len(data) == 0:  return ''

    '''
        lzw_alogorithm:
            s = ''
            c = ''
            for c in data:
                if c is first appear char => add to lzw_dict and new_char_set
                sc = s+c

                if sc in lzw_dict => s = sc
                else:
                    if s is new_char_set:
                        encode strategy:
                            1 byte char => word(value=0, size=current lzw word bits) + reverse bit char value(8 bit)
                            2 byte char => word(value=1, size=current lzw word bits) + reverse bit char value(16 bit)
                    else => encode lzw[s] value

                    add (sc) to lzw_dict
                    s = c

        in the end clean data of s and encode value(2) as finish and full last char
    '''
    lzw_dict = LZW_CDICT(2, 2, 2)
    result = LZW_CDATA(0, 0, char_size, getChr)
    new_char_set = set()
    s = ''
    sc = ''

    for c in data:
        if c not in lzw_dict:
            lzw_dict.put(c)
            new_char_set.add(c)

        sc = s + c

        if sc in lzw_dict:
            s = sc
        else:
            if s in new_char_set:
                char_value = ord(s[0])
                if char_value < 256:
                    for _ in range(lzw_dict.word_bits):
                        result.update(result.val<<1)

                    for _ in range(8):
                        new_val = (result.val<<1) | (char_value&1)
                        result.update(new_val)
                        char_value >>= 1

                else:
                    value = 1
                    for _ in range(lzw_dict.word_bits):
                        new_val.update(result.val | value)
                        value >>= 1

                    for _ in range(16):
                        new_val = (result.val<<1) | (char_value&1)
                        result.update(new_val)
                        char_value >>= 1

                # reduce 1 capacity since word value 0 or 1 to point next is char
                new_char_set.remove(s)
                lzw_dict.reduce_capacity()

            else:
                value = lzw_dict[s]
                for _ in range(lzw_dict.word_bits):
                    new_val = (result.val<<1) | (value&1)
                    result.update(new_val)
                    value >>= 1

            lzw_dict.reduce_capacity()
            lzw_dict.put(sc)
            s = c

    # clean s
    if len(s) != 0:
        if s in new_char_set:
            char_value = ord(s[0])
            if char_value < 256:
                for _ in range(lzw_dict.word_bits):
                    result.update(result.val << 1)
                for _ in range(8):
                    new_val = (result.val<<1) | (char_value&1)
                    result.update(new_val)

            else:
                value = 1
                for _ in range(lzw_dict.word_bits):
                    result.update(result.val | value)
                    value >>= 1

                for _ in range(lzw_dict.word_bits):
                    new_val = (result.val<<1) | (char_value&1)
                    result.update(new_val)
                    char_value >>= 1

            lzw_dict.reduce_capacity()

        else:
            value = lzw_dict[s]
            for _ in range(lzw_dict.word_bits):
                new_val = (result.val<<1) | (value&1)
                result.update(new_val)
                value >>= 1

        lzw_dict.reduce_capacity()

        # encode word(2) as end
        value = 2
        for _ in range(lzw_dict.word_bits):
            result.update((result.val<<1) | (value&1))
            value >>= 1

        while True:
            result.update(result.val<<1)
            if result.pos == 0:
                break

    return result.text

def _decompress(getValue, length : int=0, char_size : int=16) -> str:
    if length == 0:  return ''

    #lzw_dict = LZW_DDICT(3, 4, 2)
    lzw_dict = LZW_DDICT(2, 2, 2)
    result = LZW_DDATA(getValue, length, char_size)
    s = ''
    entry = ''
    key = 0

    while not result.empty():
        chunk = result.get_chunk(lzw_dict.word_bits)
        key = chunk
        
        if chunk == 0:
            entry = result.get_char(8)
            key = lzw_dict.put(entry)
            # char use 2 chunk
            lzw_dict.reduce_capacity()

        elif chunk == 1:
            entry = result.get_char(16)
            key = lzw_dict.put(entry)
            # char use 2 chunk
            lzw_dict.reduce_capacity()

        # chunk 2
        elif chunk == 2:
            return result.text

        if key not in lzw_dict:
            '''
                special case:   AAAABBBB
                dict = {A=>3, AA=>4, AAA=>5, D=>6, ...}
                when decode key 2, we can't get dict[2] = AA
                so we need to get last add s + s[0]
            '''
            if key == (lzw_dict.size+1):
                entry = s + s[0]
            else:
                return ''
        else:
            entry = lzw_dict[key]

        result.append(entry)

        if len(s) != 0:
            lzw_dict.put(s+entry[0])
        lzw_dict.reduce_capacity()
        s = entry

    return result.text

class LZString(object):
    def compress(self, data : str='') -> str:
        return _compress(data, 16, chr)

    def compress_utf16(self, data : str='') -> str:
        return _compress(data, 15, lambda val: chr(val+32)) + ' '

    def compress_base64(self, data : str='') -> str:
        result = _compress(data, 6, lambda val: BASE64_STR_CODES[val])
        padding = 4- (len(result) % 4)
        
        if 4 > padding > 0:    result += padding*'='
        return result

    def compress_encodeuri(self, data : str='') -> str:
        return _compress(data, 6, lambda val : URL_STR_CODES[val])

    def decompress(self, data : str='') -> str:
        return _decompress(lambda index : ord(data[index]), len(data), 16)

    def decompress_utf16(self, data : str='') -> str:
        return _decompress(lambda index : ord(data[index])-32, len(data), 15)

    def decompress_base64(self, data : str='') -> str:
        return _decompress(lambda index : get_reverse_base64_code(data[index]), len(data), 6)

    def decompress_encodeuri(self, data : str='') -> str:
        data = data.replace(' ', '+')
        return _decompress(lambda index : get_reverse_uri_code(data[index]), len(data), 6)