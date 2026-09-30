import devsup.ptable as PT
from devsup.hooks import addHook
from devsup import NO_ALARM, MINOR_ALARM, MAJOR_ALARM, INVALID_ALARM, COMM_ALARM, READ_ALARM
import signal
import time
from threading import Thread


class AlarmTest(PT.TableBase):
    pini_no = PT.Parameter(iointr=True)
    pini_yes = PT.Parameter(iointr=True)
    ai_42 = PT.Parameter(iointr=True)
    ao_42 = PT.Parameter(iointr=True)
    ai_rval_info = PT.Parameter(iointr=True)
    ao_rval_info = PT.Parameter(iointr=True)
    ai_val_info = PT.Parameter(iointr=True)
    ao_val_info = PT.Parameter(iointr=True)
    ai_rval_eslo = PT.Parameter(iointr=True)
    ai_val_eslo = PT.Parameter(iointr=True)

    def __init__(self, name):
        super().__init__(name=name)
        self.stop = False
        self.run_thread = Thread(target=self._run)

    def start(self):
        self.run_thread.start()

    def stop_threads(self):
        print("stopping threads")
        self.stop = True
        self.run_thread.join()

    def _run(self):
        count = 0
        while not self.stop:
            self.pini_yes.value = count
            if count % 2:
                self.pini_yes.alarm = NO_ALARM
                self.pini_yes.amsg = None
            else:
                self.pini_yes.alarm = MAJOR_ALARM
                self.pini_yes.amsg = "even number"

            self.pini_yes.notify()
            print(count)

            self.ai_42.value = 42
            self.ai_42.notify()

            self.ao_42.value = 42
            self.ao_42.notify()

            self.ai_rval_info.value = 42
            self.ai_rval_info.notify()

            # only sets RVAL and VAL should stay 0 since it's an ao 
            self.ao_rval_info.value = 42
            self.ao_rval_info.notify()

            self.ai_val_info.value = 42
            self.ai_val_info.notify()

            self.ao_val_info.value = 42
            self.ao_val_info.notify()

            # this should set RVAL and then DB ESLO/EOFF applies
            self.ai_rval_eslo.value = 42
            self.ai_rval_eslo.notify()

            self.ai_val_eslo.value = 42
            self.ai_val_eslo.notify()

            #self.pini_no.value = count
            #self.pini_no.notify()

            count += 1
            time.sleep(5)

def build():
    sup = AlarmTest(name="alarm")

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    addHook('AfterIocRunning', sup.start)
    addHook('AtIocExit', sup.stop_threads)

    return sup
