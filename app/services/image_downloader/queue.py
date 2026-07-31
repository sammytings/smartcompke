from queue import Queue as PythonQueue


class ImageQueue:
    """
    Thread-safe queue used between
    image download workers and the database writer.
    """

    def __init__(self):

        self.queue = PythonQueue()


    def put(self, item):

        self.queue.put(item)



    def get(self):

        return self.queue.get()



    def task_done(self):

        self.queue.task_done()



    def join(self):

        self.queue.join()



    def empty(self):

        return self.queue.empty()