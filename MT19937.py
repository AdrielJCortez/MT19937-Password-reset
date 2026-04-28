class MT19937:
    n = 624 # number of values in the internal state array 
    m = 397 # offset
    w = 32 # Word size
    r = 31 # # of lower bits used in splitting

    UMASK = 0xffffffff << r & 0xffffffff  # upper 1 bit
    LMASK = (1 << r) - 1                  # lower 31 bits

    a = 0x9908b0df # twist constant

    # tempering constanats
    u = 11
    s = 7
    t = 15
    l = 18

    # tampering masks
    b = 0x9d2c5680
    c = 0xefc60000

    # initialization constant
    f = 1812433253

    def __init__(self, seed: int):
        # if server.py passes 4 random bytes, convert them to an int
        if isinstance(seed, bytes):
            seed = int.from_bytes(seed, "big")

        # Internal state array (624 integers)
        self.state = [0] * self.n
        self.index = 0
        self.initialize(seed)

    
    # step 1: Initialize state from seed
    def initialize(self, seed: int):
        self.state[0] = seed & 0xffffffff

        for i in range(1, self.n):
            prev = self.state[i - 1]
            # new_seed = f * (prev_seed ^ (prev_seed >> (w-2))) + i
            val = self.f * (prev ^ (prev >> 30)) + i
            self.state[i] = val & 0xffffffff  # force 32-bit

        self.index = 0

    # step 2: Generate one random number
    # (includes twist + tempering)
    def random_uint32(self) -> int:
        k = self.index  # current index

        # Get x[k+1] using circular indexing
        # j is the index after k
        j = k - (self.n - 1)
        if j < 0:
            j += self.n

        # Combine upper bit of x[k] and lower bits of x[k+1]
        x = (self.state[k] & self.UMASK) | (self.state[j] & self.LMASK)

        # Twist transformation
        xA = x >> 1
        # if odd add extra mixing
        if x & 1:  # if lowest bit is 1
            xA ^= self.a

        # Get x[k+397]
        j = k - (self.n - self.m)
        if j < 0:
            j += self.n

        # Compute new state value
        # new_state[k] = state[k+397] XOR xA
        x = self.state[j] ^ xA
        self.state[k] = x & 0xffffffff  # store back (32-bit)

        # Move index forward (circular)
        k += 1
        if k >= self.n:
            k = 0
        self.index = k

        # STEP 3: Tempering (output transformation)
        y = x ^ (x >> self.u)
        y = y ^ ((y << self.s) & self.b)
        y = y ^ ((y << self.t) & self.c)
        z = y ^ (y >> self.l)

        return z & 0xffffffff  # ensure 32-bit output

    # server.py expects this method name
    def extract_number(self):
        return self.random_uint32()