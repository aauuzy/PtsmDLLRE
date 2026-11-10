import sys, math, hashlib, re
import pefile

path = sys.argv[1]
data = open(path, "rb").read()
pe = pefile.PE(data=data, fast_load=False)

print("== HEADER ==")
print("machine", hex(pe.FILE_HEADER.Machine))
print("timestamp", pe.FILE_HEADER.TimeDateStamp)
print("subsystem", pe.OPTIONAL_HEADER.Subsystem)
print("dll_characteristics", hex(pe.OPTIONAL_HEADER.DllCharacteristics))
print("entrypoint", hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint))
print("image_size", pe.OPTIONAL_HEADER.SizeOfImage)
print("file_size", len(data))

print("\n== SECTIONS ==")
end_of_last_raw = 0
for s in pe.sections:
    name = s.Name.rstrip(b"\x00").decode("latin1", "replace")
    print(f"{name:10} vsize={s.Misc_VirtualSize:>10} rawsize={s.SizeOfRawData:>10} "
          f"entropy={s.get_entropy():.2f} char={hex(s.Characteristics)}")
    end_of_last_raw = max(end_of_last_raw, s.PointerToRawData + s.SizeOfRawData)

overlay = len(data) - end_of_last_raw
print(f"\noverlay_offset={end_of_last_raw} overlay_size={overlay} "
      f"({overlay/1024/1024:.2f} MB)")

print("\n== IMPORTS (dll: count) ==")
if hasattr(pe, "DIRECTORY_ENTRY_IMPORT"):
    for e in pe.DIRECTORY_ENTRY_IMPORT:
        dll = e.dll.decode("latin1", "replace")
        print(f"{dll:22} {len(e.imports)}")

print("\n== RESOURCE TYPES ==")
if hasattr(pe, "DIRECTORY_ENTRY_RESOURCE"):
    for rt in pe.DIRECTORY_ENTRY_RESOURCE.entries:
        tid = rt.id if rt.id is not None else rt.name
        print("type", tid)
else:
    print("none")

print("\n== SECURITY DIR (Authenticode) ==")
sd = pe.OPTIONAL_HEADER.DATA_DIRECTORY[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_SECURITY"]]
print("virtualaddress(fileoffset)", sd.VirtualAddress, "size", sd.Size)

print("\n== VERSION INFO ==")
found = False
if hasattr(pe, "FileInfo"):
    for fi in pe.FileInfo:
        for e in fi:
            if hasattr(e, "StringTable"):
                for st in e.StringTable:
                    for k, v in st.entries.items():
                        print(k.decode(), "=", v.decode())
                        found = True
if not found:
    print("(no version string table)")

print("\n== FRAMEWORK FINGERPRINTS (count of marker in file) ==")
markers = [b"tauri", b"TAURI", b"WebView2", b"webview", b"Electron", b"electron",
           b"app.asar", b"node.dll", b"PyInstaller", b"_MEIPASS", b"V8",
           b"chrome", b"Chromium", b"NSIS", b"Nullsoft", b"rust", b"cargo",
           b"Roblox", b"luau", b"Luau", b"loadstring", b"hookfunction",
           b"hookmetamethod", b"RemoteEvent", b"FireServer", b"VMProtect",
           b"Themida"]
for m in markers:
    c = data.count(m)
    if c:
        print(f"{m.decode('latin1'):16} {c}")
