IMAGE_SIZE = 500
import numpy as np
import matplotlib.pyplot as plt

plt.ion()

fig1, ax1 = plt.subplots()
fig2, ax2 = plt.subplots()

# # this example doesn't work because array only contains zeroes
array = np.zeros(shape=(IMAGE_SIZE, IMAGE_SIZE), dtype=np.uint8)
axim1 = ax1.imshow(array)

array[0, 0] = 99  # this value allow imshow to initialise it's color scale
axim2 = ax2.imshow(array)

del array

for _ in range(50):
    print(".", end="")
    matrix = np.random.randint(0, 100, size=(IMAGE_SIZE, IMAGE_SIZE), dtype=np.uint8)

    axim1.set_data(matrix)
    fig1.canvas.flush_events()

    axim2.set_data(matrix)
    fig1.canvas.flush_events()

print()
