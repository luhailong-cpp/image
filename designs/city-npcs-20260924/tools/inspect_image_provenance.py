"""Read PNG C2PA action metadata without validating signatures or inferring backend IDs."""
from __future__ import annotations
import argparse, hashlib, json, struct, zlib
from pathlib import Path

class Cbor:
    def __init__(self, data):
        self.data, self.pos = data, 0
    def take(self, n):
        if n < 0 or self.pos+n > len(self.data):
            raise ValueError("truncated CBOR")
        result = self.data[self.pos:self.pos+n]
        self.pos += n
        return result
    def read(self, depth=0):
        if depth > 64:
            raise ValueError("CBOR nesting limit")
        first = self.take(1)[0]
        kind, ai = first >> 5, first & 31
        if ai < 24: n = ai
        elif ai in (24,25,26,27): n = int.from_bytes(self.take(1 << (ai-24)), "big")
        else: raise ValueError("unsupported indefinite/reserved CBOR")
        if kind == 0: return n
        if kind == 1: return -1-n
        if kind == 2: return {"bytes_hex": self.take(n).hex()}
        if kind == 3: return self.take(n).decode("utf-8")
        if kind == 4: return [self.read(depth+1) for _ in range(n)]
        if kind == 5:
            result = {}
            for _ in range(n):
                key = self.read(depth+1)
                value = self.read(depth+1)
                result[str(key)] = value
            return result
        if kind == 6: return {"cbor_tag":n, "value":self.read(depth+1)}
        if kind == 7:
            if ai == 20: return False
            if ai == 21: return True
            if ai in (22,23): return None
            if ai in (25,26,27):
                fmt = {25:">e",26:">f",27:">d"}[ai]
                return struct.unpack(fmt,n.to_bytes(1 << (ai-24),"big"))[0]
        raise ValueError("unsupported CBOR item")

def boxes(data):
    pos=0
    while pos < len(data):
        if len(data)-pos < 8: raise ValueError("truncated JUMBF box")
        size,kind = struct.unpack(">I4s",data[pos:pos+8])
        header=8
        if size == 1:
            if len(data)-pos < 16: raise ValueError("truncated extended JUMBF")
            size = struct.unpack(">Q",data[pos+8:pos+16])[0]
            header=16
        if size == 0: size=len(data)-pos
        if size < header or pos+size>len(data): raise ValueError("invalid JUMBF length")
        yield kind,data[pos+header:pos+size]
        pos+=size

def label_from_description(data):
    if len(data)<17: return ""
    if data[16]&2:
        return data[17:].split(b"\0",1)[0].decode("utf-8","replace")
    return ""

def inspect_jumbf(data,path=(),depth=0):
    if depth>32: raise ValueError("JUMBF nesting limit")
    entries=list(boxes(data))
    label=next((label_from_description(value) for kind,value in entries if kind==b"jumd"),"")
    current=path+(label,) if label else path
    found=[]
    for kind,value in entries:
        if kind==b"jumb":
            found.extend(inspect_jumbf(value,current,depth+1))
        elif kind==b"cbor" and label.startswith("c2pa.actions"):
            reader=Cbor(value)
            decoded=reader.read()
            if reader.pos != len(value): raise ValueError("trailing action CBOR")
            found.append({"jumbf_path":list(current),"assertion":decoded})
    return found

def inspect_image(path):
    path=Path(path).resolve()
    raw=path.read_bytes()
    if raw[:8] != b"\x89PNG\r\n\x1a\n": raise ValueError("PNG required")
    pos=8
    assertions=[]
    dims=None
    c2pa_chunks=0
    ended=False
    while pos<len(raw):
        if pos+12>len(raw): raise ValueError("truncated PNG")
        size,kind=struct.unpack(">I4s",raw[pos:pos+8])
        if pos+12+size>len(raw): raise ValueError("truncated PNG chunk")
        value=raw[pos+8:pos+8+size]
        crc=struct.unpack(">I",raw[pos+8+size:pos+12+size])[0]
        if (zlib.crc32(kind+value)&0xffffffff)!=crc: raise ValueError("PNG CRC mismatch")
        if kind==b"IHDR": dims=list(struct.unpack(">II",value[:8]))
        if kind==b"caBX":
            c2pa_chunks+=1
            assertions.extend(inspect_jumbf(value))
        pos+=12+size
        if kind==b"IEND":
            ended=True
            if pos != len(raw): raise ValueError("trailing PNG data")
            break
    if not ended or dims is None: raise ValueError("invalid PNG")
    actions=[]
    for row in assertions:
        assertion=row["assertion"]
        for action in assertion.get("actions",[]):
            agent=action.get("softwareAgent")
            if agent is None and "softwareAgentIndex" in action:
                agents=assertion.get("softwareAgents",[])
                index=action["softwareAgentIndex"]
                if isinstance(index,int) and 0<=index<len(agents): agent=agents[index]
            actions.append({"jumbf_path":row["jumbf_path"],"action":action.get("action"),
                "when":action.get("when"),"software_agent":agent,
                "digital_source_type":action.get("digitalSourceType")})
    created=[row for row in actions if row["action"]=="c2pa.created"]
    return {"path":str(path),"sha256":hashlib.sha256(raw).hexdigest(),
        "native_size":dims,"png_crc_valid":True,"c2pa_chunk_count":c2pa_chunks,
        "signature_verified":False,"metadata_only":True,
        "effective_backend_model":"not_exposed_by_builtin_tool",
        "interpretation":"Embedded software version is evidence, not API model locking or a verified C2PA signature.",
        "created_actions":created,"all_action_count":len(actions)}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images",nargs="+",type=Path)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    result={"schema":1,"images":[inspect_image(p) for p in args.images]}
    text=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open("x",encoding="utf-8") as f:f.write(text)
    print(text)
if __name__=="__main__": main()
