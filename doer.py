#!/usr/bin/env python

from caerbannog import Caerbannog, App

class ArmrestImporter(Caerbannog):
    def __init__(self, host='localhost'):
        super(ArmrestImporter, self).__init__('armrest', 'importer', host=host)

        self.route('tasks.import', self.task_import)
        self.route('armrest.c2', self.c2)

    def task_import(self, msg):
        print " [m] task_import: [%r]" % (msg,)

    def c2(self, msg):
        print " [m] c2: [%r]" % (msg,)


if __name__ == "__main__":
    app = App(ArmrestImporter)
    app.do_daemon()