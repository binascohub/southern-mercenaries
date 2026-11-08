"""Demogorgon da Floresta ("Demogorgon Rig", NO DONT EAT ME CASEOH (Ferris wheel) na Sketchfab, CC BY 4.0; arquivo trazido pelo autor do projeto): criatura
magra de ~2,4 m com a cabeça que abre em pétalas, 14 mil triângulos, esqueleto de 210 ossos, 11 texturas (40 MB) e 48 animações. É o visual do Tio Fungo
(fungus_uncle) na Floresta. Como o Cão da Vala (build_ditch_dog.py), o arquivo é editado direto no glTF (sem Blender):
 - ficam "idle" (Idle, os 6 primeiros segundos), "run" (Run), "attack" (Swing, o golpe de garra), "hit" (o começo do Stun) e "die" (o Stun inteiro: ele desaba);
 - as texturas vão a no máximo 1024 px; faixas paradas viram um quadro só, e o resto (as outras 43 animações e seus dados) sai do arquivo.
Vai para assets/models/monsters/demogorgon.glb (game/actors/monster_model.gd, família "demogorgon").
uso: python3 tools/assets/build_demogorgon.py <demogorgon_rig.glb> <saída.glb>"""
import array, io, json, struct, sys
from PIL import Image

src, out = sys.argv[1:3]
MAX_TEX = 1024
P = "demogorgon_ref_demogorgon_head1_skeleton|"
KEEP = {"idle": (P + "Idle", 0.0, 6.0), "run": (P + "Run", 0.0, None), "attack": (P + "Swing", 0.0, None),
        "hit": (P + "Stun", 0.0, 0.6), "die": (P + "Stun", 0.0, None)}

raw = open(src, "rb").read()
json_len = struct.unpack("<I", raw[12:16])[0]
gltf = json.loads(raw[20:20 + json_len])
bin_start = 20 + json_len + 8
binary = raw[bin_start:bin_start + struct.unpack("<I", raw[20 + json_len:24 + json_len])[0]]
COMPONENTS = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}
DTYPES = {5126: "f", 5123: "H", 5125: "I", 5121: "B", 5120: "b", 5122: "h"}


def view_bytes(index):
    v = gltf["bufferViews"][index]
    return binary[v.get("byteOffset", 0):v.get("byteOffset", 0) + v["byteLength"]]


def read_accessor(index):
    """Lista de linhas (cada uma com os componentes) de um acessor."""
    a = gltf["accessors"][index]
    v = gltf["bufferViews"][a["bufferView"]]
    n = COMPONENTS[a["type"]]
    code = DTYPES[a["componentType"]]
    size = struct.calcsize(code)
    stride = v.get("byteStride", n * size)
    base = v.get("byteOffset", 0) + a.get("byteOffset", 0)
    return [list(struct.unpack_from("<%d%s" % (n, code), binary, base + i * stride)) for i in range(a["count"])]


new_bin = bytearray()
new_views, new_accessors = [], []


def add_view(data, target=None):
    while len(new_bin) % 4:
        new_bin.append(0)
    view = {"buffer": 0, "byteOffset": len(new_bin), "byteLength": len(data)}
    if target:
        view["target"] = target
    new_bin.extend(data)
    new_views.append(view)
    return len(new_views) - 1


accessor_map, view_map = {}, {}


def keep_accessor(index):
    """Copia um acessor (e a vista dele) para o arquivo novo, uma vez só."""
    if index in accessor_map:
        return accessor_map[index]
    a = dict(gltf["accessors"][index])
    assert "sparse" not in a
    old_view = a["bufferView"]
    if old_view not in view_map:
        v = gltf["bufferViews"][old_view]
        view_map[old_view] = add_view(view_bytes(old_view), v.get("target"))
        if "byteStride" in v:
            new_views[view_map[old_view]]["byteStride"] = v["byteStride"]
    a["bufferView"] = view_map[old_view]
    new_accessors.append(a)
    accessor_map[index] = len(new_accessors) - 1
    return accessor_map[index]


def new_accessor(rows, component_type, kind):
    data = array.array(DTYPES[component_type], [x for row in rows for x in row])
    a = {"bufferView": add_view(data.tobytes()), "componentType": component_type, "count": len(rows), "type": kind}
    if kind == "SCALAR":
        a["min"], a["max"] = [min(r[0] for r in rows)], [max(r[0] for r in rows)]
    new_accessors.append(a)
    return len(new_accessors) - 1


for mesh in gltf["meshes"]:
    for prim in mesh["primitives"]:
        prim["attributes"] = {k: keep_accessor(v) for k, v in prim["attributes"].items()}
        if "indices" in prim:
            prim["indices"] = keep_accessor(prim["indices"])
        if "targets" in prim:
            prim["targets"] = [{k: keep_accessor(v) for k, v in t.items()} for t in prim["targets"]]
for skin in gltf.get("skins", []):
    if "inverseBindMatrices" in skin:
        skin["inverseBindMatrices"] = keep_accessor(skin["inverseBindMatrices"])

by_name = {a["name"]: a for a in gltf["animations"]}
animations = []
for new_name, (old_name, t0, t1) in KEEP.items():
    old = by_name[old_name]
    samplers, channels = [], []
    for ch in old["channels"]:
        s = old["samplers"][ch["sampler"]]
        assert s.get("interpolation", "LINEAR") != "CUBICSPLINE"
        times = [r[0] for r in read_accessor(s["input"])]
        values = read_accessor(s["output"])
        end = times[-1] if t1 is None else t1
        pick = [i for i, t in enumerate(times) if t0 - 1e-4 <= t <= end + 1e-4] or [min(range(len(times)), key=lambda i: abs(times[i] - t0))]
        kind = gltf["accessors"][s["output"]]["type"]
        samplers.append({"input": new_accessor([[times[i] - times[pick[0]]] for i in pick], 5126, "SCALAR"),
                         "output": new_accessor([values[i] for i in pick], 5126, kind), "interpolation": s.get("interpolation", "LINEAR")})
        channels.append({"sampler": len(samplers) - 1, "target": ch["target"]})
    animations.append({"name": new_name, "samplers": samplers, "channels": channels})
gltf["animations"] = animations

for image in gltf["images"]:
    picture = Image.open(io.BytesIO(view_bytes(image["bufferView"])))
    if max(picture.size) > MAX_TEX:
        picture = picture.resize((MAX_TEX * picture.size[0] // max(picture.size), MAX_TEX * picture.size[1] // max(picture.size)), Image.LANCZOS)
    data = io.BytesIO()
    if image.get("mimeType") == "image/jpeg":
        picture.convert("RGB").save(data, "JPEG", quality=85)
    else:
        picture.save(data, "PNG", optimize=True)
    image["bufferView"] = add_view(data.getvalue())

gltf["accessors"], gltf["bufferViews"] = new_accessors, new_views
while len(new_bin) % 4:
    new_bin.append(0)
gltf["buffers"] = [{"byteLength": len(new_bin)}]
text = json.dumps(gltf, separators=(",", ":")).encode()
text += b" " * (-len(text) % 4)
with open(out, "wb") as f:
    f.write(struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(text) + 8 + len(new_bin)))
    f.write(struct.pack("<II", len(text), 0x4E4F534A) + text)
    f.write(struct.pack("<II", len(new_bin), 0x004E4942) + bytes(new_bin))
print("animações", [(a["name"], len(a["channels"])) for a in animations], "tamanho", len(new_bin) // 1024, "KB")
