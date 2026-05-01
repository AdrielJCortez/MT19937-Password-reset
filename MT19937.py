import time
import random
import base64

class MT19937:
    n = 624 # number of values in the internal state array 
    m = 397 # offset
    w = 32 # Word size
    r = 31 # # of lower bits used in splitting

    # lower 31 bits
    LMASK = (1 << r) - 1

    # upper 1 bit
    UMASK = ((1 << w) - 1) & (~LMASK)

    a = 0x9908b0df # twist constant

    # tempering constanats
    u = 11
    s = 7
    t = 15
    l = 18

    # tempering masks
    b = 0x9d2c5680
    c = 0xefc60000

    # initialization constant
    f = 1812433253

    def __init__(self, seed: int):
        # if seed is 4 raw bytes, convert it to an integer
        if isinstance(seed, bytes):
            seed = int.from_bytes(seed, byteorder="big")

        # Internal state array (624 integers)
        self.state = [0] * self.n

        # index into state array
        # set to n so we twist before first extract
        self.index = self.n

        self.initialize(seed)

    
    # step 1: Initialize state from seed
    def initialize(self, seed: int):
        self.state[0] = seed & 0xffffffff

        for i in range(1, self.n):
            prev = self.state[i - 1]
            # new_seed = f * (prev_seed ^ (prev_seed >> (w-2))) + i
            val = self.f * (prev ^ (prev >> 30)) + i
            self.state[i] = val & 0xffffffff  # force 32-bit

        # state exists now, but standard MT twists before first extraction
        self.index = self.n

    # step 2: Generate one random number
    # (uses existing state, and twists only when all 624 values are used)
    def random_uint32(self) -> int:
        # if we have used all state values, twist the whole state array, force it to run before producing the output
        if self.index >= self.n:
            self.twist()

        # get current state value
        y = self.state[self.index]

        # Move index forward
        self.index += 1

        # STEP 3: Tempering (output transformation)
        y = y ^ (y >> self.u)
        y = y ^ ((y << self.s) & self.b)
        y = y ^ ((y << self.t) & self.c)
        z = y ^ (y >> self.l)

        return z & 0xffffffff  # ensure 32-bit output

    # server.py expects this method name
    def extract_number(self):
        return self.random_uint32()

    # twist all 624 state values at once
    def twist(self):
        for i in range(self.n):
            # Combine upper bit of state[i] and lower bits of state[i+1]
            x = (self.state[i] & self.UMASK) | (self.state[(i + 1) % self.n] & self.LMASK)
            # Twist transformation
            xA = x >> 1

            # if odd add extra mixing
            if x & 1:
                xA ^= self.a

            # Compute new state value
            # new_state[i] = state[i+397] XOR xA
            self.state[i] = (self.state[(i + self.m) % self.n] ^ xA) & 0xffffffff

        # after twisting, start reading from the beginning again
        self.index = 0

    # useful for Task II when cloning recovered state
    def set_state(self, state_array, index=624):
        self.state = [x & 0xffffffff for x in state_array]
        self.index = index


# "server" gives us a random output based on time (also chosen on random)
def oracle():
    # Wait 5 to 60 seconds
    time.sleep(random.randint(5, 60))

    # Seed with current UNIX timestamp
    seed = int(time.time())
    mt = MT19937(seed)

    # Wait another 5 to 60 seconds
    time.sleep(random.randint(5, 60))

    # First 32-bit output
    output = mt.random_uint32()

    # Convert to 4 bytes big endian then base64 encode
    output_bytes = output.to_bytes(4, byteorder="big")
    output_b64 = base64.b64encode(output_bytes).decode("ascii")

    return seed, output_b64


# FOR TESTING
def oracle_fast():
    time.sleep(1)
    seed = int(time.time())
    mt = MT19937(seed)
    time.sleep(1)

    output = mt.random_uint32()
    output_bytes = output.to_bytes(4, byteorder="big")
    output_b64 = base64.b64encode(output_bytes).decode("ascii")
    return seed, output_b64


def crack_seed_from_b64(output_b64, search_window=300):
    # Decode base64 back to 4 raw bytes
    output_bytes = base64.b64decode(output_b64)

    # Convert bytes to 32-bit integer using big endian
    target_output = int.from_bytes(output_bytes, byteorder="big")

    # Assume seed was a recent UNIX timestamp (Guess the seed)
    guess = int(time.time()) # time since 1970 in seconds

    # try last 5 minutes (try the last 5 minutes)
    for possible_seed in range(guess, guess - search_window, -1):
        # see if we get the same output
        mt = MT19937(possible_seed)
        test_output = mt.random_uint32()

        # if outputs match we found the seed that maps to the string (base 64 string)
        if test_output == target_output:
            return possible_seed

    return None


# use fast version for testing so we also get the real seed back
real_seed, oracle_output = oracle_fast()
guessed_seed = crack_seed_from_b64(oracle_output)

print("Oracle returned:", oracle_output)
print("Real seed:     ", real_seed)
print("Guessed seed:  ", guessed_seed)
print("Success:", real_seed == guessed_seed)