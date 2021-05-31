import codecs


with open('/home/pims/Documents/input_data.txt', 'r') as file:
    data = file.read().replace('\n', '')

data_rot13 = codecs.encode(data, 'rot_13')

print(data_rot13)
