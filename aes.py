from key_scheduling import key_scheduler 
import datetime
import random
import base64

# S-Box
S_BOX = [
    [0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76],
    [0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0],
    [0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15],
    [0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75],
    [0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84],
    [0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf],
    [0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8],
    [0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2],
    [0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73],
    [0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb],
    [0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79],
    [0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08],
    [0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a],
    [0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e],
    [0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf],
    [0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16]
]

# Inverse S-Box
inverse_S_BOX = [
    [0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb],
    [0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb],
    [0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e],
    [0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25],
    [0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92],
    [0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84],
    [0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06],
    [0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b],
    [0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73],
    [0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e],
    [0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b],
    [0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4],
    [0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f],
    [0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef],
    [0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61],
    [0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d]
]

# S-Box substitution
def sub_bytes(state):
    for i in range(4):
        for j in range(4):
            row = (state[i][j] & 0xF0) >> 4
            col = state[i][j] & 0x0F
            state[i][j] = S_BOX[row][col]

# inverse S-Box substitution
def inverse_sub_bytes(state):
    for i in range(4):
        for j in range(4):
            row = (state[i][j] & 0xF0) >> 4
            col = state[i][j] & 0x0F
            state[i][j] = inverse_S_BOX[row][col]
# ShiftRows
def shift_rows(state):
    state[1] = state[1][1:] + state[1][:1]
    state[2] = state[2][2:] + state[2][:2]
    state[3] = state[3][3:] + state[3][:3]

# inverse ShiftRows
def inverse_shift_rows(state):
    state[1] = state[1][3:] + state[1][:3]
    state[2] = state[2][2:] + state[2][:2]
    state[3] = state[3][1:] + state[3][:1]

# Xor with key
def add_round_key(state, round_key):
    """Perform AddRoundKey operation."""
    for i in range(4):
        for j in range(4):
            state[i][j] ^= round_key[i][j]

# Galois Field multiplication helper
def galois_mult(a, b):
    p = 0
    for i in range(8):
        if b & 1:
            p ^= a
        high_bit_set = a & 0x80
        a = (a << 1) & 0xFF
        if high_bit_set:
            a ^= 0x1b
        b >>= 1
    return p

# MixColumns
def mix_columns(state):
    for i in range(4):
        col = [state[j][i] for j in range(4)]
        state[0][i] = galois_mult(col[0], 2) ^ galois_mult(col[1], 3) ^ col[2] ^ col[3]
        state[1][i] = col[0] ^ galois_mult(col[1], 2) ^ galois_mult(col[2], 3) ^ col[3]
        state[2][i] = col[0] ^ col[1] ^ galois_mult(col[2], 2) ^ galois_mult(col[3], 3)
        state[3][i] = galois_mult(col[0], 3) ^ col[1] ^ col[2] ^ galois_mult(col[3], 2)

# Inverse MixColumns
def inverse_mix_columns(state):
    for i in range(4):
        col = [state[j][i] for j in range(4)]
        state[0][i] = galois_mult(col[0], 0x0e) ^ galois_mult(col[1], 0x0b) ^ galois_mult(col[2], 0x0d) ^ galois_mult(col[3], 0x09)
        state[1][i] = galois_mult(col[0], 0x09) ^ galois_mult(col[1], 0x0e) ^ galois_mult(col[2], 0x0b) ^ galois_mult(col[3], 0x0d)
        state[2][i] = galois_mult(col[0], 0x0d) ^ galois_mult(col[1], 0x09) ^ galois_mult(col[2], 0x0e) ^ galois_mult(col[3], 0x0b)
        state[3][i] = galois_mult(col[0], 0x0b) ^ galois_mult(col[1], 0x0d) ^ galois_mult(col[2], 0x09) ^ galois_mult(col[3], 0x0e)

