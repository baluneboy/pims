HSKP_STEP = 0.05  # voltage step for encoded housekeeping outputs (nominally 0.05 for 50 mV)

def convert_7bits_to_int(b):
    """return int value converted from list of 7 bits"""
    if not len(b) == 7:
        raise ValueError('cannot convert, need exactly 7 bits')
    b_string = '0' + ''.join([str(bit) for bit in b])  # prepend zero to get 8 bits
    # print(b, 'gives b_string =', b_string)
    return int(b_string, 2)


def convert_hskp_index_to_3bits(idx_h):
    """convert hskp_index to 3-bit value"""
    if idx_h not in range(7):
        raise ValueError('cannot convert, need index to be in range(7)')
    h_string = '{0:03b}'.format(idx_h)
    # print('idx_h = ', idx_h, ' gives binary h_string = ', h_string)
    return [int(i) for i in h_string]


def pluck_4bits(dins, keep_indices):
    """return list of 4 dins at keep_indices locations"""
    if not len(dins) == 8:
        raise ValueError('unhandled condition when len(dins) is not 8')
    if not all([idx in range(8) for idx in keep_indices]):
        raise ValueError('cannot pluck dins, not all of keep_indices is in range(8)')
    return [dins[i] for i in keep_indices]


def convert_state_to_hskp_voltage(dins8, keep_inds, hskp_ind):
    """return floating point voltage value from state integer (saturates at min=0V and max=5V)"""
    upper_4bits = pluck_4bits(dins8, keep_inds)
    lower_3bits = convert_hskp_index_to_3bits(hskp_ind)
    state_7bits = upper_4bits + lower_3bits
    state_int = convert_7bits_to_int(state_7bits)
    v = state_int * HSKP_STEP
    v1 = min(v, 5.0)
    return max(v1, 0.0)


def demo_get_state():
    keep_idx = [0, 1, 4, 5]  # 0, 1, 4, 5 for X1, X2, Z1, Z2
    for hskp_index in range(7):
        for d in range(256):
            dins8 = demo_convert8bits(d)
            print(' '.join([str(i) for i in dins8]), '  << dins8')
            xx = [dins8[x] if x in keep_idx else ' ' for x in range(8)]
            print(' '.join([str(i) for i in xx]), '  << dins8 keepers')
            left4bits = pluck_4bits(dins8, keep_idx)
            right3bits = convert_hskp_index_to_3bits(hskp_index)
            h_string = '{0:03b}'.format(hskp_index)
            print(' '*12 + ' '.join(str(hh) for hh in h_string), '<< hskp_index = %d as 3 bits' % hskp_index)
            state_7bits = left4bits + right3bits
            state_int = convert_7bits_to_int(state_7bits)
            hskp_volts = convert_state_to_hskp_voltage(dins8, keep_idx, hskp_index)
            print('    ' + ' '.join([str(i) for i in state_7bits]), '<< state_7bits = %d = %.2f V' % (state_int, hskp_volts))
            print('-'*55)


def check_7bit_conversion():
    for d in range(128):
        d_string = '{0:07b}'.format(d)
        i7 = [int(s) for s in d_string]
        hv = convert_7bits_to_int(i7) * HSKP_STEP
        print('{:.2f} {:>3} {:<9}'.format(hv, d, d_string))


def demo_convert8bits(d):
    d_string = '{0:08b}'.format(d)
    return [int(s) for s in d_string]


if __name__ == '__main__':
    # check_7bit_conversion()
    demo_get_state()
