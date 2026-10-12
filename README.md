# Ramos Scientific Calculator

A native **CLI, REPL and desktop scientific calculator**, written in Ramos.
The same expression engine powers both interfaces on Linux x64 and Windows x64.
Targets **Ramos 0.19.1**. Part of the
[Ramos project hub](https://github.com/zackmsa777-a11y/ramos/blob/main/docs/ecosystem.md).

## Install the compiler and run

Download the native compiler from the
[0.19.1 release](https://github.com/zackmsa777-a11y/ramos/releases/tag/v0.19.1):
`ramos-linux-x86_64` (rename to `ramos`, `chmod +x ramos`) or `ramos.exe`.
Optional Python 3 setup verifies the binary SHA-256:

```sh
python tools/compiler.py
```

Linux:

```sh
mkdir -p build
./ramos build calc.ramos -o build/calc
./build/calc 'sin(rad(30)) + sqrt(9) + log(100)'
./build/calc --repl
./ramos build gui.ramos -o build/calculator --gui
./build/calculator
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force build
.\ramos.exe build calc.ramos -o build/calc.exe
.\build\calc.exe 'sin(rad(30)) + sqrt(9) + log(100)'
.\build\calc.exe --repl
.\ramos.exe build gui.ramos -o build/calculator.exe --gui
.\build\calculator.exe
```

The first expression prints `5.5000000000`. No Python runtime is required by the
calculator. Linux GUI requires GTK3 and a display (`libgtk-3-0` on Ubuntu);
Windows uses native system controls. Cross-compile by adding `--target windows`
or `--target linux`; cross-compilation alone is not a platform execution test.

## Expressions

| Feature | Example |
| --- | --- |
| Arithmetic and parentheses | `2 + 3 * (4 - 1)` |
| Right-associative integer powers | `2^3^2` is 512; `-2^2` is -4 |
| Decimal/scientific input | `1e2 + 2.5E-1` |
| Constants | `pi`, `e`, `ans` (last successful result; initially zero) |
| Square root and magnitude | `sqrt(9)`, `abs(-7)` |
| Ranges | `min(1,2)`, `max(1,2)`, `clamp(8,0,5)` |
| Integer power | `pow(2,-3)` |
| Angle conversion | `rad(180)`, `deg(pi)` |
| Trigonometry in radians | `sin(pi/2)`, `cos(0)`, `tan(rad(45))` |
| Logarithms and exponential | `ln(e)`, `log(100)` (base 10), `exp(1)` |

Run with one quoted expression for clean numeric stdout; errors go to stderr
with exit 2 and a byte column. Run with no argument or `--repl` for a session;
`quit` exits. A bad expression leaves `ans` intact. The GUI has an expression
field, Evaluate/Clear, helper buttons and a keypad; resize adjusts the controls.
Clear resets the expression and retains `ans`.

## Deliberate limits

- Binary64 approximations, not arbitrary-precision mathematics. Results use
  fixed formatting with 10 decimal places; tiny values can display as zero.
- Each nonzero input/intermediate must have magnitude **1e-100 through 1e100**.
  Out-of-range values are reported, with headroom to avoid native overflow traps.
- Integer power exponents are **-64 through 64**; `0^0` is 1.
- Trig input is at most **1e6 radians** in magnitude. `tan` rejects points where
  the computed cosine has magnitude below **1e-12**. Values near poles lose accuracy.
- `ln` and `log` require positive arguments; `exp` accepts **[-230,230]**.
- At most **4096 UTF-8 bytes** per expression and **8 recursive expression
  levels**, including unary operators, arguments and right-hand subexpressions.
- Lowercase function/constants only; decimal literals need digits before and
  after a decimal point. No assignments, implicit multiplication or variables
  beyond `ans`. Invalid UTF-8 is governed by Ramos's checked string conversion.

Trig/ln/exp algorithms live in `src/science.ramos`; they are Ramos application
code, not compiler intrinsics or a hidden backend. Checks compare deterministic
samples with Python's independent `math` reference. Acceptance tolerances are
2e-9 absolute or 5e-12 relative after display rounding; this is test evidence on
the sampled inputs, not a certified error bound for every possible input.

## Develop and verify

```sh
python tools/check.py
```

Checks verify the pinned standard library, build CLI/GUI for both targets,
compare numerical results, test bad input and REPL recovery, and interact with
an actual native window. Linux needs `xvfb`, `xdotool`, `xclip` and GTK3 for the
GUI harness. Windows checks inspect result/error labels and `ans` recovery;
Linux checks exercise controls, errors, resize and normal close. CI runs both OSes.
Python is test/setup tooling only. See [ROADMAP.md](ROADMAP.md) for the next app features.

`stdlib/` is copied unchanged from the compiler commit in
[upstream.json](upstream.json). Read the
[Ramos Book](https://zackmsa777-a11y.github.io/ramos-docs/) for the supported language.

## Ramos family

[Source](https://github.com/zackmsa777-a11y/ramos) ·
[Book](https://github.com/zackmsa777-a11y/ramos-docs) ·
[Examples](https://github.com/zackmsa777-a11y/ramos-examples) ·
[Calculator](https://github.com/zackmsa777-a11y/ramos-calculator) ·
[Benchmarks](https://github.com/zackmsa777-a11y/ramos-benchmarks)

Browse the shared [Ramos topic](https://github.com/topics/ramos).
