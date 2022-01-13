import threading
import queue
from queue import Empty

class Workers:
    def __init__(self, path_queue: queue.Queue, func, num_threads: int = 1):
        self._queue = path_queue
        self._threads = []
        self._num_threads = num_threads
        self._func = func

    def set_num_threads(self, num_threads: int):
        self._num_threads = num_threads

    def get_num_threads(self) -> int:
        return self._num_threads

    def _worker_wrapper(self):
        while True:
            try:
                path = self._queue.get_nowait()
            except Empty:
                break
            self._func(path)

    def start_workers(self):
        """ Assuming it is not called when other threads are joint! """
        l = len(self._threads)  # current running threads
        if l >= self._num_threads:
            return
        diff = self._num_threads - l
        for _ in range(diff):
            t = threading.Thread(target=self._worker_wrapper)
            t.start()
            self._threads.append(t)

    def wait_for_all_workers(self):
        for t in self._threads:
            t.join()
            