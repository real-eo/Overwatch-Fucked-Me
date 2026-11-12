I've extracted the source from the archive and am now reading the recognition, model, and startup code to see where the boot time goes.



Having read the code, I'd say a C++ rewrite would fix your boot time, but you can get most of that gain in Python for a fraction of the work. I haven't run the app (it's a Windows/Tk/TensorFlow app), so the numbers below are typical estimates, not measurements.



\## Where the boot time comes from



1\. \*\*Keras/TensorFlow loads before the window appears.\*\* `src/constants/model.py` calls `load\_model(...)` at import time, and `ui.py` imports `recognize`, which imports it. So the whole TensorFlow import plus the model build happens before `Tk()` is even created. That is usually several seconds, and it's the biggest cost.

2\. \*\*The PyInstaller build is `onefile` and bundles TensorFlow.\*\* Every launch unpacks the bundle (hundreds of MB with TF) to a temp folder. `upx=True` adds decompression time and tends to trigger antivirus scans.

3\. \*\*162 PNG decodes at startup.\*\* `\_portraits.py` builds three `PhotoImage` sets (3×, 4×, 6× subsample) for every hero. Each one decodes the full-size PNG and then shrinks it.



\## Recognition speed



\- `keras\_model.h5` is about 2.4 MB, takes 224×224 input, and uses `/127 − 1` normalization. That looks like a Teachable Machine (MobileNet-style) export. A model that small should run in a few milliseconds on a CPU.

\- `recognize()` calls `MODEL.predict()` five times, once per enemy, and each call has a lot of Keras overhead. One batched call, or calling `MODEL(batch, training=False)` directly, would likely cut that from roughly 100–300 ms to about 10–30 ms.

\- The first call also pays a one-time warm-up cost, so your first hotkey press is slower than the rest.

\- Crops are written to disk as PNGs and read straight back. That costs little, but it's unnecessary.

\- Recognition already runs in its own thread, so the Tk UI shouldn't freeze during it. For the UI, a C++ rewrite wouldn't buy you much.



\## What I'd do first



1\. \*\*Convert the model to ONNX and use `onnxruntime`.\*\* Do the conversion once, offline with `tf2onnx`, then ship only ONNX Runtime. It's about 15–30 MB against 500 MB+ for TF, and it imports in a fraction of a second. This is the biggest single win.

2\. \*\*Load the model in a background thread\*\* after the window shows, and run one dummy inference to warm it up. The UI then appears almost immediately.

3\. \*\*Batch the five crops\*\* into one `(5, 224, 224, 3)` array, keep them in memory, and drop the disk round-trip.

4\. \*\*Switch PyInstaller to `onedir` and set `upx=False`.\*\* This removes the per-launch unpacking.

5\. \*\*Pre-bake the portraits\*\* into 3×, 4×, and 6× thumbnails (or one sprite sheet) so startup doesn't decode and subsample 162 big PNGs.



Together, I'd expect boot time to drop from something like 5–15 s to roughly 1 s, and recognition from a few hundred ms to tens of ms.



\## What C++ would add on top



A C++ version would use ONNX Runtime (or OpenVINO) with Qt, Dear ImGui, or Win32 for the UI, and GDI/DXGI for screen capture. It could realistically start in 0.2–0.3 s and be a single small EXE. Against an optimized Python build, though, you'd be saving maybe a second of startup, and you'd have to reimplement the layout code, hotkeys, config handling, and counters loading. The scraper and counters-generation scripts would stay in Python regardless.



I'd do the Python changes first. If startup still isn't fast enough, the ONNX model and the batching logic carry over to C++ unchanged, so none of that work is wasted.



\## How to check



\- `python -X importtime main.py 2> imports.txt` shows what the import time is spent on. I expect `keras`/`tensorflow` at the top.

\- Put `time.perf\_counter()` around `createPhotoImages()` and around the five `predict` calls to confirm the portrait and inference costs.



I can sketch the ONNX conversion and the lazy-loading and batching changes against your actual files if you'd like.

