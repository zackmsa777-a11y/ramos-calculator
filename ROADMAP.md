# Calculator roadmap

Keep the application simple to use and measure before claiming speed.
The working foundation is a shared native expression engine, CLI/REPL and
resizable Windows/Linux GUI, with bounded scientific functions and recoverable errors.

Next, in order:

1. Adaptive/scientific output so small and large results remain readable;
   specify rounding and verify against independent decimal/binary references.
2. Error messages naming the failed operator/function and showing a caret;
   expression history with explicit capacity and file save/load status.
3. Backspace, keyboard shortcuts and a scientific-button panel, with native
   interaction tests on both desktop backends.
4. Inverse trigonometry and optional degree mode, with documented domains,
   approximation bounds and tests near singularities.
5. User variables, unit conversions and a small statistics worksheet, only
   after their semantics and persistence are defined.
6. Measure startup, parsing, numerical workloads and memory during long GUI
   sessions. Publish raw results rather than unmeasured speed comparisons.

These are app proposals, not features available in the current release.
Language/runtime improvements belong in the source repository; the app is
an end-to-end consumer that can expose their practical gaps.
