import threading
import time

class MyTimer:
    def __init__(self, onEndCallback) -> None:
        self.onEndCallback = onEndCallback
    
    def start(self, interval):
        self.start_time = time.time()
        self._timer = threading.Timer(interval, self.onEndCallback)
        self._timer.start()

    def remaining(self):
        return self.start_time + self._timer.interval - time.time()
    
    def cancel(self):
        self._timer.cancel()

    def elapsed(self):
        return time.time() - self.start_time
    
def test():
    timer = MyTimer(lambda: print("Timer ended"))
    timer.start(5)
    print("Timer started")
    print("Remaining time: ", timer.remaining())
    time.sleep(2)
    print("Remaining time: ", timer.remaining())
    timer.cancel()
    print("Timer cancelled")
    print("Elapsed time: ", timer.elapsed())

if __name__ == "__main__":
    # test()
    ls = [1]
    print(ls[1:])