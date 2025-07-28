#!/usr/bin/env python3
import os
import sys
import time
from time import sleep
import pandas as pd
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore    import Qt, QTimer, QUrl
from PyQt5.QtGui     import QTextCursor, QMouseEvent, QImage

# — Ensure your project root is on PYTHONPATH —
HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)
from components.description.editor import DescriptionEditor

# — Inline test definitions (14 total) —
TEST_CASES = [
    # Functional tests
    {"TestID":"TC1",  "Method":"load_content",        "Input":"",            "ExpectedPlain":"",     "Notes":"Empty HTML"},
    {"TestID":"TC2",  "Method":"load_content",        "Input":"<p>Hello</p>", "ExpectedPlain":"Hello","Notes":"Simple HTML"},
    {"TestID":"TC3",  "Method":"on_save",             
        "SetupHTML":"<b>Bold</b>", "ExpectSignal":"content_changed","Contains":"Bold","Notes":"Save emits HTML"},
    {"TestID":"TC4",  "Method":"detect_newline_reset","SetupText":"Line1\n",  "ExpectTimer":True,    "Notes":"Newline triggers"},
    {"TestID":"TC5",  "Method":"detect_newline_reset","SetupText":"Line1",    "ExpectTimer":False,   "Notes":"No newline"},
    {"TestID":"TC6",  "Method":"update_toolbar_state","SetupText":"Hello","ExpectSignal":"text_format_updated","Notes":"Plain-text update"},
    {"TestID":"TC7",  "Method":"update_toolbar_state","SetupText":"Hi","SelectAll":True,"ExpectSignal":"text_format_updated","Notes":"Selection update"},
    {"TestID":"TC8",  "Method":"eventFilter",         "Image":False,           "ExpectReturn":False,  "Notes":"Click non-image"},
    {"TestID":"TC9",  "Method":"eventFilter",         "Image":True,            "ExpectReturn":True,   "Notes":"Click image"},
    {"TestID":"TC10", "Method":"debounce",            "RapidCalls":5,          "ExpectCount":1,       "Notes":"Debounce"},

    # Stress / performance tests
    {"TestID":"P1",  "Method":"perf_load",           "LineCount":1000,       "MaxMs":100,  "Notes":"Load 1 000 lines"},
    {"TestID":"P2",  "Method":"perf_load",           "LineCount":2000,       "MaxMs":200,  "Notes":"Load 2 000 lines"},
    {"TestID":"P3",  "Method":"perf_save",           "LineCount":2000,       "MaxMs":150,  "Notes":"Save after 2 000 lines"},
    {"TestID":"P4",  "Method":"perf_insert_images",  "ImageCount":100,       "MaxMs":100,  "Notes":"Insert 100 images"},
]

def _time_ms(fn):
    """Measure milliseconds taken by fn()."""
    t0 = time.perf_counter()
    fn()
    return (time.perf_counter() - t0) * 1000

def simulate_event(editor, tc, app):
    method = tc["Method"]
    passed = False

    # — Functional tests —
    if method == "load_content":
        editor.load_content(tc["Input"]); app.processEvents()
        passed = (editor.text_edit.toPlainText() == tc["ExpectedPlain"])

    elif method == "on_save":
        editor.load_content(tc["SetupHTML"]); app.processEvents()
        cap=[]; getattr(editor, tc["ExpectSignal"]).connect(cap.append)
        editor.on_save(); app.processEvents()
        passed = bool(cap) and (tc["Contains"] in cap[0])

    elif method == "detect_newline_reset":
        fired=[]; orig=editor.reset_format_on_newline
        editor.reset_format_on_newline=lambda: fired.append(True)
        editor.text_edit.setPlainText(tc["SetupText"]); app.processEvents()
        editor.detect_newline_reset()
        for _ in range(5): sleep(0.01); app.processEvents()
        editor.reset_format_on_newline=orig
        passed = bool(fired) if tc["ExpectTimer"] else not fired

    elif method == "update_toolbar_state":
        editor.text_edit.setPlainText(tc["SetupText"])
        if tc.get("SelectAll"):
            cur=editor.text_edit.textCursor(); cur.select(QTextCursor.Document)
            editor.text_edit.setTextCursor(cur)
        app.processEvents()
        cap=[]; getattr(editor, tc["ExpectSignal"]).connect(lambda *a: cap.append(a))
        editor.update_toolbar_state(); app.processEvents()
        passed = bool(cap)

    elif method == "eventFilter":
        viewport=editor.text_edit.viewport(); center=viewport.rect().center()
        if tc["Image"]:
            editor.text_edit.insertHtml('<img src=""/>'); app.processEvents()
        ev=QMouseEvent(QMouseEvent.MouseButtonDblClick, center, Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
        res=editor.eventFilter(viewport, ev)
        passed = (res == tc["ExpectReturn"])

    elif method == "debounce":
        calls=[]; editor.update_timer.timeout.connect(lambda: calls.append(True))
        for _ in range(tc["RapidCalls"]): editor.on_selection_change(); app.processEvents(); sleep(0.01)
        for _ in range(30): sleep(0.01); app.processEvents()
        passed = (len(calls)==tc["ExpectCount"])

    # — Performance tests —
    elif method == "perf_load":
        lines=["Line"]*tc["LineCount"]
        def action():
            editor.load_content("\n".join(lines)); app.processEvents()
        ms=_time_ms(action)
        passed = (ms <= tc["MaxMs"])

    elif method == "perf_save":
        lines=["Line"]*tc["LineCount"]
        editor.load_content("\n".join(lines)); app.processEvents()
        def action():
            editor.on_save(); app.processEvents()
        ms=_time_ms(action)
        passed = (ms <= tc["MaxMs"])

    elif method == "perf_insert_images":
        def action():
            for i in range(tc["ImageCount"]):
                img=QImage(1, 1, QImage.Format_ARGB32)
                editor.text_edit.document().addResource(
                    editor.text_edit.document().ImageResource,
                    QUrl(f"img_{i}"),
                    img
                )
            app.processEvents()
        ms=_time_ms(action)
        passed = (ms <= tc["MaxMs"])

    return passed

def main():
    app = QApplication.instance() or QApplication(sys.argv)
    editor = DescriptionEditor("PERF TEST")

    results=[]
    for tc in TEST_CASES:
        ok = simulate_event(editor, tc, app)
        print(f"{tc['TestID']}: {'PASS' if ok else 'FAIL'} -- {tc['Notes']}")
        results.append({"TestID":tc["TestID"], "Pass":ok, "Notes":tc["Notes"]})

    passed=sum(r["Pass"] for r in results); total=len(results)
    print(f"\nSummary: {passed}/{total} passed.")

    pd.DataFrame(results).to_excel("test_results_description_editor_full.xlsx", index=False)

if __name__=="__main__":
    main()
