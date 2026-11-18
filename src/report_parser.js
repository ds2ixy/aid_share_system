/* 샘플 보고서(PDF/텍스트) → 설문 통계 추출기
   종합보고서: 전체 사전·사후(M·SD)·t, 만족도, 이수율
   대학별 보고서: 우리대학 vs 전체 참여대학 (부록 표) 또는 본문 표 */
var RP = (function(){
  var KA=['디지털 관련 지식','디지털 관련 태도'], DOM=['디지털시민윤리','디지털에티켓','디지털역량','디지털규범'];
  var SUB=['디지털 시민정체성','디지털 시민가치관','사회참여의식','자기관리','도덕적가치와 의무','사이버에티켓','개인정보 보호','커뮤니케이션','정보의 생산과 소비','비판적 사고','디지털능력','디지털 활용','법제도 인식','디지털 권리','사이버 범죄','사이버 폭력'];
  var SAT=['수업 주제와 내용','관련 분야 역량 향상지원','공유 LMS 활용 수업','추천 및 참여의향','총합'];
  var ALL=KA.concat(DOM,SUB);
  function nameRe(n){ return new RegExp(n.replace(/\s+/g,'').split('').map(function(c){return c.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')}).join('\\s*')); }
  var NUMRE=/-?\d*\.\d+\**|-?\d+\**/g;
  function numsOf(s){ return (s.match(NUMRE)||[]).map(function(x){return parseFloat(x.replace(/\*/g,''))}); }
  /* PDF에서 t값이 다음 줄로 밀리는 경우까지 처리. pair=true: 우리대학4+전체4 형식 */
  function findLine(lines,name,need,pair){
    var re=nameRe(name);
    for(var i=0;i<lines.length;i++){ var m=re.exec(lines[i]); if(!m) continue;
      var ns=numsOf(lines[i].slice(m.index+m[0].length));
      if(ns.length<need && i+1<lines.length){
        var nx=numsOf(lines[i+1].replace(/^[^\d-]*/,''));
        if(nx.length && nx.length<=2 && ns.length+nx.length>=need){
          if(pair && ns.length===6 && nx.length===2) ns=[ns[0],ns[1],ns[2],nx[0],ns[3],ns[4],ns[5],nx[1]];
          else ns=ns.concat(nx);
        }
      }
      if(ns.length>=need) return ns; }
    return null;
  }
  function satLine(lines,name,need){ return findLine(lines,name,need) || (name.indexOf('공유')>=0 ? findLine(lines,name.replace('공유','공동'),need) : null); }
  function comp(lines,need){
    for(var i=0;i<lines.length;i++){ var s=lines[i].trim(); if(s.indexOf('이수율')!==0) continue;
      var ns=(s.match(/\d+\.?\d*/g)||[]).map(Number); if(ns.length>=need) return ns; }
    return null;
  }
  function N(text){ var m=/\(N=\s*(\d+)\)/.exec(text); return m?+m[1]:null; }
  function parseTotal(text){
    var lines=text.split('\n'), out={N:N(text),items:{},sat:{}};
    ALL.forEach(function(n){ var v=findLine(lines,n,6); if(v&&v[0]>=1&&v[0]<=5) out.items[n]={pre:v[0],preSD:v[1],post:v[2],postSD:v[3],diff:v[4],t:v[5]}; });
    SAT.forEach(function(n){ var v=satLine(lines,n,3); if(v&&v[0]<=5) out.sat[n]={m:v[0],n:Math.round(v[1]),sd:v[2]}; });
    var c=comp(lines,3); if(c) out.comp={apply:c[0],done:c[1],rate:c[2]};
    return out;
  }
  function parseUniv(text){
    var lines=text.split('\n'), out={N:N(text),items:{},sat:{}}, all={items:{},sat:{}};
    var mm=/\[\s*부\s*록\s*\]/.exec(text), ap=mm?mm.index:-1; if(ap<0){ var re=/디지털\s*지식과\s*태도/g, x; while((x=re.exec(text))) ap=x.index; }
    var app=ap>=0?text.slice(ap).split('\n'):[];
    ALL.forEach(function(n){ var v=findLine(app,n,8,true); if(v&&v[0]>=1&&v[0]<=5){ out.items[n]={pre:v[0],post:v[1],diff:v[2],t:v[3]}; all.items[n]={pre:v[4],post:v[5],diff:v[6],t:v[7]}; } });
    if(Object.keys(out.items).length<10){ var alt={}; ALL.forEach(function(n){ var v=findLine(lines,n,5); if(v&&v[0]>=1&&v[0]<=5&&v[2]>=1&&v[2]<=5) alt[n]={pre:v[0],preSD:v[1],post:v[2],postSD:v[3],diff:v[4],t:v.length>5?v[5]:null}; });
      if(Object.keys(alt).length>Object.keys(out.items).length){ out.items=alt; all.items={}; } }
    SAT.forEach(function(n){ var v=satLine(lines,n,6);
      if(v&&v[0]<=5){ out.sat[n]={m:v[0],n:Math.round(v[1]),sd:v[2]}; all.sat[n]={m:v[3],n:Math.round(v[4]),sd:v[5]}; }
      else { v=satLine(lines,n,3); if(v&&v[0]<=5) out.sat[n]={m:v[0],n:Math.round(v[1]),sd:v[2]}; } });
    var s4=SAT.slice(0,4).filter(function(n){return out.sat[n]});
    if(!out.sat['총합']&&s4.length===4) out.sat['총합']={m:+(s4.reduce(function(a,n){return a+out.sat[n].m},0)/4).toFixed(2),n:out.sat[s4[0]].n,sd:null};
    if(!out.N&&s4.length) out.N=out.sat[s4[0]].n;
    var c=comp(lines,6)||comp(lines,3); if(c){ out.comp={apply:c[0],done:c[1],rate:c[2]}; if(c.length>=6) all.comp={apply:c[3],done:c[4],rate:c[5]}; }
    return {univ:out, all:all};
  }
  /* PDF 텍스트 조각 → 줄 (pdf.js getTextContent 결과) */
  function linesFromItems(items){
    var rows=[];
    items.forEach(function(it){ if(!it.str||!it.str.trim()) return; var y=Math.round(it.transform[5]), x=it.transform[4];
      var r=rows.find(function(r){return Math.abs(r.y-y)<=2}); if(!r){r={y:y,c:[]};rows.push(r);} r.c.push({x:x,s:it.str,w:it.width||0}); });
    rows.sort(function(a,b){return b.y-a.y});
    return rows.map(function(r){ r.c.sort(function(a,b){return a.x-b.x}); var out='',end=null;
      r.c.forEach(function(c){ if(end!==null) out+= (c.x-end>1.5?'  ':''); out+=c.s; end=c.x+c.w; }); return out; }).join('\n');
  }
  function isTotal(fileName,text){ return /종합/.test(fileName) || (/종합\s*(결과)?\s*보고서/.test(text.slice(0,400)) && !/대학별/.test(text.slice(0,400))); }
  return {parseTotal:parseTotal, parseUniv:parseUniv, linesFromItems:linesFromItems, isTotal:isTotal};
})();
if(typeof module!=='undefined') module.exports=RP;
