import openpyxl, json, re, sys
import argparse
ap=argparse.ArgumentParser();ap.add_argument('grades');ap.add_argument('enroll');ap.add_argument('out');args=ap.parse_args()
A=openpyxl.load_workbook(args.grades,data_only=True)
B=openpyxl.load_workbook(args.enroll,data_only=True)
def clean(k):
    k=str(k or '').strip()
    k=re.sub(r'^\d+_','',k); k=re.sub(r'_\(.*수정\)$','',k)
    k=k.replace('윤리적인 실천','윤리적 실천').replace('MY GPTer','My GPTer').replace('AI 기반 문서','AI기반 문서').replace('ESG!','ESG !')
    return re.sub(r'\s+',' ',k).strip()
def num(v):
    try: return round(float(v),1)
    except: return None
recs=[]; seen=set()
def add(r):
    key=(r['s'],r['u'],r['id'],r['k'],r['g'])
    if key in seen: return
    seen.add(key); recs.append(r)
for r in list(A['2025-1학기(메타버시티)'].iter_rows(values_only=True))[1:]:
    if not r[1] or not r[4]: continue
    add(dict(s='2025-1',u=r[1],n=r[4],id=str(r[7] or ''),a=num(r[27]),h=num(r[28]),e=None,t=num(r[29]),c='수료' if r[30]=='P' else '미수료',k=clean(r[3]),g='교과'))
for r in list(A['2025-2학기'].iter_rows(values_only=True))[1:]:
    if not r[0] or not r[1]: continue
    add(dict(s='2025-2',u=r[0],n=r[1],id=str(r[2]),a=num(r[20]),h=num(r[21]),e=None,t=num(r[22]),c=r[23],k=clean(r[24]),g='교과'))
for r in list(A['2026-1학기'].iter_rows(values_only=True))[1:]:
    if not r[1] or not r[2] or not r[26]: continue
    add(dict(s='2026-1',u=r[1],n=r[2],id=str(r[3]),a=num(r[21]),h=num(r[22]),e=num(r[23]),t=num(r[24]),c=r[25],k=clean(r[26]),g='교과'))
for sh,g in [('전체수강신청','교과'),('전체수강신청(비교과)','비교과')]:
    for r in list(B[sh].iter_rows(values_only=True))[1:]:
        if not r[1] or not r[3]: continue
        add(dict(s='2026-2',u=r[1],n=r[3],id=str(r[2]),a=None,h=None,e=None,t=None,c='수강중',k=clean(r[7]),g=g))
cancels=[dict(s='2026-2',u=r[1],n=r[3],id=str(r[2]),k=clean(r[7])) for r in list(B['수강취소(확인)'].iter_rows(values_only=True))[1:] if r[1] and r[3]]
leads=[]
for r in list(B['과정책임'].iter_rows(values_only=True))[1:]:
    if not r[1] or r[1]=='합계': continue
    weeks=[i+1 for i in range(14) if str(r[7+i] or '').strip().lower()=='o']
    leads.append(dict(k=clean(r[1]),ban=r[3] or 1,fee=r[4] or 0,dev=r[5] or 0,rep=r[6] or 0,weeks=weeks,lead=r[22] or ''))
dup=sum(1 for _ in recs)
out=dict(records=recs,cancels=cancels,meta={'2026-2':{'courses':leads}},built=__import__('datetime').datetime.now(__import__('datetime').timezone(__import__('datetime').timedelta(hours=9))).strftime('%Y-%m-%d'))
json.dump(out,open(args.out,'w'),ensure_ascii=False,separators=(',',':'))
import collections as C
print(C.Counter((r['s'],r['g']) for r in recs)); print(len(cancels),len(leads))
print(sorted(set(r['k'] for r in recs)))
