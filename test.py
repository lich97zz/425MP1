import time
a = 123
def f():
    global a
    def g():
        print(a)
    g()

f()
    
    
