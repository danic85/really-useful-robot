# import threading

# class thread_manager:
    # def __init__(self):
    #     self.threads = {}
    #
    # def __del__(self):
    #     for i in self.threads:
    #         self.threads[i].stop()
    #
    # def add_thread(self, name, target, args):
    #     if self.threads[name]:
    #         return False
    #     self.threads[name] = threading.Thread(target=target, args=args)
    #     self.threads[name].start()
    #     return True
    #
    # def get_thread(self, name):
    #     if self.threads[name]:
    #         return self.threads[name]
    #     return None
    #
    # def remove_thread(self, name):
    #     if self.threads[name]:
    #         self.threads[name].join()
    #         del self.threads[name]
    #         return True
    #     return False