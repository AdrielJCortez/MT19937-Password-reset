from MT19937 import MT19937
import base64

# read tokens from file
with open("tokens.txt", "r") as f:
    tokens = [line.strip() for line in f if line.strip()]

outputs = []

for token in tokens:
    decoded = base64.b64decode(token).decode("utf-8")
    nums = [int(x) for x in decoded.split(":")]
    outputs.extend(nums)

print("Total outputs collected:", len(outputs))
print(outputs[:16])


def undo_right_shift_xor(value, shift):
    result = 0
    for i in range(31, -1, -1):
        bit = (value >> i) & 1
        shifted_bit = 0
        if i + shift <= 31:
            shifted_bit = (result >> (i + shift)) & 1
        original_bit = bit ^ shifted_bit
        result |= (original_bit << i)
    return result & 0xffffffff


def undo_left_shift_xor_and(value, shift, mask):
    result = 0
    for i in range(32):
        bit = (value >> i) & 1
        shifted_bit = 0
        if i - shift >= 0 and ((mask >> i) & 1):
            shifted_bit = (result >> (i - shift)) & 1
        original_bit = bit ^ shifted_bit
        result |= (original_bit << i)
    return result & 0xffffffff


def untemper(z):
    y = undo_right_shift_xor(z, 18)
    y = undo_left_shift_xor_and(y, 15, 0xefc60000)
    y = undo_left_shift_xor_and(y, 7, 0x9d2c5680)
    x = undo_right_shift_xor(y, 11)
    return x & 0xffffffff


raw_state = [untemper(o) for o in outputs[:624]]

print("Recovered state count:", len(raw_state))
print("First 5 recovered values:", raw_state[:5])

actual = outputs[624:640]

found = False

for start_index in range(624):
    arranged_state = [0] * 624

    # place recovered values into the slots they were written to
    for i in range(624):
        arranged_state[(start_index + i) % 624] = raw_state[i]

    clone = MT19937(0)
    clone.set_state(arranged_state, start_index)

    predicted = [clone.extract_number() for _ in range(16)]

    if predicted == actual:
        print("FOUND MATCH")
        print("start_index =", start_index)
        print("Predicted next 16 =", predicted)
        found = True
        break

if not found:
    print("No matching rotation found.")