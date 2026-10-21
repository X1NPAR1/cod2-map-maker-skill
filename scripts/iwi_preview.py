# Usage (run inside <game>/main): python iwi_preview.py OUT_DIR material1 material2 ...
# Resolves each material's colour map (.iwi, DXT1/3/5 or raw) from the iwds and saves a PNG
# so you can LOOK at a texture before using it. Requires Pillow.
import zipfile,glob,struct,io,re
from PIL import Image
import sys
OUT=sys.argv[1] if len(sys.argv)>1 else './'
zs=[zipfile.ZipFile(f) for f in sorted(glob.glob('iw_*.iwd'))]
def bul(n):
    for z in reversed(zs):
        if n in z.NameToInfo: return z.read(n)
def dds(data,w,h,fourcc):
    hdr=struct.pack('<4sIIIIIII44sII4sIIIIIIIIII', b'DDS ',124,0x1007,h,w,0,0,1,bytes(44),32,4,fourcc,0,0,0,0,0,0x1000,0,0,0,0)
    return Image.open(io.BytesIO(hdr+data))
mats=sys.argv[2:] or ['stalingradwinter_door_wood01','stalingradwinter_door_wood02','mtl_caen_door_wood_01','mtl_caen_door_wood_02','mtl_caen_door_wood_03','mtl_door_wood','stalingrad_wd_door','v_door01','v_door02','v_door03','dawnville2_wood_door01','dawnville2_wood_door02','dawnville2_wood_door03','mtl_wood_door1','mtl_hill400_door_01','mtl_hill400_door_02','mtl_caen_door_01','mtl_caen_door_02']
for m in mats:
    b=bul('materials/'+m)
    names=[x.decode() for x in re.findall(rb'[a-z0-9_~&$#@!\-\.]{4,}',b)]
    img=None
    for nm in names:
        d=bul('images/'+nm+'.iwi')
        if d: img=nm;break
    if not d: print(m,'gorsel yok',names[:6]);continue
    fmt=d[4];w,h=struct.unpack_from('<HH',d,6)
    bs={0x0B:8,0x0C:16,0x0D:16}.get(fmt)
    if bs:
        sz=max(1,w//4)*max(1,h//4)*bs
        im=dds(d[-sz:],w,h,{0x0B:b'DXT1',0x0C:b'DXT3',0x0D:b'DXT5'}[fmt])
    elif fmt==1: im=Image.frombytes('RGBA',(w,h),d[-w*h*4:])
    elif fmt==2: im=Image.frombytes('RGB',(w,h),d[-w*h*3:])
    else: print(m,'fmt',fmt);continue
    im.convert('RGB').save(OUT+m+'.png'); print(m,img,w,h)
