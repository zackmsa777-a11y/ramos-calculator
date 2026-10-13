# Calculator roadmap

Keep the application simple to use and measure before claiming speed.
The working foundation is a shared native expression engine, CLI/REPL and
resizable Windows/Linux GUI, with bounded scientific functions and recoverable errors.

Implemented with Ramos 0.24: exact compact/scientific output preserves tiny
values, with independent decimal references and 17-digit binary64 round trips.
CLI, REPL and GUI use the same formatter.

Next, in order:

1. Error messages naming the failed operator/function and showing a caret;
   expression history with explicit capacity and file save/load status.
2. Backspace, keyboard shortcuts and a scientific-button panel, with native
   interaction tests on both desktop backends.
3. Inverse trigonometry and optional degree mode, with documented domains,
   approximation bounds and tests near singularities.
4. User variables, unit conversions and a small statistics worksheet, only
   after their semantics and persistence are defined.
5. Measure startup, parsing, numerical workloads and memory during long GUI
   sessions. Publish raw results rather than unmeasured speed comparisons.

These are app proposals, not features available in the current release.
Language/runtime improvements belong in the source repository; the app is
an end-to-end consumer that can expose their practical gaps.
