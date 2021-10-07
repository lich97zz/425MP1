import time
def f():
    
    a = 123
    def g():
        nonlocal a
        a = 345
    print(a)

f()
    
    
