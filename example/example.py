from time import sleep as slp

def timer():
    for i in range(0, 7):
        print(f'time: {i}')
        i+=1
        slp(0.5)

timer()