import functools
import traceback
import logging
import threading
from PyQt5.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal, pyqtSlot

# --- Global Thread Pool ---
thread_pool = QThreadPool.globalInstance()
thread_pool.setMaxThreadCount(8)

def run_in_thread(_func=None, *, on_result=None, on_error=None, on_print=None, on_emit=None):
    """
    Decorator to run a class method in background using QRunnable + QThreadPool.
    Emits result, print, emit, and error signals safely to UI thread.
    Warns if nested thread usage is detected (threaded function calling another).
    """

    # --- Signal Class (scoped) ---
    class TaskSignals(QObject):
        result = pyqtSignal(object)
        error = pyqtSignal(str)
        printed = pyqtSignal(str)
        emit_signal = pyqtSignal(str)

    # --- Runnable Class (scoped) ---
    class TaskRunnable(QRunnable):
        def __init__(self, fn, args, kwargs, signals):
            super().__init__()
            self.fn = fn
            self.args = args
            self.kwargs = kwargs
            self.signals = signals

        @pyqtSlot()
        def run(self):
            try:
                # Debug Info (optional)
                # print(f"🔧 Running: {self.fn.__name__}")
                # print(f"🧵 Thread: {threading.current_thread().name}")
                # print(f"📊 Active: {thread_pool.activeThreadCount()} / {thread_pool.maxThreadCount()}")

                result = self.fn(*self.args, **self.kwargs)

                if isinstance(result, dict):
                    if 'print' in result:
                        self.signals.printed.emit(str(result['print']))
                    if 'emit' in result:
                        self.signals.emit_signal.emit(result['emit'])
                    if 'result' in result:
                        self.signals.result.emit(result['result'])
                    elif not result.get('result'):
                        self.signals.result.emit(None)
                else:
                    self.signals.result.emit(result)

            except Exception as e:
                tb = traceback.format_exc()
                logging.error(f"[ThreadWorker Error] {e}\n{tb}")
                self.signals.error.emit(str(e))

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self = args[0]

            # ⚠️ Nested Thread Warning
            current_thread = threading.current_thread().name
            if "ThreadPoolThread" in current_thread:
                print(f"⚠️ Warning: '{func.__name__}' is being called from within another thread ({current_thread}). "
                      "Nested threading can cause async bugs or race conditions. Consider chaining instead.")

            signals = TaskSignals()

            if on_result:
                signals.result.connect(lambda res: on_result(self, res))
            if on_error:
                signals.error.connect(lambda err: on_error(self, err))
            if on_print:
                signals.printed.connect(lambda msg: on_print(self, msg))
            if on_emit:
                signals.emit_signal.connect(lambda msg: on_emit(self, msg))

            runnable = TaskRunnable(func, args, kwargs, signals)
            thread_pool.start(runnable)

            # Debug Submit Info (optional)
            # print(f"🚀 Submitted: {func.__name__}")
            # print(f"📊 Pool after submit: {thread_pool.activeThreadCount()}")
        return wrapper

    return decorator if _func is None else decorator(_func)
