class MT19937:
    n = 624 # number of values in the internal state array
    m = 397 # offset
    w = 32  # word size
    r = 31  # number of lower bits used in splitting

    a = 0x9908b0df # twist constant

    # tempering constants
    u = 11
    s = 7
    t = 15
    l = 18

    # tempering masks
    b = 0x9d2c5680
    c = 0xefc60000

    # initialization constant
    f = 1812433253

    # lower 31 bits
    lower_mask = (1 << r) - 1

    # upper 1 bit
    upper_mask = ((1 << w) - 1) & (~lower_mask)

    def __init__(self, seed):
        # if server.py passes 4 random bytes, convert them to an int
        if isinstance(seed, bytes):
            seed = int.from_bytes(seed, "big")

        # Internal state array (624 integers)
        self.mt = [0] * self.n

        # index tells us which state value to output next
        # setting it to n means "state is not ready yet, twist first"
        self.index = self.n

        # step 1: Initialize state from seed
        self.mt[0] = seed & 0xffffffff

        for i in range(1, self.n):
            prev = self.mt[i - 1]
            # new_seed = f * (prev_seed ^ (prev_seed >> 30)) + i
            self.mt[i] = (self.f * (prev ^ (prev >> 30)) + i) & 0xffffffff

    # step 2: Generate one random number
    def extract_number(self):
        # if we have used all 624 state values, generate a fresh batch
        if self.index >= self.n:
            self.twist()

        # get the current state value
        y = self.mt[self.index]

        # step 3: Tempering (output transformation)
        y ^= (y >> self.u)
        y ^= ((y << self.s) & self.b)
        y ^= ((y << self.t) & self.c)
        y ^= (y >> self.l)

        # move to the next state value
        self.index += 1

        return y & 0xffffffff

    # twist all 624 state values at once
    def twist(self):
        for i in range(self.n):
            # combine upper bit of mt[i] and lower 31 bits of mt[i+1]
            x = (self.mt[i] & self.upper_mask) + (self.mt[(i + 1) % self.n] & self.lower_mask)

            # shift right by 1
            xA = x >> 1

            # if x is odd, add extra mixing
            if x & 1:
                xA ^= self.a

            # compute the new state value using the value 397 ahead
            self.mt[i] = self.mt[(i + self.m) % self.n] ^ xA

        # after twisting, start reading outputs again from index 0
        self.index = 0

    # allow us to directly load recovered state for the attack
    def set_state(self, state_array, index=624):
        self.mt = [x & 0xffffffff for x in state_array]
        self.index = index