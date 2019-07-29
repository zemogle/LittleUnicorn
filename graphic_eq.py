import numpy as np

SAMPLE_RATE = 44100
CHUNK_SIZE = 4096

def piff(val):
    return int(2 * CHUNK_SIZE * val / SAMPLE_RATE)

def volume_frequency_range(power, freq_low, freq_high):
    try:
        volume = int(np.mean(power[piff(freq_low):piff(freq_high):1]))
        return volume
    except:
        return 0

def calculate_levels(data):
    weighting = [2, 8, 8, 8]

    power = 100000*np.abs(data['data'])
    # print(power)
    matrix = [0, 0, 0, 0]
    matrix[0] = volume_frequency_range(power, 0, 64)
    matrix[1] = volume_frequency_range(power,64, 128)
    matrix[2] = volume_frequency_range(power, 128, 192)
    matrix[3] = volume_frequency_range(power, 192, 266)

    # Tidy up column values for the LED matrix
    matrix = np.divide(np.multiply(matrix, weighting),2000)
    # Set floor at 0 and ceiling at 16 for LED matrix
    matrix = matrix.clip(0, 16)
    return matrix
