# usage: python3 inject.py data.json template.html out.html [public]
#   public : 게시용. 이름·아이디를 마스킹해서 넣고 실명은 넣지 않음 (보기 전용)
#   (없음) : 내부용. 실명을 넣고 화면에서 마스킹을 켜고 끌 수 있음
import json,sys,re,os
d=json.load(open(sys.argv[1])); public=len(sys.argv)>4 and sys.argv[4]=='public'
def mname(n):
    n=str(n); return n if len(n)<2 else (n[0]+'*' if len(n)==2 else n[0]+'*'*(len(n)-2)+n[-1])
def mid(i):
    i=str(i); m=re.match(r'^([A-Za-z]*)(\d{0,4})',i); keep=m.group(0) if m else ''
    keep=keep if len(keep)<len(i) else i[:max(1,len(i)-4)]
    return keep+'*'*(len(i)-len(keep))
recs=d['records']; univs=sorted(set(r['u'] for r in recs)); courses=sorted(set(r['k'] for r in recs)); status=['수료','미수료','수강중']
pid={}
for r in recs: pid.setdefault((r['u'],r['id']),len(pid))
N=(lambda x:mname(x)) if public else (lambda x:x); I=(lambda x:mid(x)) if public else (lambda x:x)
rows=[[r['s'],univs.index(r['u']),N(r['n']),I(r['id']),r['a'],r['h'],r['e'],r['t'],status.index(r['c']),courses.index(r['k']),1 if r['g']=='비교과' else 0,pid[(r['u'],r['id'])]] for r in recs]
cancels=[dict(c,n=N(c['n']),id=I(c['id'])) for c in d['cancels']]
# 기본자료(내부용 백업/내보내기 형식 {meta:{학기:{info,courses}}} 또는 {학기:{...}}) 병합
meta=dict(d['meta']); mp=os.environ.get('DASH_META')
if mp and os.path.exists(mp):
    m=json.load(open(mp)); m=m.get('meta',m)
    for s,v in m.items(): meta[s]={**meta.get(s,{}),**v}
# 설문 통계(샘플 보고서에서 추출한 survey.json {학기:{all,univ}}) 병합
sp=os.environ.get('DASH_SURVEY')
if sp and os.path.exists(sp):
    for s,v in json.load(open(sp)).items(): meta[s]={**meta.get(s,{}),'survey':v}
raw=dict(univs=univs,courses=courses,status=status,rows=rows,cancels=cancels,meta=meta,built=d['built'],public=public)
t=open(sys.argv[2]).read()
if public:  # 게시용 HTML에는 마스킹 버튼 자체를 넣지 않음
    t=re.sub(r'\n\s*<button class="btn" id="privBtn"[^\n]*</button>','',t)
t=t.replace('/*__DATA__*/null',json.dumps(raw,ensure_ascii=False,separators=(',',':')))
open(sys.argv[3],'w').write(t)
print('public(masked)' if public else 'internal(real names)', len(rows))
