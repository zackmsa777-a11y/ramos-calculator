"""Independent numerical, malformed-input, REPL and native desktop checks."""
from pathlib import Path
import math
import platform
import random
import subprocess
import sys
from compiler import install
from provenance import check_sources
ROOT = Path(__file__).resolve().parents[1]
check_sources(ROOT)
compiler = install()
BUILD = ROOT / "build"
BUILD.mkdir(exist_ok=True)
for target, suffix in [("linux", ""), ("windows", ".exe")]:
    for source, name in [("calc.ramos", "calc"), ("gui.ramos", "calculator")]:
        cmd = [str(compiler), "build", str(ROOT/source), "-o", str(BUILD/(name+suffix)),
               "--target", target, "--force"]
        if name == "calculator": cmd.append("--gui")
        subprocess.run(cmd, check=True, cwd=ROOT)
windows = platform.system() == "Windows"
binary = str(BUILD / ("calc.exe" if windows else "calc"))
count = 0
def numeric(expression, expected, relative=5e-12, absolute=2e-9):
    global count
    p = subprocess.run([binary, expression], capture_output=True, timeout=10)
    assert p.returncode == 0, (expression, p.stderr)
    assert not p.stderr, (expression, p.stderr)
    value = float(p.stdout)
    assert math.isclose(value, expected, rel_tol=relative, abs_tol=absolute), (expression, value, expected)
    count += 1
for expression, expected in [("sqrt(9)+2^3",11),("-2^2",-4),("2^3^2",512),
    ("2^-3",.125),("(-2)^2",4),("min(7,2)+max(3,9)",11),("clamp(8,0,5)",5),
    ("abs(-7)",7),("pow(3,-2)",1/9),("deg(pi)",180),("rad(180)",math.pi),
    ("sin(rad(30))+log(100)+ln(e)",3.5),("0^0",1),("1e2 + 2.5E-1",100.25),
    ("sqrt(max(4,9))",3),(" 2 + 3 * (4 - 1) ",11),("1e100/1e100",1),
    ("1e-100/1e-100",1),("exp(230)",math.exp(230)),("ln(1e-100)",math.log(1e-100))]:
    numeric(expression, expected)
rng = random.Random(191)
for _ in range(80):
    angle = rng.uniform(-1e6,1e6)
    numeric(f"sin({angle:.14g})", math.sin(float(f"{angle:.14g}")))
    numeric(f"cos({angle:.14g})", math.cos(float(f"{angle:.14g}")))
    x = rng.uniform(-230,230)
    numeric(f"exp({x:.14g})", math.exp(float(f"{x:.14g}")))
    value = 10 ** rng.uniform(-100,100)
    value = float(f"{value:.14g}")
    numeric(f"ln({value:.14g})", math.log(value))
    numeric(f"log({value:.14g})", math.log10(value))
for angle in [-1,-.5,0,.5,1]: numeric(f"tan({angle})",math.tan(angle))
bad = ["", "1+", "(1+2", "1 2", "sqrt(-1)", "1/0", "0^-1", "pow(2,0.5)",
       "2^65", "clamp(1,5,0)", "min(1)", "sqrt()", "max(1,2,3,4)", "missing", "pi()",
       "sin(1000001)", "tan(pi/2)", "ln(0)", "log(-1)", "exp(231)", "exp(-231)",
       "1e101", "1e-101", "1e-400", "1e100*1e100", "1e-100*1e-100", "1e100/1e-100",
       "1e-100/1e100", ".5", "1.", "2^^3", "2+🌍", "1e+", "0x10", "1,2",
       "("*9+"1"+")"*9, "1"*4097]
for expression in bad:
    p = subprocess.run([binary, expression], capture_output=True, timeout=10)
    assert p.returncode == 2 and b"byte column" in p.stderr, (expression[:40],p.returncode,p.stderr)
    assert b"runtime error" not in p.stderr.lower(), (expression[:40],p.stderr)
    count += 1
p = subprocess.run([binary,"--repl"],input=b"2+3\n1/0\nans*2\nquit\n",capture_output=True,timeout=10)
assert p.returncode == 0 and b"5.0000000000" in p.stdout and b"10.0000000000" in p.stdout
assert b"byte column" in p.stderr
count += 1
print(f"{count} numerical/error/REPL checks passed", flush=True)
if windows:
    subprocess.run([sys.executable,str(ROOT/"tools/gui_check.py"),str(BUILD/"calculator.exe")],check=True)
else:
    subprocess.run(["xvfb-run","-a",sys.executable,str(ROOT/"tools/gui_check.py"),str(BUILD/"calculator")],check=True)
