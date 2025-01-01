import random
import datetime
from math import gcd
from sympy import randprime

def generate_prime_number():
    #get the current date and time
    date = datetime.datetime.now()
    #create a seed from the date and time day*month*year*hour*minute*second
    seed = date.year * date.month * date.day * date.hour * date.minute * date.second
    random.seed(seed)
    prime_number = randprime(2**1024, 2**1025)
    return prime_number

def mult_inverse(a, m): 
    #extended euclidean algorithm
    m0 = m
    y = 0
    x = 1
    if (m == 1):
        return 0
    while (a > 1):
        q = a // m
        t = m
        m = a % m
        a = t
        t = y
        y = x - q * y
        x = t
        # if a is non type
        if type(a) != int:
            break
    if (x < 0):
        x = x + m0
    return x


def find_e(phi_n):
    e = random.randint(2, phi_n - 1)
    if gcd(e, phi_n) == 1:
        return e

def generate_keys():
    p = generate_prime_number()
    q = generate_prime_number()
    n = p * q
    phi_n = (p - 1) * (q - 1)
    e = None
    while type(e) != int:
        e = find_e(phi_n)
    d = mult_inverse(e, phi_n)
    return (e, n), (d, p, q, n)

def encrypt_rsa(plain_text, public_key):
    e, n = public_key
    #checks if the plain text is a string
    if type(plain_text) == str:
        plain_text = int.from_bytes(plain_text.encode(), 'big')
    #if plaintext > n return error
    if(plain_text > n):
        return "Error: Plain text is greater than n"
    # c = m^e mod n
    cipher_text = pow(plain_text, e, n)
    return cipher_text

def decrypt_rsa(cipher_text, private_key):
    d, p, q, n = private_key
    # m = c^d mod n
    plain_text = pow(cipher_text, d, n)
    #reuse the plain text as a string
    plain_string = plain_text.to_bytes((plain_text.bit_length() + 7) // 8, 'big').decode()
    return plain_string

def sign_rsa(plain_text, private_key):
    d, p, q, n = private_key
    # s = m^d mod n
    signature = pow(plain_text, d, n)
    return signature

def verify_rsa(signature, public_key):
    e, n = public_key
    # m = s^e mod n
    plain_text = pow(signature, e, n)
    return plain_text

########################################################################################################
#                                        Test Function                                                 #
########################################################################################################

# [pu_key , pr_key] = generate_keys()
# plain_text = "ÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿ"
# cipher_text = encrypt_rsa(plain_text, pu_key)
# print(cipher_text)
# decrypted_text = decrypt_rsa(cipher_text, pr_key)
# print(decrypted_text)