# encrypt function
def aes_encrypt_logic(input_block, key):
    # Convert input block and key to matrix
    state = [[input_block[i + 4 * j] for j in range(4)] for i in range(4)]
    round_key = [[key[i + 4 * j] for j in range(4)] for i in range(4)]

    # Initial round
    add_round_key(state, round_key)

    # Main rounds
    for k in range(9):
        # Key for each round
        round_key = [[key[(i + 4 * j)+(k+1)*16] for j in range(4)] for i in range(4)]
        sub_bytes(state)
        shift_rows(state)
        mix_columns(state)
        add_round_key(state, round_key)
    
    # Final round
    round_key = [[key[i + 4 * j+160] for j in range(4)] for i in range(4)]
    sub_bytes(state)
    shift_rows(state)
    add_round_key(state, round_key)
    
    # Convert matrix back to an array
    output_block = [state[i][j] for j in range(4) for i in range(4)]
    return output_block

# decrypt function
def aes_decryption_logic(input_block, key):

    state = [[input_block[i + 4 * j] for j in range(4)] for i in range(4)]
    round_key = [[key[i + 4 * j+160] for j in range(4)] for i in range(4)]

    # final round
    add_round_key(state, round_key)
    inverse_shift_rows(state)
    inverse_sub_bytes(state)

    # main rounds
    for k in range(9):
        round_key = [[key[(i + 4 * j)+(9-k)*16] for j in range(4)] for i in range(4)]
        add_round_key(state, round_key)
        inverse_mix_columns(state)
        inverse_shift_rows(state)
        inverse_sub_bytes(state)

    # initial round
    round_key = [[key[i + 4 * j] for j in range(4)] for i in range(4)]
    add_round_key(state, round_key)

    output_block = [state[i][j] for j in range(4) for i in range(4)]
    return output_block

def aes_enc(string, key):
    # from string to [0x32, 0x43, 0xf6, 0xa8, 0x88, 0x5a, 0x30, 0x8d, 0x31, 0x31, 0x98, 0xa2, 0xe0, 0x37, 0x07, 0x34]
    string = [ord(char) for char in string]
    all_keys = key_scheduler(key)
    all_keys = [x for key_round in all_keys for x in key_round]
    if len(string) % 16 != 0:
        string += [0 for _ in range(16 - len(string) % 16)]
    encrypted_blocks = []
    for i in range(0, len(string), 16):
        encrypted_blocks.append(aes_encrypt_logic(string[i:i+16], all_keys))
    #return encrypted blocks as a continous string
    b =  [x for block in encrypted_blocks for x in block]
    #make b a string
    b = [chr(x) for x in b]
    return "".join(b)

def aes_dec(string, key):
    #from string to bytes
    string = [ord(char) for char in string]
    all_keys = key_scheduler(key)
    all_keys = [x for key_round in all_keys for x in key_round]
    # for each 16 element in the string decrypt it
    decrypted_blocks = []
    for i in range(0, len(string), 16):
        decrypted_blocks.append(aes_decryption_logic(string[i:i+16], all_keys))
    #return decrypted blocks as a continous string
    b =  [x for block in decrypted_blocks for x in block]
    #make b a string
    b = [chr(x) for x in b]
    return "".join(b)

def generate_key():
    #get the current date and time
    date = datetime.datetime.now()
    #create a seed from the date and time day*month*year*hour*minute*second
    seed = date.year * date.month * date.day * date.hour * date.minute * date.second * random.randint(0, 1000)
    random.seed(seed)
    key = [random.randint(0, 255) for _ in range(16)]
    return key

def key_to_string(key):
    # Convert the list of integers to bytes
    key_bytes = bytes(key)
    # Encode the bytes to a base64 string
    key_string = base64.b64encode(key_bytes).decode('utf-8')
    return key_string

def string_to_key(key_string):
    # Decode the base64 string back to bytes
    key_bytes = base64.b64decode(key_string)
    # Convert the bytes back to a list of integers
    key = list(key_bytes)
    return key

########################################################################################################
#                                        Test Function                                                 #
########################################################################################################
# key = generate_key()
# print(key)
# key_string = key_to_string(key)
# print(key_string)
# key = string_to_key(key_string)
# print(key)
# print(aes_enc("hello world", key))
# print(aes_dec(aes_enc("hello world", key), key))