from queue import Empty
from threading import Thread

from django.db import close_old_connections

from .image_saver import ImageSaver


class ImageWriter(Thread):
    """
    Single database writer.

    Download threads never touch Django models.

    They simply enqueue completed downloads.

    This thread performs all database writes,
    preventing SQLite/PostgreSQL locking issues.
    """

    daemon = True

    def __init__(self, queue):

        super().__init__()

        self.queue = queue

        self.saved = 0
        self.failed = 0

        self.running = True

    def stop(self):

        self.running = False

    def run(self):

        close_old_connections()

        while self.running or not self.queue.empty():

            try:

                item = self.queue.get(timeout=1)

            except Empty:

                continue

            if item is None:

                self.queue.task_done()

                break

            try:

                ImageSaver.save_product_image(

                    product=item["product"],

                    file=item["temp_file"],

                    filename=item["filename"],

                    primary=item["primary"],
                )

                self.saved += 1

            except Exception as e:

                self.failed += 1

                print()
                print("=" * 70)
                print("DATABASE SAVE FAILED")
                print(item["product"].name)
                print(e)
                print("=" * 70)

            finally:

                try:
                    item["temp_file"].close()
                except Exception:
                    pass

                self.queue.task_done()

        close_old_connections()

    @classmethod
    def save(cls, jobs):

        """
        Compatibility helper for the
        management command.
        """

        from queue import Queue

        q = Queue()

        writer = cls(q)

        writer.start()

        for job in jobs:

            q.put(job)

        q.put(None)

        q.join()

        writer.stop()

        writer.join()