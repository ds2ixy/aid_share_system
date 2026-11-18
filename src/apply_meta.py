# 내부용 「게시용에 반영」 요청 JSON → meta.json 병합
# 사용: python3 -I src/apply_meta.py <요청.json>   (저장소 루트에서)
import json, sys, os, datetime
req = json.load(open(sys.argv[1]))
src = req.get('meta', req)
BAD = {'n','id','name','phone','email','이름','아이디','휴대폰','이메일'}
def has_pii(o):
    if isinstance(o, dict): return any(k in BAD and isinstance(v,str) for k,v in o.items()) or any(has_pii(v) for v in o.values())
    if isinstance(o, list): return any(has_pii(v) for v in o)
    return False
if has_pii(src): sys.exit('개인정보로 보이는 필드가 있어 반영하지 않았습니다')
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(root, 'meta.json')
cur = json.load(open(path)) if os.path.exists(path) else {'meta': {}}
meta = cur.get('meta', cur)
for sem, v in src.items():
    meta[sem] = {**meta.get(sem, {}), **v}      # 학기 안에서 info / courses / survey 단위로 교체
out = {'updated': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'meta': meta}
json.dump(out, open(path, 'w'), ensure_ascii=False, indent=1)
print('반영:', ', '.join(f"{s}({'/'.join(v.keys())})" for s, v in src.items()))
