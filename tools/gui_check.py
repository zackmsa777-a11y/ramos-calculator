"""Test native controls. This Python harness is never an app runtime."""
import ctypes as C
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

binary = sys.argv[1]
test_env = os.environ.copy()
if platform.system() == "Linux":
    # This isolated desktop test does not exercise accessibility services.
    # Disable only that optional bridge; unexpected stderr still fails.
    test_env["NO_AT_BRIDGE"] = "1"
process = subprocess.Popen([binary], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=test_env)

def wait(predicate, label):
    end = time.monotonic() + 20
    while time.monotonic() < end:
        value = predicate()
        if value:
            return value
        assert process.poll() is None, (label, process.communicate())
        time.sleep(.05)
    raise AssertionError("Timed out: " + label)

try:
    if platform.system() == "Windows":
        from ctypes import wintypes as W
        user = C.WinDLL("user32", use_last_error=True)
        signatures = {
            "EnumWindows": (W.BOOL, [C.c_void_p, W.LPARAM]),
            "GetWindowThreadProcessId": (W.DWORD, [W.HWND, C.POINTER(W.DWORD)]),
            "GetDlgItem": (W.HWND, [W.HWND, C.c_int]),
            "SendMessageW": (W.LPARAM, [W.HWND, W.UINT, W.WPARAM, W.LPARAM]),
            "PostMessageW": (W.BOOL, [W.HWND, W.UINT, W.WPARAM, W.LPARAM]),
            "SetWindowPos": (W.BOOL, [W.HWND, W.HWND, C.c_int, C.c_int, C.c_int, C.c_int, W.UINT]),
        }
        for name, (result, args) in signatures.items():
            fn = getattr(user, name)
            fn.restype, fn.argtypes = result, args

        def find():
            found = []
            @C.WINFUNCTYPE(W.BOOL, W.HWND, W.LPARAM)
            def callback(window, unused):
                pid = W.DWORD()
                user.GetWindowThreadProcessId(window, C.byref(pid))
                if pid.value == process.pid:
                    found.append(window)
                return True
            user.EnumWindows(callback, 0)
            return found[0] if found else None

        window = wait(find, "calculator window")
        def control(number):
            return wait(lambda: user.GetDlgItem(window, number), "control " + str(number))
        def text(number):
            raw = C.create_unicode_buffer(32768)
            user.SendMessageW(control(number), 0xD, len(raw), C.addressof(raw))
            return raw.value
        def set_expression(value):
            raw = C.create_unicode_buffer(value)
            assert user.SendMessageW(control(2), 0xC, 0, C.addressof(raw))
        def click(number):
            assert user.PostMessageW(control(number), 0xF5, 0, 0)
        set_expression("sin(rad(30))+sqrt(9)")
        click(5)
        wait(lambda: text(3) == "Result: 3.5", "scientific result")
        set_expression("("*63+"1"+")"*63)
        click(5)
        wait(lambda: text(3) == "Result: 1", "deep nesting result")
        set_expression("("*64+"1"+")"*64)
        click(5)
        wait(lambda: "nesting limit" in text(4), "recoverable nesting error")
        set_expression("sin(rad(30))+sqrt(9)")
        click(5)
        wait(lambda: text(3) == "Result: 3.5", "recovery after nesting error")
        set_expression("1/0")
        click(5)
        wait(lambda: "byte column" in text(4), "recoverable division error")
        assert text(3) == "Result: 3.5"
        set_expression("ans*2")
        click(5)
        wait(lambda: text(3) == "Result: 7", "ans after error")
        set_expression("1e-100")
        click(5)
        wait(lambda: text(3) == "Result: 1e-100", "tiny scientific display")
        set_expression("1/0")
        click(5)
        wait(lambda: "byte column" in text(4), "tiny result preserved after error")
        assert text(3) == "Result: 1e-100"
        set_expression("ans*2")
        click(5)
        wait(lambda: text(3) == "Result: 2e-100", "tiny ans after error")
        set_expression("1e100")
        click(5)
        wait(lambda: text(3) == "Result: 1e+100", "large scientific display")
        click(6)
        wait(lambda: "Cleared" in text(4), "clear")
        assert text(2) == ""
        click(16)
        wait(lambda: text(2) == "7", "keypad")
        user.SetWindowPos(window, None, 0, 0, 720, 620, 0x6)
        time.sleep(.2)
        user.PostMessageW(window, 0x10, 0, 0)
    else:
        # GTK controls are exercised on an isolated Xvfb display. CLI tests
        # prove engine results; Windows checks additionally inspect labels.
        def command(*args):
            return subprocess.check_output(["xdotool", *map(str, args)], stderr=subprocess.DEVNULL, timeout=5)
        def find():
            try:
                return command("search", "--onlyvisible", "--name", "^Ramos Scientific Calculator$").splitlines()[0].decode()
            except (subprocess.CalledProcessError, IndexError):
                return None
        window = wait(find, "GTK calculator window")
        def click(x, y):
            command("windowfocus", window, "mousemove", "--window", window, x, y, "click", "1")
            time.sleep(.15)
        def paste(value):
            click(150, 64)
            command("key", "ctrl+a")
            subprocess.run(["xclip", "-selection", "clipboard"], input=value.encode(),
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            command("key", "ctrl+v")
            time.sleep(.2)
        for expression in ["("*63+"1"+")"*63, "("*64+"1"+")"*64,
                           "sin(rad(30))+sqrt(9)", "1/0", "ans*2",
                           "1e-100", "1/0", "ans*2", "1e100"]:
            paste(expression)
            click(60, 192)
            assert process.poll() is None, process.communicate()
        click(160, 192)  # clear
        click(60, 250)   # keypad 7
        command("windowsize", window, 720, 620)
        time.sleep(.3)
        output = Path(__file__).resolve().parents[1] / "build" / "gui-smoke.png"
        # Optional screenshot for local review; ImageMagick is not required.
        import shutil
        if shutil.which("import"):
            subprocess.run(["import", "-window", window, str(output)], check=True, timeout=10)
        # Request normal WM_DELETE_WINDOW without needing a window manager.
        class Client(C.Structure):
            _fields_ = [("type", C.c_int), ("serial", C.c_ulong), ("send_event", C.c_int),
                        ("display", C.c_void_p), ("window", C.c_ulong), ("message_type", C.c_ulong),
                        ("format", C.c_int), ("data", C.c_long * 5)]
        class Event(C.Union):
            _fields_ = [("client", Client), ("pad", C.c_long * 24)]
        x = C.CDLL("libX11.so.6")
        for name, result, args in [
            ("XOpenDisplay", C.c_void_p, [C.c_char_p]),
            ("XInternAtom", C.c_ulong, [C.c_void_p, C.c_char_p, C.c_int]),
            ("XSendEvent", C.c_int, [C.c_void_p, C.c_ulong, C.c_int, C.c_long, C.POINTER(Event)]),
            ("XFlush", C.c_int, [C.c_void_p]),
            ("XCloseDisplay", C.c_int, [C.c_void_p]),
        ]:
            fn = getattr(x, name)
            fn.restype, fn.argtypes = result, args
        display = x.XOpenDisplay(os.environ["DISPLAY"].encode())
        assert display
        event = Event()
        event.client.type, event.client.display, event.client.window = 33, display, int(window)
        event.client.message_type = x.XInternAtom(display, b"WM_PROTOCOLS", 0)
        event.client.format = 32
        event.client.data[0] = x.XInternAtom(display, b"WM_DELETE_WINDOW", 0)
        x.XSendEvent(display, int(window), 0, 0, C.byref(event))
        x.XFlush(display)
        x.XCloseDisplay(display)
    out, err = process.communicate(timeout=10)
    assert process.returncode == 0 and not err, (process.returncode, out, err)
    print("Native calculator GUI interaction, recovery, resize and close passed")
finally:
    if process.poll() is None:
        process.kill()
        process.communicate()
