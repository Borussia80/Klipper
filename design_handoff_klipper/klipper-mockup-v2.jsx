import { useState } from "react";
import { AreaChart, Area, PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line } from "recharts";

// ── Design tokens ─────────────────────────────────────────────────────────────
const T = {
  bg:"#020617", bg2:"#07111D", card:"#0D1726", active:"#132238",
  crit:"#1B2B45",
  border:"rgba(255,255,255,0.07)", border2:"rgba(255,255,255,0.13)",
  brass:"#D9B26F", brassSoft:"rgba(217,178,111,0.12)", brassGlow:"rgba(217,178,111,0.25)",
  sea:"#7FB3C8", electric:"#3B82F6", electricSoft:"rgba(59,130,246,0.12)",
  emerald:"#10B981", emeraldSoft:"rgba(16,185,129,0.12)",
  rust:"#F87171", warn:"#F59E0B", moss:"#34D399",
  ink:"#F1F5F9", ink2:"#CBD5E1", ink3:"#94A3B8", ink4:"#475569",
  // Brand blues from logo
  brandDark:"#0D1B35", brandMid:"#2961C7", brandLight:"#5AAFF0",
};

const CAT = {
  "Moradia":["#10B981","rgba(16,185,129,.14)"],
  "Alimentação":["#F59E0B","rgba(245,158,11,.14)"],
  "Transporte":["#3B82F6","rgba(59,130,246,.14)"],
  "Saúde":["#EF4444","rgba(239,68,68,.14)"],
  "Lazer":["#8B5CF6","rgba(139,92,246,.14)"],
  "Investimento":["#D9B26F","rgba(217,178,111,.18)"],
  "Educação":["#0EA5E9","rgba(14,165,233,.14)"],
  "Renda":["#22C55E","rgba(34,197,94,.14)"],
  "Outros":["#8F8770","rgba(143,135,112,.12)"],
};

const fmtBRL = v=>"R$ "+v.toLocaleString("pt-BR",{minimumFractionDigits:2,maximumFractionDigits:2});
const fmtK   = v=>v>=1000?`R$ ${(v/1000).toFixed(1).replace(".",",")}k`:fmtBRL(v);
const fmtPct = (v,plus=true)=>`${v>0&&plus?"+":""}${v.toFixed(1).replace(".",",")}%`;

// ── Logo SVG (fiel ao brand mark) ─────────────────────────────────────────────
function KlipperMark({size=32}) {
  return (
    <svg width={size} height={size} viewBox="0 0 60 60" fill="none">
      <defs>
        <linearGradient id="blade-g" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#7EC4F4"/>
          <stop offset="55%" stopColor="#3B82F6"/>
          <stop offset="100%" stopColor="#1D4ED8"/>
        </linearGradient>
      </defs>
      {/* Vertical left bar — dark navy */}
      <rect x="8" y="4" width="13" height="52" fill={T.brandDark}/>
      {/* Upper arm diagonal — dark navy */}
      <polygon points="21,4 54,4 21,30" fill={T.brandDark}/>
      {/* Lower blade — blue gradient wedge */}
      <polygon points="21,32 54,56 21,56" fill="url(#blade-g)"/>
    </svg>
  );
}

function KlipperLockup({dark=true}) {
  return (
    <div style={{display:"flex",alignItems:"center",gap:10}}>
      <KlipperMark size={30}/>
      <span style={{fontFamily:"'Geist',sans-serif",fontSize:20,fontWeight:600,
        letterSpacing:"-.03em",color:dark?T.ink:"#0D1B35"}}>
        Klipper
      </span>
    </div>
  );
}

// ── CSS ───────────────────────────────────────────────────────────────────────
const css = `
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500;600&family=Geist:wght@300;400;500;600;700&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
body{background:#020617;color:#F1F5F9;font-family:'Geist',sans-serif;-webkit-font-smoothing:antialiased}
::-webkit-scrollbar{width:3px}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,.1);border-radius:4px}
.serif{font-family:'Instrument Serif',serif;letter-spacing:-.02em}
.mono{font-family:'JetBrains Mono',monospace;font-variant-numeric:tabular-nums}
.fade{animation:fadeUp .3s cubic-bezier(.2,.7,.2,1) both}
@keyframes fadeUp{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
.modal-bg{position:fixed;inset:0;background:rgba(2,6,23,.82);backdrop-filter:blur(10px);
  display:flex;align-items:center;justify-content:center;z-index:200;animation:fi .18s ease}
@keyframes fi{from{opacity:0}to{opacity:1}}
.modal{background:#0D1726;border:1px solid rgba(255,255,255,.13);border-radius:22px;
  padding:28px 32px;width:580px;max-width:95vw;animation:su .22s cubic-bezier(.2,.7,.2,1)}
@keyframes su{from{transform:translateY(18px);opacity:0}to{transform:translateY(0);opacity:1}}
.k-input{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);
  border-radius:10px;color:#F1F5F9;font-family:'Geist',sans-serif;font-size:13px;
  padding:9px 13px;width:100%;outline:none;transition:border-color .15s,box-shadow .15s}
.k-input:focus{border-color:#D9B26F;box-shadow:0 0 0 1px #D9B26F,0 0 10px rgba(217,178,111,.18)}
.k-select{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);
  border-radius:10px;color:#F1F5F9;font-family:'Geist',sans-serif;font-size:13px;
  padding:9px 13px;width:100%;outline:none;cursor:pointer}
.btn-p{background:linear-gradient(180deg,#D9B26F,#B8923D);color:#1A1106;font-weight:600;
  font-size:13px;border:none;border-radius:999px;padding:9px 22px;cursor:pointer;
  font-family:'Geist',sans-serif;transition:filter .12s,transform .1s;
  box-shadow:0 0 0 1px rgba(217,178,111,.2),0 4px 16px rgba(217,178,111,.12)}
.btn-p:hover{filter:brightness(1.08);transform:translateY(-1px)}
.btn-g{background:rgba(255,255,255,.05);color:#F1F5F9;font-size:13px;
  border:1px solid rgba(255,255,255,.08);border-radius:999px;padding:9px 22px;
  cursor:pointer;font-family:'Geist',sans-serif;transition:all .12s}
.btn-g:hover{background:rgba(255,255,255,.1);border-color:rgba(255,255,255,.15)}
.btn-sm{font-size:11px;padding:6px 14px}
.nav-btn{display:flex;align-items:center;gap:10;padding:9px 12px;border-radius:10px;
  border:none;cursor:pointer;text-align:left;font-size:13px;font-family:'Geist',sans-serif;
  transition:all .15s;width:100%}
.chip{display:inline-flex;align-items:center;padding:5px 12px;border-radius:999px;
  font-size:11px;font-weight:600;cursor:pointer;transition:all .15s;border:1px solid transparent;
  font-family:'Geist',sans-serif}
.kpi-card{background:#0D1726;border:1px solid rgba(255,255,255,.07);border-radius:16px;
  padding:18px 20px;flex:1;transition:border-color .2s,box-shadow .2s,transform .2s;cursor:default}
.kpi-card:hover{border-color:rgba(255,255,255,.14);
  box-shadow:0 8px 28px rgba(0,0,0,.45);transform:translateY(-1px)}
.tx-row{display:grid;grid-template-columns:40px 1fr auto;gap:12px;align-items:center;
  padding:10px 0;border-top:1px solid rgba(255,255,255,.07)}
.tx-row:first-of-type{border-top:none}
.card-obj{border-radius:16px;padding:20px;position:relative;overflow:hidden;
  cursor:default;transition:transform .2s,box-shadow .2s}
.card-obj:hover{transform:translateY(-2px);box-shadow:0 12px 32px rgba(0,0,0,.5)}
.section-label{font-size:10px;letter-spacing:.12em;text-transform:uppercase;
  color:#94A3B8;font-weight:600;margin-bottom:12px}
`;

// ── Dados mock ────────────────────────────────────────────────────────────────
const monthlyBar = [
  {m:"Dez",e:8200,s:6100},{m:"Jan",e:9100,s:7200},{m:"Fev",e:7800,s:5900},
  {m:"Mar",e:10200,s:8100},{m:"Abr",e:9500,s:6800},{m:"Mai",e:11200,s:7500},
];
const spendPie = [
  {n:"Moradia",v:3200},{n:"Alimentação",v:1800},{n:"Saúde",v:1500},
  {n:"Transporte",v:950},{n:"Lazer",v:650},{n:"Outros",v:400},
];
const txList = [
  {d:"25/Mai",name:"Salário",cat:"Renda",val:11200,pos:true,conta:"Itaú CC"},
  {d:"24/Mai",name:"Condomínio",cat:"Moradia",val:3200,pos:false,conta:"Itaú CC"},
  {d:"24/Mai",name:"Terapia Pedro",cat:"Saúde",val:350,pos:false,conta:"Nubank"},
  {d:"23/Mai",name:"Mercado Extra",cat:"Alimentação",val:487,pos:false,conta:"Nubank"},
  {d:"23/Mai",name:"Uber",cat:"Transporte",val:87,pos:false,conta:"Itaú CC"},
  {d:"22/Mai",name:"Rendimento MXRF11",cat:"Renda",val:210,pos:true,conta:"BTG"},
  {d:"21/Mai",name:"Cinema",cat:"Lazer",val:95,pos:false,conta:"Nubank"},
  {d:"20/Mai",name:"Freelance Proj X",cat:"Renda",val:2400,pos:true,conta:"Itaú CC"},
];
const positions = [
  {t:"MXRF11",s:"FII",p:10.42,v:+0.8,vt:18750,gl:+12.3,qty:1800},
  {t:"BOVA11",s:"ETF",p:118.90,v:-0.3,vt:11890,gl:+4.1,qty:100},
  {t:"TESOURO",s:"RF",p:null,v:null,vt:25000,gl:+8.7,qty:1},
  {t:"PETR4",s:"Ação",p:38.60,v:+1.4,vt:7720,gl:-2.1,qty:200},
];
const portPerf = [
  {d:"Nov",v:57200},{d:"Dez",v:58100},{d:"Jan",v:60200},{d:"Fev",v:59100},
  {d:"Mar",v:61800},{d:"Abr",v:62400},{d:"Mai",v:63360},
];
const contas = [
  {id:1,name:"Conta Corrente Itaú",bank:"Itaú",color:"#F97316",bal:18420.50,type:"CC"},
  {id:2,name:"Nubank",bank:"Nubank",color:"#8B5CF6",bal:3200.00,type:"CC"},
  {id:3,name:"BTG Invest",bank:"BTG",color:"#3B82F6",bal:20680.00,type:"Invest"},
];
const cartoes = [
  {id:1,name:"Itaú Mastercard",bank:"Itaú",color:"#F97316",limit:8000,used:3240,close:5,due:15},
  {id:2,name:"Nubank Platinum",bank:"Nubank",color:"#8B5CF6",limit:12000,used:1890,close:15,due:25},
];
const NAVITEMS = [
  {i:"◉",l:"Dashboard",id:"dash"},
  {i:"↕",l:"Transações",id:"tx"},
  {i:"▲",l:"Investimentos",id:"inv"},
  {i:"⊞",l:"Contas",id:"contas"},
  {i:"◎",l:"Orçamento",id:"orc"},
  {i:"∞",l:"AI Consilium",id:"ai"},
  {i:"✚",l:"Saúde",id:"saude"},
];

// ── Componentes base ──────────────────────────────────────────────────────────
function Sidebar({active, onNav}) {
  return (
    <div style={{width:220,background:T.bg2,borderRight:`1px solid ${T.border}`,
      display:"flex",flexDirection:"column",padding:"20px 10px",
      flexShrink:0,height:"100vh",position:"sticky",top:0}}>
      <div style={{padding:"4px 10px 24px"}}>
        <KlipperLockup/>
      </div>
      <div style={{display:"flex",flexDirection:"column",gap:2,flex:1}}>
        {NAVITEMS.map(item=>{
          const isActive = active===item.id;
          return(
            <button key={item.id} onClick={()=>onNav(item.id)}
              className="nav-btn"
              style={{gap:10,background:isActive?T.emeraldSoft:"transparent",
                color:isActive?T.emerald:T.ink3,
                fontWeight:isActive?600:400}}>
              <span style={{fontSize:14,width:18,textAlign:"center",flexShrink:0}}>{item.i}</span>
              <span>{item.l}</span>
              {isActive&&<div style={{marginLeft:"auto",width:4,height:4,borderRadius:"50%",background:T.emerald}}/>}
            </button>
          );
        })}
      </div>
      <div style={{borderTop:`1px solid ${T.border}`,paddingTop:14,marginTop:14,padding:"14px 10px 0"}}>
        <div style={{display:"flex",alignItems:"center",gap:10}}>
          <div style={{width:30,height:30,borderRadius:"50%",
            background:"linear-gradient(135deg,#2961C7,#5AAFF0)",
            display:"flex",alignItems:"center",justifyContent:"center",
            fontSize:12,fontWeight:700,color:"#fff",flexShrink:0}}>R</div>
          <div style={{minWidth:0}}>
            <div style={{fontSize:12,fontWeight:500,color:T.ink,whiteSpace:"nowrap",overflow:"hidden",textOverflow:"ellipsis"}}>Roberto Milet</div>
            <div style={{fontSize:10,color:T.ink4}}>I&C Engineer</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function KPICard({label,value,sub,tone,delta}) {
  const c = {pos:T.emerald,neg:T.rust,brass:T.brass,sea:T.sea}[tone]||T.ink;
  return (
    <div className="kpi-card">
      <div className="section-label" style={{marginBottom:5}}>{label}</div>
      <div className="mono" style={{fontSize:21,fontWeight:600,color:c,marginBottom:3}}>{value}</div>
      <div style={{fontSize:11,color:T.ink4}}>{sub}</div>
    </div>
  );
}

function TxRow({tx,onClick}) {
  const [fg,bg]=CAT[tx.cat]||["#8F8770","rgba(143,135,112,.12)"];
  return(
    <div className="tx-row" onClick={onClick}
      style={{cursor:"pointer",borderRadius:6,padding:"10px 4px",
        transition:"background .12s"}}
      onMouseEnter={e=>e.currentTarget.style.background="rgba(255,255,255,.03)"}
      onMouseLeave={e=>e.currentTarget.style.background="transparent"}>
      <div style={{width:38,height:38,borderRadius:10,background:bg,flexShrink:0,
        display:"flex",alignItems:"center",justifyContent:"center",fontSize:15,
        fontWeight:600,color:fg}}>
        {tx.cat[0]}
      </div>
      <div style={{minWidth:0}}>
        <div style={{fontSize:13,fontWeight:500,color:T.ink,whiteSpace:"nowrap",overflow:"hidden",textOverflow:"ellipsis"}}>{tx.name}</div>
        <div style={{fontSize:10.5,color:T.ink3,marginTop:1}}>{tx.d} · {tx.cat} · {tx.conta}</div>
      </div>
      <div className="mono" style={{fontSize:13,fontWeight:600,textAlign:"right",flexShrink:0,
        color:tx.pos?T.emerald:T.electric}}>
        {tx.pos?"+":""}{fmtK(tx.val)}
      </div>
    </div>
  );
}

const CustomTip=({active,payload,label})=>{
  if(!active||!payload?.length)return null;
  return(
    <div style={{background:T.card,border:`1px solid ${T.border2}`,borderRadius:10,
      padding:"10px 14px",fontFamily:"'JetBrains Mono',monospace",fontSize:11}}>
      <div style={{color:T.ink3,marginBottom:4}}>{label}</div>
      {payload.map((p,i)=>(
        <div key={i} style={{color:p.color||p.fill||T.ink}}>{p.name}: {fmtK(p.value)}</div>
      ))}
    </div>
  );
};

// ── Modal Transação ───────────────────────────────────────────────────────────
function AddTxModal({onClose}) {
  const [tipo,setTipo]=useState("GASTO");
  const [tab,setTab]=useState("rapido");
  return(
    <div className="modal-bg" onClick={e=>{if(e.target===e.currentTarget)onClose()}}>
      <div className="modal">
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:18}}>
          <div>
            <div style={{fontSize:16,fontWeight:600,color:T.ink}}>Lançar transação</div>
            <div style={{fontSize:11,color:T.ink4,marginTop:2}}>registre ganhos ou gastos no Klipper</div>
          </div>
          <button onClick={onClose} style={{background:"none",border:"none",color:T.ink3,
            fontSize:18,cursor:"pointer",lineHeight:1,padding:"2px 6px",borderRadius:6,
            transition:"background .12s"}}
            onMouseEnter={e=>e.currentTarget.style.background="rgba(255,255,255,.08)"}
            onMouseLeave={e=>e.currentTarget.style.background="none"}>✕</button>
        </div>
        {/* Tabs */}
        <div style={{display:"flex",gap:0,marginBottom:20,background:"rgba(255,255,255,.04)",
          borderRadius:10,padding:3}}>
          {[["rapido","⚡ Rápido"],["completo","Completo"]].map(([id,l])=>(
            <button key={id} onClick={()=>setTab(id)}
              style={{flex:1,padding:"7px 12px",borderRadius:8,border:"none",cursor:"pointer",
                fontSize:12,fontFamily:"'Geist',sans-serif",fontWeight:tab===id?600:400,
                background:tab===id?T.card:"transparent",
                color:tab===id?T.ink:T.ink3,transition:"all .15s"}}>
              {l}
            </button>
          ))}
        </div>

        {tab==="rapido"?(
          <div>
            <div style={{fontSize:12,color:T.ink3,marginBottom:10,lineHeight:1.5}}>
              Digite em linguagem natural — inferimos categoria, valor e método.
            </div>
            <input className="k-input" placeholder="almoço 42 · pix mercado 150 · uber 25 crédito"
              style={{fontSize:14,padding:"12px 14px",marginBottom:12}}/>
            <div style={{background:T.brassSoft,border:"1px solid rgba(217,178,111,.22)",
              borderRadius:12,padding:"12px 16px",marginBottom:20}}>
              <div className="section-label" style={{color:T.brass,marginBottom:6}}>Inferido pelo Klipper</div>
              <div style={{display:"flex",gap:20,fontSize:12}}>
                <div><span style={{color:T.ink4}}>Descrição: </span><span style={{color:T.ink,fontWeight:500}}>almoço</span></div>
                <div><span style={{color:T.ink4}}>Valor: </span><span className="mono" style={{color:T.ink,fontWeight:600}}>R$ 42,00</span></div>
                <div><span style={{color:T.ink4}}>Categoria: </span><span style={{color:T.warn,fontWeight:500}}>Alimentação</span></div>
                <div><span style={{color:T.ink4}}>Via: </span><span style={{color:T.ink3}}>PIX</span></div>
              </div>
            </div>
            <div style={{display:"flex",gap:8,justifyContent:"flex-end"}}>
              <button className="btn-g" onClick={onClose}>Cancelar</button>
              <button className="btn-p">Confirmar lançamento</button>
            </div>
          </div>
        ):(
          <div>
            <div style={{display:"flex",gap:8,marginBottom:16}}>
              {[["GANHO","⬆ Receita",T.emerald],["GASTO","⬇ Gasto",T.rust]].map(([t,l,c])=>(
                <button key={t} onClick={()=>setTipo(t)} style={{flex:1,padding:"9px",
                  borderRadius:10,border:`1.5px solid ${tipo===t?c:T.border}`,
                  background:tipo===t?`${c}18`:"transparent",
                  color:tipo===t?c:T.ink3,fontSize:13,fontWeight:600,
                  cursor:"pointer",fontFamily:"'Geist',sans-serif",transition:"all .15s"}}>
                  {l}
                </button>
              ))}
            </div>
            <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:10,marginBottom:10}}>
              <div>
                <div className="section-label">Data</div>
                <input type="date" className="k-input" defaultValue="2026-05-25"/>
              </div>
              <div>
                <div className="section-label">Valor (R$)</div>
                <input className="k-input mono" placeholder="0,00" style={{fontSize:15}}/>
              </div>
            </div>
            <div style={{marginBottom:10}}>
              <div className="section-label">Descrição</div>
              <input className="k-input" placeholder="Ex: Supermercado, Salário, Consulta…"/>
            </div>
            <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:10,marginBottom:10}}>
              <div><div className="section-label">Categoria</div>
                <select className="k-select">{Object.keys(CAT).map(c=><option key={c}>{c}</option>)}</select></div>
              <div><div className="section-label">Conta</div>
                <select className="k-select">
                  <option>Itaú CC</option><option>Nubank</option><option>BTG Invest</option>
                </select></div>
            </div>
            <div style={{display:"grid",gridTemplateColumns:"1fr 1fr 1fr",gap:10,marginBottom:20}}>
              <div><div className="section-label">Status</div>
                <select className="k-select"><option>✅ Confirmado</option><option>⏳ Pendente</option></select></div>
              <div><div className="section-label">Pagamento</div>
                <select className="k-select"><option>PIX</option><option>Crédito</option><option>Débito</option></select></div>
              <div><div className="section-label">Parcelas</div>
                <select className="k-select"><option>À vista</option><option>2×</option><option>3×</option><option>6×</option><option>12×</option></select></div>
            </div>
            <div style={{display:"flex",gap:8,justifyContent:"flex-end"}}>
              <button className="btn-g" onClick={onClose}>Cancelar</button>
              <button className="btn-p">Salvar transação</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ── PÁGINA: Dashboard ─────────────────────────────────────────────────────────
function Dashboard({onAddTx}) {
  return(
    <div style={{flex:1,overflowY:"auto",padding:"28px 32px"}} className="fade">
      {/* Hero */}
      <div style={{background:"linear-gradient(135deg,#020617 0%,#07111D 55%,#0D1726 100%)",
        border:"1px solid rgba(16,185,129,.12)",borderRadius:24,padding:"28px 32px",
        marginBottom:22,position:"relative",overflow:"hidden"}}>
        <div style={{position:"absolute",top:"-40%",left:"-8%",width:"55%",height:"180%",
          background:"radial-gradient(ellipse,rgba(16,185,129,.08) 0%,transparent 70%)",pointerEvents:"none"}}/>
        <div style={{position:"absolute",bottom:"-30%",right:"-5%",width:"45%",height:"140%",
          background:"radial-gradient(ellipse,rgba(41,97,199,.07) 0%,transparent 65%)",pointerEvents:"none"}}/>
        <div className="mono" style={{fontSize:9,letterSpacing:".18em",textTransform:"uppercase",
          color:T.emerald,fontWeight:600,marginBottom:3}}>mai · 2026</div>
        <div style={{fontSize:11,color:T.ink4,marginBottom:8}}>tudo em dia · 0 pendentes</div>
        <div className="serif" style={{fontSize:42,color:T.ink,lineHeight:1,marginBottom:18}}>
          R$ 3.700,00
        </div>
        <div style={{display:"flex",alignItems:"center",gap:6,flexWrap:"wrap"}}>
          {[["Entradas",fmtK(11200),T.emerald],["Saídas",fmtK(7500),T.electric],["Caixa total",fmtK(42300),T.brass]].map(([l,v,c],i)=>(
            <div key={l} style={{display:"flex",alignItems:"center",gap:i>0?0:0}}>
              {i>0&&<div style={{width:1,height:24,background:"rgba(255,255,255,.08)",margin:"0 16px"}}/>}
              <div>
                <div style={{fontSize:9.5,color:T.ink4,letterSpacing:".05em",marginBottom:2}}>{l}</div>
                <div className="mono" style={{fontSize:14,fontWeight:600,color:c}}>{v}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick actions */}
      <div style={{display:"flex",gap:8,marginBottom:20,flexWrap:"wrap"}}>
        <button className="btn-p btn-sm" onClick={onAddTx}>＋ Lançar</button>
        {["⇄ Transferir","⬆ Importar","◈ Investir"].map(l=>(
          <button key={l} className="btn-g btn-sm">{l}</button>
        ))}
      </div>

      {/* KPIs */}
      <div style={{display:"flex",gap:10,marginBottom:20}}>
        <KPICard label="Caixa disponível" value={fmtK(42300)} sub="2 contas ativas"/>
        <KPICard label="Entradas · mês" value={fmtK(11200)} sub="3 fontes" tone="pos"/>
        <KPICard label="Saídas · mês" value={fmtK(7500)} sub="8 lançamentos" tone="neg"/>
        <KPICard label="Saldo líquido" value={fmtK(3700)} sub="▲ mai/2026" tone="brass"/>
      </div>

      {/* Charts */}
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:14,marginBottom:20}}>
        <div style={{background:T.card,border:`1px solid ${T.border}`,borderRadius:20,padding:"20px 22px"}}>
          <div className="section-label">Gastos por categoria</div>
          <div style={{display:"flex",alignItems:"center",gap:8}}>
            <PieChart width={118} height={118}>
              <Pie data={spendPie} cx={54} cy={54} innerRadius={34} outerRadius={50}
                dataKey="v" startAngle={90} endAngle={-270} strokeWidth={0}>
                {spendPie.map((s,i)=><Cell key={i} fill={(CAT[s.n]||["#8F8770"])[0]}/>)}
              </Pie>
            </PieChart>
            <div style={{flex:1,display:"flex",flexDirection:"column",gap:5}}>
              {spendPie.slice(0,5).map((s,i)=>(
                <div key={i} style={{display:"flex",justifyContent:"space-between",alignItems:"center"}}>
                  <div style={{display:"flex",alignItems:"center",gap:5}}>
                    <div style={{width:7,height:7,borderRadius:2,flexShrink:0,background:(CAT[s.n]||["#8F8770"])[0]}}/>
                    <span style={{fontSize:11,color:T.ink3}}>{s.n}</span>
                  </div>
                  <span className="mono" style={{fontSize:11,color:T.ink2}}>{fmtK(s.v)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
        <div style={{background:T.card,border:`1px solid ${T.border}`,borderRadius:20,padding:"20px 22px"}}>
          <div className="section-label">Entradas × Saídas · 6 meses</div>
          <ResponsiveContainer width="100%" height={118}>
            <BarChart data={monthlyBar} barSize={7} barGap={2}>
              <XAxis dataKey="m" tick={{fontSize:9,fill:T.ink4}} axisLine={false} tickLine={false}/>
              <YAxis hide/><Tooltip content={<CustomTip/>}/>
              <Bar dataKey="e" name="Entradas" fill={T.emerald} radius={[3,3,0,0]}/>
              <Bar dataKey="s" name="Saídas"   fill={T.electric} radius={[3,3,0,0]}/>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent transactions */}
      <div style={{background:T.card,border:`1px solid ${T.border}`,borderRadius:20,padding:"20px 22px"}}>
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:14}}>
          <div className="section-label" style={{margin:0}}>Últimas transações</div>
          <span style={{fontSize:11,color:T.brass,cursor:"pointer",fontWeight:500}}>Ver todas →</span>
        </div>
        {txList.slice(0,5).map((tx,i)=><TxRow key={i} tx={tx} onClick={()=>{}}/>)}
        <div style={{marginTop:14}}>
          <button className="btn-p btn-sm" onClick={onAddTx}>＋ Lançar transação</button>
        </div>
      </div>
    </div>
  );
}

// ── PÁGINA: Transações ────────────────────────────────────────────────────────
function Transacoes({onAddTx}) {
  const [filter,setFilter]=useState("Todas");
  const [search,setSearch]=useState("");
  const filters=["Todas","Receitas","Gastos","Pendentes"];
  const filtered=txList.filter(tx=>{
    if(filter==="Receitas"&&!tx.pos)return false;
    if(filter==="Gastos"&&tx.pos)return false;
    if(search&&!tx.name.toLowerCase().includes(search.toLowerCase()))return false;
    return true;
  });
  const totalE=txList.filter(t=>t.pos).reduce((a,t)=>a+t.val,0);
  const totalS=txList.filter(t=>!t.pos).reduce((a,t)=>a+t.val,0);

  return(
    <div style={{flex:1,overflowY:"auto",padding:"28px 32px"}} className="fade">
      {/* Header */}
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:20}}>
        <div>
          <div className="serif" style={{fontSize:26,color:T.ink,lineHeight:1}}>Transações</div>
          <div style={{fontSize:11,color:T.ink4,marginTop:4}}>maio · 2026 · {txList.length} lançamentos</div>
        </div>
        <div style={{display:"flex",gap:8}}>
          <button className="btn-g btn-sm">⬆ Importar extrato</button>
          <button className="btn-p btn-sm" onClick={onAddTx}>＋ Novo lançamento</button>
        </div>
      </div>

      {/* KPIs */}
      <div style={{display:"flex",gap:10,marginBottom:20}}>
        <KPICard label="Receitas" value={fmtK(totalE)} sub={`${txList.filter(t=>t.pos).length} lançamentos`} tone="pos"/>
        <KPICard label="Gastos" value={fmtK(totalS)} sub={`${txList.filter(t=>!t.pos).length} lançamentos`} tone="neg"/>
        <KPICard label="Saldo" value={fmtK(totalE-totalS)} sub="mai/2026" tone="brass"/>
        <KPICard label="Pendentes" value="0" sub="tudo confirmado"/>
      </div>

      {/* Mini chart */}
      <div style={{background:T.card,border:`1px solid ${T.border}`,borderRadius:16,
        padding:"16px 20px",marginBottom:16}}>
        <div className="section-label">Gastos diários · maio</div>
        <ResponsiveContainer width="100%" height={72}>
          <AreaChart data={[
            {d:"1",v:0},{d:"5",v:200},{d:"10",v:850},{d:"15",v:1200},
            {d:"20",v:2800},{d:"21",v:3200},{d:"22",v:3320},{d:"23",v:3807},{d:"24",v:7057},{d:"25",v:7057},
          ]}>
            <defs><linearGradient id="ag" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={T.electric} stopOpacity={0.3}/>
              <stop offset="95%" stopColor={T.electric} stopOpacity={0}/>
            </linearGradient></defs>
            <XAxis dataKey="d" tick={{fontSize:9,fill:T.ink4}} axisLine={false} tickLine={false}/>
            <YAxis hide/>
            <Area type="monotone" dataKey="v" stroke={T.electric} strokeWidth={1.5} fill="url(#ag)" dot={false}/>
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Filtros + busca */}
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:14}}>
        <div style={{display:"flex",gap:6}}>
          {filters.map(f=>(
            <button key={f} className="chip" onClick={()=>setFilter(f)}
              style={{background:filter===f?"rgba(217,178,111,.15)":"rgba(255,255,255,.04)",
                color:filter===f?T.brass:T.ink3,
                borderColor:filter===f?"rgba(217,178,111,.3)":T.border}}>
              {f}
            </button>
          ))}
        </div>
        <input className="k-input" placeholder="🔍 Buscar transação…"
          value={search} onChange={e=>setSearch(e.target.value)}
          style={{width:220,fontSize:12,padding:"7px 12px"}}/>
      </div>

      {/* Lista agrupada */}
      {["25/Mai","24/Mai","23/Mai","22/Mai","21/Mai","20/Mai"].map(d=>{
        const dayTxs=filtered.filter(t=>t.d===d);
        if(!dayTxs.length)return null;
        const dayTotal=dayTxs.reduce((a,t)=>a+(t.pos?t.val:-t.val),0);
        return(
          <div key={d} style={{marginBottom:12}}>
            <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",
              padding:"6px 4px",marginBottom:4}}>
              <div style={{fontSize:11,color:T.ink4,fontWeight:500}}>{d}</div>
              <div className="mono" style={{fontSize:11,
                color:dayTotal>=0?T.emerald:T.rust}}>
                {dayTotal>=0?"+":""}{fmtK(Math.abs(dayTotal))}
              </div>
            </div>
            <div style={{background:T.card,border:`1px solid ${T.border}`,
              borderRadius:16,padding:"4px 16px"}}>
              {dayTxs.map((tx,i)=><TxRow key={i} tx={tx} onClick={()=>{}}/>)}
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ── PÁGINA: Investimentos ─────────────────────────────────────────────────────
function Investimentos({onAddInv}) {
  const total=63360,custo=57520,gl=total-custo,glp=(gl/custo*100);
  const allocData=[{n:"Renda Fixa",v:25000},{n:"FII",v:18750},{n:"Ação",v:12110},{n:"ETF",v:7500}];
  const allocColors=[T.emerald,T.brass,T.electric,"#8B5CF6"];

  return(
    <div style={{flex:1,overflowY:"auto",padding:"28px 32px"}} className="fade">
      {/* Hero */}
      <div style={{background:"linear-gradient(135deg,#0D1726 0%,#132238 55%,#1B2B45 100%)",
        border:"1px solid rgba(217,178,111,.18)",borderRadius:24,padding:"28px 32px",
        marginBottom:22,position:"relative",overflow:"hidden"}}>
        <div style={{position:"absolute",top:"-30%",right:"-8%",width:"50%",height:"160%",
          background:"radial-gradient(ellipse,rgba(217,178,111,.07) 0%,transparent 70%)",pointerEvents:"none"}}/>
        <div className="mono" style={{fontSize:9,letterSpacing:".18em",textTransform:"uppercase",
          color:T.brass,fontWeight:600,marginBottom:3}}>Portfólio · ao vivo</div>
        <div className="serif" style={{fontSize:42,color:T.ink,lineHeight:1,marginBottom:6}}>
          {fmtBRL(total)}
        </div>
        <div className="mono" style={{fontSize:13,color:T.emerald,marginBottom:16}}>
          ▲ {fmtK(gl)} ({fmtPct(glp)}) sobre custo total
        </div>
        {/* Benchmarks */}
        <div style={{display:"flex",gap:10,flexWrap:"wrap"}}>
          {[["Portfólio",glp,true],["BOVA11",-0.3,false],["IFIX",0.6,false],["IVVB11",1.1,false]].map(([l,v,h])=>(
            <div key={l} style={{background:"rgba(255,255,255,.05)",border:`1px solid ${T.border}`,
              borderRadius:10,padding:"8px 14px",minWidth:90}}>
              <div style={{fontSize:9,color:T.ink4,letterSpacing:".08em",textTransform:"uppercase",marginBottom:3}}>{l}</div>
              <div className="mono" style={{fontSize:13,fontWeight:600,
                color:v>=0?T.emerald:T.rust}}>{fmtPct(v)}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div style={{display:"flex",gap:8,marginBottom:20}}>
        <button className="btn-p btn-sm" onClick={onAddInv}>＋ Nova posição</button>
        <button className="btn-g btn-sm">↺ Atualizar cotações</button>
      </div>

      {/* KPIs */}
      <div style={{display:"flex",gap:10,marginBottom:20}}>
        <KPICard label="Valor de mercado" value={fmtK(total)} sub="4 ativos" tone="brass"/>
        <KPICard label="P&L total" value={fmtK(gl)} sub={fmtPct(glp)} tone="pos"/>
        <KPICard label="DY médio 12m" value="11,2%" sub="rendimentos YTD"/>
        <KPICard label="Fragilidade" value="0.28" sub="baixa · M2 ok" tone="pos"/>
      </div>

      {/* Posições + Alocação */}
      <div style={{display:"grid",gridTemplateColumns:"1fr auto",gap:14,marginBottom:14}}>
        {/* Tabela */}
        <div style={{background:T.card,border:`1px solid ${T.border}`,borderRadius:20,padding:"20px 22px"}}>
          <div className="section-label">Posições ao vivo</div>
          {/* Header */}
          <div style={{display:"grid",gridTemplateColumns:"86px 60px 1fr 76px 76px 76px 30px",
            gap:8,fontSize:9.5,letterSpacing:".1em",textTransform:"uppercase",color:T.ink4,
            fontWeight:600,paddingBottom:10,borderBottom:`1px solid ${T.border}`,marginBottom:2}}>
            <span>Ticker</span><span>Setor</span><span>Valor</span>
            <span style={{textAlign:"right"}}>Preço</span>
            <span style={{textAlign:"right"}}>Var%</span>
            <span style={{textAlign:"right"}}>G/L%</span>
            <span/>
          </div>
          {positions.map((p,i)=>(
            <div key={i} style={{display:"grid",
              gridTemplateColumns:"86px 60px 1fr 76px 76px 76px 30px",
              gap:8,alignItems:"center",padding:"10px 0",fontSize:12,
              borderBottom:i<positions.length-1?`1px solid ${T.border}`:"none"}}>
              <span className="mono" style={{color:T.brass,fontWeight:600,fontSize:13}}>{p.t}</span>
              <span style={{color:T.ink3,fontSize:11}}>{p.s}</span>
              <span className="mono" style={{color:T.ink,fontWeight:500}}>{fmtK(p.vt)}</span>
              <span className="mono" style={{textAlign:"right",color:T.ink2}}>
                {p.p?`R$ ${p.p}`:"—"}</span>
              <span className="mono" style={{textAlign:"right",
                color:p.v===null?T.ink4:p.v>=0?T.emerald:T.rust}}>
                {p.v===null?"—":fmtPct(p.v)}</span>
              <span className="mono" style={{textAlign:"right",fontWeight:600,
                color:p.gl>=0?T.emerald:T.rust}}>{fmtPct(p.gl)}</span>
              <button style={{background:"rgba(255,255,255,.05)",border:`1px solid ${T.border}`,
                borderRadius:6,color:T.ink3,cursor:"pointer",fontSize:11,padding:"3px 6px"}}>✎</button>
            </div>
          ))}
        </div>

        {/* Donut alocação */}
        <div style={{background:T.card,border:`1px solid ${T.border}`,borderRadius:20,
          padding:"20px 22px",width:220,flexShrink:0}}>
          <div className="section-label">Alocação</div>
          <div style={{display:"flex",justifyContent:"center",margin:"8px 0"}}>
            <PieChart width={140} height={140}>
              <Pie data={allocData} cx={65} cy={65} innerRadius={40} outerRadius={58}
                dataKey="v" startAngle={90} endAngle={-270} strokeWidth={0}>
                {allocData.map((d,i)=><Cell key={i} fill={allocColors[i]}/>)}
              </Pie>
            </PieChart>
          </div>
          {allocData.map((d,i)=>(
            <div key={i} style={{display:"flex",justifyContent:"space-between",
              padding:"5px 0",borderTop:`1px solid ${T.border}`}}>
              <div style={{display:"flex",alignItems:"center",gap:6}}>
                <div style={{width:7,height:7,borderRadius:2,background:allocColors[i]}}/>
                <span style={{fontSize:11,color:T.ink3}}>{d.n}</span>
              </div>
              <span className="mono" style={{fontSize:11,color:T.ink2}}>
                {((d.v/total)*100).toFixed(0)}%</span>
            </div>
          ))}
        </div>
      </div>

      {/* Performance histórica */}
      <div style={{background:T.card,border:`1px solid ${T.border}`,borderRadius:20,padding:"20px 22px"}}>
        <div className="section-label">Performance do portfólio · 6 meses</div>
        <ResponsiveContainer width="100%" height={100}>
          <AreaChart data={portPerf}>
            <defs><linearGradient id="pg" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={T.brass} stopOpacity={0.25}/>
              <stop offset="95%" stopColor={T.brass} stopOpacity={0}/>
            </linearGradient></defs>
            <XAxis dataKey="d" tick={{fontSize:9,fill:T.ink4}} axisLine={false} tickLine={false}/>
            <YAxis hide domain={['dataMin - 2000','dataMax + 1000']}/>
            <Tooltip content={<CustomTip/>}/>
            <Area type="monotone" dataKey="v" name="Portfólio" stroke={T.brass}
              strokeWidth={2} fill="url(#pg)" dot={false}/>
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// ── PÁGINA: Contas ────────────────────────────────────────────────────────────
function Contas({onAddConta}) {
  const [selAcc,setSelAcc]=useState(1);
  const totalCaixa=contas.reduce((a,c)=>a+c.bal,0);
  const totalLimit=cartoes.reduce((a,c)=>a+c.limit,0);
  const totalUsed=cartoes.reduce((a,c)=>a+c.used,0);

  return(
    <div style={{flex:1,overflowY:"auto",padding:"28px 32px"}} className="fade">
      {/* Header */}
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:20}}>
        <div>
          <div className="serif" style={{fontSize:26,color:T.ink}}>Contas & Cartões</div>
          <div style={{fontSize:11,color:T.ink4,marginTop:4}}>carteira · saldos · parcelamentos</div>
        </div>
        <div style={{display:"flex",gap:8}}>
          <button className="btn-g btn-sm">＋ Novo cartão</button>
          <button className="btn-p btn-sm" onClick={onAddConta}>＋ Nova conta</button>
        </div>
      </div>

      {/* KPIs */}
      <div style={{display:"flex",gap:10,marginBottom:20}}>
        <KPICard label="Caixa total" value={fmtK(totalCaixa)} sub={`${contas.length} contas ativas`} tone="brass"/>
        <KPICard label="Fatura total · mês" value={fmtK(totalUsed)} sub={`${cartoes.length} cartões`} tone="neg"/>
        <KPICard label="Limite disponível" value={fmtK(totalLimit-totalUsed)} sub={`de ${fmtK(totalLimit)} total`}/>
        <KPICard label="Próx. vencimento" value="dia 15" sub="Nubank Platinum" tone="warn"/>
      </div>

      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:14,marginBottom:14}}>
        {/* Contas bancárias */}
        <div>
          <div className="section-label">Contas bancárias</div>
          <div style={{display:"flex",flexDirection:"column",gap:10}}>
            {contas.map(c=>(
              <div key={c.id} onClick={()=>setSelAcc(c.id)}
                style={{background:selAcc===c.id?T.active:T.card,
                  border:`1px solid ${selAcc===c.id?T.border2:T.border}`,
                  borderRadius:16,padding:"16px 20px",cursor:"pointer",
                  transition:"all .15s",
                  boxShadow:selAcc===c.id?"0 4px 20px rgba(0,0,0,.4)":"none"}}>
                <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start"}}>
                  <div style={{display:"flex",alignItems:"center",gap:10}}>
                    <div style={{width:36,height:36,borderRadius:10,
                      background:`${c.color}22`,border:`1px solid ${c.color}44`,
                      display:"flex",alignItems:"center",justifyContent:"center",
                      fontSize:13,fontWeight:700,color:c.color}}>
                      {c.bank[0]}
                    </div>
                    <div>
                      <div style={{fontSize:13,fontWeight:500,color:T.ink}}>{c.name}</div>
                      <div style={{fontSize:10.5,color:T.ink4,marginTop:1}}>{c.bank} · {c.type}</div>
                    </div>
                  </div>
                  <div style={{textAlign:"right"}}>
                    <div className="mono" style={{fontSize:15,fontWeight:600,color:T.emerald}}>{fmtK(c.bal)}</div>
                    <div style={{fontSize:10,color:T.ink4,marginTop:2}}>saldo atual</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Cartões */}
        <div>
          <div className="section-label">Cartões de crédito</div>
          <div style={{display:"flex",flexDirection:"column",gap:10}}>
            {cartoes.map(c=>{
              const pct=(c.used/c.limit*100);
              return(
                <div key={c.id} className="card-obj"
                  style={{background:`linear-gradient(135deg,${c.color}cc 0%,${c.color}44 60%,#0D1726 100%)`,
                    border:`1px solid ${c.color}44`}}>
                  <div style={{position:"absolute",top:"-20%",right:"-10%",width:"60%",height:"140%",
                    background:"radial-gradient(ellipse,rgba(255,255,255,.06) 0%,transparent 70%)",pointerEvents:"none"}}/>
                  <div style={{display:"flex",justifyContent:"space-between",marginBottom:20}}>
                    <div>
                      <div style={{fontSize:13,fontWeight:600,color:"#fff"}}>{c.bank}</div>
                      <div style={{fontSize:11,color:"rgba(255,255,255,.6)",marginTop:1}}>{c.name}</div>
                    </div>
                    <div style={{fontSize:18,opacity:.7}}>💳</div>
                  </div>
                  <div style={{marginBottom:10}}>
                    <div style={{display:"flex",justifyContent:"space-between",
                      fontSize:11,color:"rgba(255,255,255,.6)",marginBottom:5}}>
                      <span>Usado: <span className="mono" style={{color:"#fff",fontWeight:600}}>{fmtK(c.used)}</span></span>
                      <span>Limite: <span className="mono" style={{color:"rgba(255,255,255,.8)"}}>{fmtK(c.limit)}</span></span>
                    </div>
                    <div style={{height:4,background:"rgba(255,255,255,.15)",borderRadius:2}}>
                      <div style={{width:`${pct}%`,height:"100%",borderRadius:2,
                        background:pct>80?"#F87171":pct>60?"#F59E0B":"rgba(255,255,255,.7)",
                        transition:"width .3s"}}/>
                    </div>
                  </div>
                  <div style={{display:"flex",gap:16,fontSize:10.5,color:"rgba(255,255,255,.5)"}}>
                    <span>Fecha: dia {c.close}</span>
                    <span>Vence: dia {c.due}</span>
                    <span style={{color:pct>80?"#F87171":"rgba(255,255,255,.5)",fontWeight:pct>80?600:400}}>
                      {pct.toFixed(0)}% usado
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Transações da conta selecionada */}
      <div style={{background:T.card,border:`1px solid ${T.border}`,borderRadius:20,padding:"20px 22px"}}>
        <div className="section-label">
          Últimos lançamentos · {contas.find(c=>c.id===selAcc)?.name}
        </div>
        {txList.slice(0,4).map((tx,i)=><TxRow key={i} tx={tx} onClick={()=>{}}/>)}
      </div>
    </div>
  );
}

// ── Modal nova posição ─────────────────────────────────────────────────────────
function AddInvModal({onClose}) {
  const [searched,setSearched]=useState(false);
  return(
    <div className="modal-bg" onClick={e=>{if(e.target===e.currentTarget)onClose()}}>
      <div className="modal">
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:20}}>
          <div>
            <div style={{fontSize:16,fontWeight:600,color:T.ink}}>Nova posição</div>
            <div style={{fontSize:11,color:T.ink4,marginTop:2}}>adicionar ativo ao portfólio Klipper</div>
          </div>
          <button onClick={onClose} style={{background:"none",border:"none",color:T.ink3,
            fontSize:18,cursor:"pointer",padding:"2px 6px",borderRadius:6}}>✕</button>
        </div>
        {/* Ticker search */}
        <div style={{display:"grid",gridTemplateColumns:"1fr auto",gap:8,marginBottom:12}}>
          <div>
            <div className="section-label">Ticker</div>
            <input className="k-input mono" placeholder="MXRF11, PETR4, BOVA11…"
              style={{fontSize:15,textTransform:"uppercase"}}/>
          </div>
          <div style={{paddingTop:20}}>
            <button className="btn-g" onClick={()=>setSearched(true)}
              style={{padding:"9px 16px",fontSize:12,whiteSpace:"nowrap"}}>🔍 Buscar cotação</button>
          </div>
        </div>
        {/* Cotação live */}
        {searched&&(
          <div style={{background:T.brassSoft,border:"1px solid rgba(217,178,111,.25)",
            borderRadius:12,padding:"12px 16px",marginBottom:14}}>
            <div className="section-label" style={{color:T.brass,marginBottom:6}}>Cotação ao vivo · MXRF11</div>
            <div style={{display:"flex",gap:20,flexWrap:"wrap"}}>
              {[["Preço","R$ 10,42",T.ink],["Var. dia","+0,80%",T.emerald],["DY 12m","12,4%",T.emerald],["P/VP","0,92",T.ink]].map(([l,v,c])=>(
                <div key={l}>
                  <div style={{fontSize:10,color:T.ink4,marginBottom:2}}>{l}</div>
                  <div className="mono" style={{fontSize:13,fontWeight:600,color:c}}>{v}</div>
                </div>
              ))}
            </div>
          </div>
        )}
        <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:10,marginBottom:10}}>
          <div><div className="section-label">Quantidade</div>
            <input className="k-input mono" placeholder="1800" style={{fontSize:14}}/></div>
          <div><div className="section-label">Preço médio (R$)</div>
            <input className="k-input mono" placeholder={searched?"10,42":"0,00"} style={{fontSize:14}}/></div>
        </div>
        <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:10,marginBottom:20}}>
          <div><div className="section-label">Classe de ativo</div>
            <select className="k-select">
              <option>FII</option><option>Ação</option><option>ETF</option>
              <option>Renda Fixa</option><option>Exterior</option>
            </select></div>
          <div><div className="section-label">Conta custódia</div>
            <select className="k-select">
              <option>BTG Invest</option><option>XP Investimentos</option><option>Itaú</option>
            </select></div>
        </div>
        <div style={{display:"flex",gap:8,justifyContent:"flex-end"}}>
          <button className="btn-g" onClick={onClose}>Cancelar</button>
          <button className="btn-p">Salvar posição ▲</button>
        </div>
      </div>
    </div>
  );
}

// ── Dados mock Orçamento ──────────────────────────────────────────────────────
const budgets=[
  {cat:"Moradia",   limite:3500, gasto:3200, status:"OK"},
  {cat:"Alimentação",limite:2000,gasto:1980, status:"ALERTA"},
  {cat:"Saúde",    limite:1200, gasto:1500, status:"ESTOURO"},
  {cat:"Transporte",limite:1000,gasto:950,  status:"OK"},
  {cat:"Lazer",    limite:800,  gasto:650,  status:"OK"},
  {cat:"Educação", limite:500,  gasto:0,    status:"OK"},
];
const scoreData={
  total:72,
  detalhes:[
    {label:"Orçamento (todas as cat.)", pts:18,max:30,ok:false},
    {label:"Meta de poupança atingida", pts:25,max:25,ok:true},
    {label:"Caixa M2 ≥ 20%",           pts:20,max:20,ok:true},
    {label:"Sem gasto acima da média",  pts:0, max:15,ok:false},
    {label:"Sem parcela atrasada",      pts:10,max:10,ok:true},
  ]
};
const scoreHist=[
  {m:"Dez",v:58},{m:"Jan",v:63},{m:"Mar",v:68},
  {m:"Abr",v:71},{m:"Mai",v:72},
];
const poupancaHist=[
  {m:"Dez",v:14},{m:"Jan",v:18},{m:"Fev",v:22},
  {m:"Mar",v:25},{m:"Abr",v:19},{m:"Mai",v:33},
];
const alertas=[
  {icon:"⚠",title:"Saúde acima da média",desc:"R$ 1.500 vs média de R$ 890 nos últimos 3 meses (+69%)",tone:"neg"},
  {icon:"⚠",title:"Alimentação próxima do limite",desc:"99% do orçamento usado — 6 dias restantes no mês",tone:"warn"},
  {icon:"✓",title:"Taxa de poupança recorde",desc:"33% em maio — melhor resultado nos últimos 6 meses",tone:"pos"},
];

// ── PÁGINA: Orçamento ─────────────────────────────────────────────────────────
function Orcamento() {
  const [tab,setTab]=useState("orc");
  const [metaPoupanca,setMetaPoupanca]=useState(20);
  const [modalBud,setModalBud]=useState(null); // null | "new" | budget object

  const totalLimite=budgets.reduce((a,b)=>a+b.limite,0);
  const totalGasto =budgets.reduce((a,b)=>a+b.gasto,0);
  const pctGeral   =(totalGasto/totalLimite*100);
  const nEstouro   =budgets.filter(b=>b.status==="ESTOURO").length;
  const nAlerta    =budgets.filter(b=>b.status==="ALERTA").length;
  const taxaPoupanca=33.1;
  const caixaM2=26.4;

  const scoreColor=scoreData.total>=80?T.emerald:scoreData.total>=60?T.brass:
    scoreData.total>=40?T.warn:T.rust;
  const scoreLabel=scoreData.total>=80?"EXCELENTE":scoreData.total>=60?"BOM":
    scoreData.total>=40?"ATENÇÃO":"CRÍTICO";

  const BudBar=({b})=>{
    const pct=Math.min((b.gasto/b.limite*100),100);
    const overpct=b.gasto>b.limite?(b.gasto/b.limite*100)-100:0;
    const barColor=b.status==="ESTOURO"?T.rust:b.status==="ALERTA"?T.warn:T.emerald;
    const stColor =b.status==="ESTOURO"?T.rust:b.status==="ALERTA"?T.warn:T.emerald;
    return(
      <div style={{marginBottom:16}}>
        <div style={{display:"flex",justifyContent:"space-between",
          alignItems:"center",marginBottom:6}}>
          <div style={{display:"flex",alignItems:"center",gap:8}}>
            <span style={{fontSize:13,fontWeight:500,color:T.ink}}>{b.cat}</span>
            <span style={{fontSize:9,fontWeight:700,letterSpacing:".08em",
              padding:"2px 7px",borderRadius:5,
              background:`${stColor}18`,border:`1px solid ${stColor}45`,color:stColor}}>
              {b.status}
            </span>
          </div>
          <div style={{display:"flex",alignItems:"center",gap:8}}>
            <span className="mono" style={{fontSize:11,color:T.ink3}}>
              {fmtK(b.gasto)} / {fmtK(b.limite)}
            </span>
            <button onClick={()=>setModalBud(b)}
              style={{background:"rgba(255,255,255,.06)",border:`1px solid ${T.border}`,
                borderRadius:6,color:T.ink4,cursor:"pointer",fontSize:10,padding:"2px 8px"}}>
              ✏
            </button>
          </div>
        </div>
        <div style={{height:6,background:"rgba(255,255,255,.07)",borderRadius:3,overflow:"hidden",position:"relative"}}>
          <div style={{width:`${Math.min(pct,100)}%`,height:"100%",borderRadius:3,
            background:barColor,transition:"width .4s"}}/>
          {overpct>0&&(
            <div style={{position:"absolute",right:0,top:0,
              width:`${Math.min(overpct,30)}%`,height:"100%",
              background:T.rust,opacity:.4,borderRadius:3}}/>
          )}
        </div>
        <div style={{textAlign:"right",marginTop:3,fontSize:10,
          color:stColor,fontFamily:"'JetBrains Mono',monospace"}}>
          {(b.gasto/b.limite*100).toFixed(0)}%
        </div>
      </div>
    );
  };

  return(
    <div style={{flex:1,overflowY:"auto",padding:"28px 32px"}} className="fade">
      {/* Header */}
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:20}}>
        <div>
          <div className="serif" style={{fontSize:26,color:T.ink}}>Orçamento & Score</div>
          <div style={{fontSize:11,color:T.ink4,marginTop:4}}>comportamento financeiro · mai · 2026</div>
        </div>
        <div style={{display:"flex",gap:8,alignItems:"center"}}>
          <select className="k-select" style={{width:"auto",fontSize:12,padding:"7px 12px"}}>
            <option>maio</option><option>abril</option><option>março</option>
          </select>
          <select className="k-select" style={{width:"auto",fontSize:12,padding:"7px 12px"}}>
            <option>2026</option><option>2025</option>
          </select>
        </div>
      </div>

      {/* KPIs */}
      <div style={{display:"flex",gap:10,marginBottom:20}}>
        <KPICard label="Orçamentos ativos" value={String(budgets.length)}
          sub={`${nEstouro} estouro · ${nAlerta} alerta`}
          tone={nEstouro>0?"neg":nAlerta>0?"warn":""}/>
        <KPICard label="Taxa de poupança" value={`${taxaPoupanca}%`}
          sub={taxaPoupanca>=metaPoupanca?"✓ meta atingida":"abaixo da meta"}
          tone={taxaPoupanca>=metaPoupanca?"pos":"neg"}/>
        <KPICard label="Score financeiro" value={String(scoreData.total)}
          sub={scoreLabel}
          tone={scoreData.total>=80?"pos":scoreData.total>=60?"brass":"warn"}/>
        <KPICard label="Caixa M2" value={`${caixaM2}%`}
          sub={caixaM2>=20?"✓ acima do mínimo":"abaixo do M2"}
          tone={caixaM2>=20?"pos":"neg"}/>
      </div>

      {/* Tabs */}
      <div style={{display:"flex",gap:0,marginBottom:20,background:"rgba(255,255,255,.04)",
        borderRadius:12,padding:4,width:"fit-content"}}>
        {[["orc","Orçamentos"],["meta","Meta de Poupança"],
          ["score","Score Financeiro"],["alertas","Alertas"]].map(([id,l])=>(
          <button key={id} onClick={()=>setTab(id)}
            style={{padding:"7px 16px",borderRadius:9,border:"none",cursor:"pointer",
              fontSize:12,fontFamily:"'Geist',sans-serif",fontWeight:tab===id?600:400,
              background:tab===id?T.card:"transparent",
              color:tab===id?T.ink:T.ink3,transition:"all .15s",
              boxShadow:tab===id?"0 2px 8px rgba(0,0,0,.3)":"none",
              whiteSpace:"nowrap"}}>
            {l}
            {id==="alertas"&&nEstouro>0&&(
              <span style={{marginLeft:6,background:T.rust,color:"#fff",fontSize:9,
                fontWeight:700,padding:"1px 5px",borderRadius:999}}>
                {nEstouro}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* TAB: Orçamentos */}
      {tab==="orc"&&(
        <div style={{display:"grid",gridTemplateColumns:"1fr 280px",gap:16}}>
          {/* Barras */}
          <div style={{background:T.card,border:`1px solid ${T.border}`,
            borderRadius:20,padding:"20px 24px"}}>
            <div style={{display:"flex",justifyContent:"space-between",
              alignItems:"center",marginBottom:18}}>
              <div className="section-label" style={{margin:0}}>Controle de gastos · maio</div>
              <button className="btn-p btn-sm" onClick={()=>setModalBud("new")}>
                ＋ Novo orçamento
              </button>
            </div>
            {budgets.map((b,i)=><BudBar key={i} b={b}/>)}
          </div>

          {/* Resumo */}
          <div style={{display:"flex",flexDirection:"column",gap:12}}>
            <div style={{background:T.card,border:`1px solid ${T.border}`,
              borderRadius:20,padding:"20px 24px"}}>
              <div className="section-label">Resumo geral</div>
              <div className="mono" style={{fontSize:28,fontWeight:600,
                color:pctGeral>=100?T.rust:pctGeral>=80?T.warn:T.emerald,
                marginBottom:4}}>
                {pctGeral.toFixed(0)}%
              </div>
              <div style={{fontSize:11,color:T.ink4,marginBottom:14}}>do orçamento total usado</div>
              <div style={{height:6,background:"rgba(255,255,255,.07)",borderRadius:3,marginBottom:14}}>
                <div style={{width:`${Math.min(pctGeral,100)}%`,height:"100%",borderRadius:3,
                  background:pctGeral>=100?T.rust:pctGeral>=80?T.warn:T.emerald}}/>
              </div>
              {[["Total orçado",fmtK(totalLimite),T.ink],
                ["Total gasto",fmtK(totalGasto),pctGeral>=100?T.rust:T.ink2],
                ["Disponível",fmtK(totalLimite-totalGasto),T.emerald]].map(([l,v,c])=>(
                <div key={l} style={{display:"flex",justifyContent:"space-between",
                  padding:"6px 0",borderTop:`1px solid ${T.border}`}}>
                  <span style={{fontSize:11,color:T.ink4}}>{l}</span>
                  <span className="mono" style={{fontSize:12,fontWeight:600,color:c}}>{v}</span>
                </div>
              ))}
            </div>

            {/* Mini score */}
            <div style={{background:T.card,border:`1px solid ${T.border}`,
              borderRadius:20,padding:"20px 24px",textAlign:"center"}}>
              <div className="section-label">Score financeiro</div>
              <div style={{position:"relative",width:100,height:100,margin:"8px auto"}}>
                <svg width="100" height="100" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" r="42" fill="none"
                    stroke="rgba(255,255,255,.08)" strokeWidth="8"/>
                  <circle cx="50" cy="50" r="42" fill="none"
                    stroke={scoreColor} strokeWidth="8"
                    strokeDasharray={`${scoreData.total*2.64} 264`}
                    strokeLinecap="round"
                    transform="rotate(-90 50 50)"/>
                </svg>
                <div style={{position:"absolute",inset:0,display:"flex",
                  flexDirection:"column",alignItems:"center",justifyContent:"center"}}>
                  <div className="mono" style={{fontSize:24,fontWeight:700,color:scoreColor,lineHeight:1}}>
                    {scoreData.total}
                  </div>
                  <div style={{fontSize:9,color:T.ink4,marginTop:2}}>/ 100</div>
                </div>
              </div>
              <div style={{fontSize:11,fontWeight:700,letterSpacing:".1em",color:scoreColor}}>
                {scoreLabel}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB: Meta de Poupança */}
      {tab==="meta"&&(
        <div style={{display:"grid",gridTemplateColumns:"280px 1fr",gap:16}}>
          <div style={{background:T.card,border:`1px solid ${T.border}`,borderRadius:20,padding:"20px 24px"}}>
            <div className="section-label">Meta de poupança</div>
            <div style={{marginBottom:16}}>
              <div style={{display:"flex",justifyContent:"space-between",
                fontSize:11,color:T.ink4,marginBottom:8}}>
                <span>Meta: <span className="mono" style={{color:T.brass,fontWeight:600}}>{metaPoupanca}%</span></span>
                <span>Real: <span className="mono" style={{color:taxaPoupanca>=metaPoupanca?T.emerald:T.rust,fontWeight:600}}>{taxaPoupanca}%</span></span>
              </div>
              <input type="range" min="5" max="50" step="5" value={metaPoupanca}
                onChange={e=>setMetaPoupanca(+e.target.value)}
                style={{width:"100%",accentColor:T.brass}}/>
              <div style={{display:"flex",justifyContent:"space-between",
                fontSize:9,color:T.ink4,marginTop:2}}>
                <span>5%</span><span>50%</span>
              </div>
            </div>
            <div style={{textAlign:"center",margin:"16px 0"}}>
              <div className="mono" style={{fontSize:48,fontWeight:700,
                color:taxaPoupanca>=metaPoupanca?T.emerald:T.rust,lineHeight:1}}>
                {taxaPoupanca}%
              </div>
              <div style={{fontSize:11,color:T.ink4,marginTop:4}}>taxa real · maio</div>
            </div>
            <div style={{height:6,background:"rgba(255,255,255,.07)",borderRadius:3,marginBottom:8}}>
              <div style={{width:`${Math.min(taxaPoupanca/50*100,100)}%`,height:"100%",borderRadius:3,
                background:taxaPoupanca>=metaPoupanca?T.emerald:T.rust}}/>
            </div>
            <div style={{fontSize:11,fontWeight:600,
              color:taxaPoupanca>=metaPoupanca?T.emerald:T.rust}}>
              {taxaPoupanca>=metaPoupanca
                ?`✓ Meta atingida! +${(taxaPoupanca-metaPoupanca).toFixed(1)}pp acima`
                :`Faltam ${(metaPoupanca-taxaPoupanca).toFixed(1)}pp para a meta`}
            </div>
          </div>
          <div style={{background:T.card,border:`1px solid ${T.border}`,borderRadius:20,padding:"20px 24px"}}>
            <div className="section-label">Histórico 6 meses</div>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={poupancaHist} margin={{top:8,right:8,bottom:0,left:0}}>
                <XAxis dataKey="m" tick={{fontSize:10,fill:T.ink4}} axisLine={false} tickLine={false}/>
                <YAxis hide domain={[0,50]}/>
                <Tooltip content={<CustomTip/>}/>
                {/* Reference line for meta */}
                <Line type="monotone" dataKey="v" name="Poupança %" stroke={T.brass}
                  strokeWidth={2.5} dot={{fill:T.brass,r:4}} activeDot={{r:6}}/>
              </LineChart>
            </ResponsiveContainer>
            {/* Meta reference */}
            <div style={{display:"flex",alignItems:"center",gap:8,marginTop:8,
              padding:"8px 12px",background:"rgba(248,113,113,.08)",
              border:"1px solid rgba(248,113,113,.2)",borderRadius:8}}>
              <div style={{width:20,height:2,background:T.rust,borderRadius:1,
                borderTop:"1px dashed "+T.rust}}/>
              <span style={{fontSize:11,color:T.rust}}>Meta {metaPoupanca}%</span>
            </div>
          </div>
        </div>
      )}

      {/* TAB: Score Financeiro */}
      {tab==="score"&&(
        <div style={{display:"grid",gridTemplateColumns:"240px 1fr",gap:16}}>
          {/* Gauge */}
          <div style={{background:T.card,border:`1px solid ${T.border}`,
            borderRadius:20,padding:"24px",textAlign:"center"}}>
            <div className="section-label">Score financeiro</div>
            <div style={{position:"relative",width:140,height:140,margin:"12px auto"}}>
              <svg width="140" height="140" viewBox="0 0 140 140">
                <circle cx="70" cy="70" r="58" fill="none"
                  stroke="rgba(255,255,255,.08)" strokeWidth="10"/>
                <circle cx="70" cy="70" r="58" fill="none"
                  stroke={scoreColor} strokeWidth="10"
                  strokeDasharray={`${scoreData.total*3.644} 364.4`}
                  strokeLinecap="round" transform="rotate(-90 70 70)"/>
              </svg>
              <div style={{position:"absolute",inset:0,display:"flex",
                flexDirection:"column",alignItems:"center",justifyContent:"center"}}>
                <div className="mono" style={{fontSize:36,fontWeight:700,
                  color:scoreColor,lineHeight:1}}>{scoreData.total}</div>
                <div style={{fontSize:10,color:T.ink4,marginTop:2}}>pontos</div>
              </div>
            </div>
            <div style={{fontSize:12,fontWeight:700,letterSpacing:".12em",
              color:scoreColor,marginBottom:8}}>{scoreLabel}</div>
            <div style={{fontSize:10,color:T.ink4,lineHeight:1.5}}>
              Score calculado com base em orçamento, poupança, caixa M2, padrões e parcelas.
            </div>
          </div>

          {/* Breakdown */}
          <div style={{background:T.card,border:`1px solid ${T.border}`,borderRadius:20,padding:"20px 24px"}}>
            <div className="section-label">Breakdown dos critérios</div>
            {scoreData.detalhes.map((d,i)=>(
              <div key={i} style={{marginBottom:14}}>
                <div style={{display:"flex",justifyContent:"space-between",
                  alignItems:"center",marginBottom:6}}>
                  <div style={{display:"flex",alignItems:"center",gap:8}}>
                    <span style={{fontSize:13,color:d.ok?T.emerald:T.rust,fontWeight:600}}>
                      {d.ok?"✓":"✗"}
                    </span>
                    <span style={{fontSize:12,color:d.ok?T.ink:T.ink3}}>{d.label}</span>
                  </div>
                  <span className="mono" style={{fontSize:11,
                    color:d.ok?T.emerald:T.rust,fontWeight:600}}>
                    {d.pts}/{d.max}
                  </span>
                </div>
                <div style={{height:5,background:"rgba(255,255,255,.07)",borderRadius:3}}>
                  <div style={{width:`${(d.pts/d.max)*100}%`,height:"100%",borderRadius:3,
                    background:d.ok?T.emerald:T.rust,transition:"width .4s"}}/>
                </div>
              </div>
            ))}
            <div style={{marginTop:20}}>
              <div className="section-label">Evolução do score · 6 meses</div>
              <ResponsiveContainer width="100%" height={100}>
                <LineChart data={scoreHist}>
                  <XAxis dataKey="m" tick={{fontSize:9,fill:T.ink4}} axisLine={false} tickLine={false}/>
                  <YAxis hide domain={[0,100]}/>
                  <Tooltip content={<CustomTip/>}/>
                  <Line type="monotone" dataKey="v" name="Score" stroke={T.brass}
                    strokeWidth={2} dot={{fill:T.brass,r:3}} activeDot={{r:5}}/>
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* TAB: Alertas */}
      {tab==="alertas"&&(
        <div style={{display:"flex",flexDirection:"column",gap:10}}>
          {alertas.map((a,i)=>{
            const c=a.tone==="neg"?T.rust:a.tone==="warn"?T.warn:T.emerald;
            return(
              <div key={i} style={{background:T.card,border:`1px solid ${c}30`,
                borderRadius:16,padding:"16px 20px",
                display:"flex",alignItems:"flex-start",gap:14}}>
                <div style={{width:36,height:36,borderRadius:10,flexShrink:0,
                  background:`${c}18`,border:`1px solid ${c}40`,
                  display:"flex",alignItems:"center",justifyContent:"center",fontSize:16}}>
                  {a.icon}
                </div>
                <div>
                  <div style={{fontSize:13,fontWeight:600,color:T.ink,marginBottom:4}}>{a.title}</div>
                  <div style={{fontSize:12,color:T.ink3,lineHeight:1.5}}>{a.desc}</div>
                </div>
                <div style={{marginLeft:"auto",flexShrink:0}}>
                  <div style={{fontSize:9,fontWeight:700,letterSpacing:".08em",
                    padding:"3px 8px",borderRadius:5,
                    background:`${c}18`,border:`1px solid ${c}40`,color:c}}>
                    {a.tone==="neg"?"CRÍTICO":a.tone==="warn"?"ATENÇÃO":"POSITIVO"}
                  </div>
                </div>
              </div>
            );
          })}
          <div style={{padding:"16px 20px",background:"rgba(255,255,255,.02)",
            border:`1px dashed ${T.border}`,borderRadius:16,
            fontSize:12,color:T.ink4,textAlign:"center"}}>
            Alertas são gerados automaticamente comparando os gastos do mês atual com a média dos 3 meses anteriores.
          </div>
        </div>
      )}

      {/* Modal orçamento */}
      {modalBud&&(
        <div className="modal-bg" onClick={e=>{if(e.target===e.currentTarget)setModalBud(null)}}>
          <div className="modal" style={{width:420}}>
            <div style={{display:"flex",justifyContent:"space-between",
              alignItems:"center",marginBottom:20}}>
              <div>
                <div style={{fontSize:16,fontWeight:600,color:T.ink}}>
                  {modalBud==="new"?"Novo orçamento":"Editar orçamento"}
                </div>
                <div style={{fontSize:11,color:T.ink4,marginTop:2}}>limite mensal por categoria</div>
              </div>
              <button onClick={()=>setModalBud(null)}
                style={{background:"none",border:"none",color:T.ink3,fontSize:18,cursor:"pointer"}}>✕</button>
            </div>
            <div style={{marginBottom:12}}>
              <div className="section-label">Categoria</div>
              <select className="k-select" defaultValue={modalBud!=="new"?modalBud.cat:""}>
                {Object.keys(CAT).map(c=><option key={c}>{c}</option>)}
              </select>
            </div>
            <div style={{marginBottom:12}}>
              <div className="section-label">Limite mensal (R$)</div>
              <input className="k-input mono" placeholder="500,00"
                defaultValue={modalBud!=="new"?modalBud.limite:""}
                style={{fontSize:15}}/>
            </div>
            <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:10,marginBottom:20}}>
              <div><div className="section-label">Mês</div>
                <select className="k-select">
                  {["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
                    .map((m,i)=><option key={i} selected={i===4}>{m}</option>)}
                </select>
              </div>
              <div><div className="section-label">Ano</div>
                <select className="k-select"><option>2026</option><option>2025</option></select>
              </div>
            </div>
            <div style={{display:"flex",gap:8,justifyContent:"space-between"}}>
              {modalBud!=="new"&&(
                <button className="btn-g" style={{color:T.rust,borderColor:"rgba(248,113,113,.3)",fontSize:12}}>
                  Remover
                </button>
              )}
              <div style={{display:"flex",gap:8,marginLeft:"auto"}}>
                <button className="btn-g" onClick={()=>setModalBud(null)}>Cancelar</button>
                <button className="btn-p">Salvar orçamento</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Dados mock Saúde ──────────────────────────────────────────────────────────
const profissionais=[
  {id:"p1",nome:"Dra. Ana Souza",esp:"Fonoaudiologia",crp:"CREFITO 12345"},
  {id:"p2",nome:"Dr. Bruno Lima",esp:"Terapia Ocupacional",crp:"CREFITO 67890"},
  {id:"p3",nome:"Dra. Carla Melo",esp:"Psicologia Infantil",crp:"CRP 08/54321"},
  {id:"p4",nome:"Dr. Diego Nunes",esp:"ABA",crp:"CRP 08/98765"},
];
const sessoes=[
  {d:"22/Mai",prof:"p1",val:350,status:"sem_sol",nf:"NF-2024"},
  {d:"20/Mai",prof:"p2",val:280,status:"sem_sol",nf:"REC-089"},
  {d:"18/Mai",prof:"p1",val:350,status:"pendente",nf:"NF-2023",prot:"BRA-2026-0412"},
  {d:"15/Mai",prof:"p3",val:220,status:"reembolsado",nf:"NF-2022",prot:"BRA-2026-0401",recv:198},
  {d:"10/Mai",prof:"p4",val:420,status:"parcial",nf:"NF-2021",prot:"BRA-2026-0389",recv:300},
  {d:"08/Mai",prof:"p2",val:280,status:"reembolsado",nf:"REC-085",prot:"BRA-2026-0380",recv:252},
  {d:"05/Mai",prof:"p1",val:350,status:"reembolsado",nf:"NF-2020",prot:"BRA-2026-0371",recv:315},
];
const solicitacoes=[
  {id:"s1",prof:"p1",data:"15/Mai",valor:700,recv:630,status:"reembolsado",prot:"BRA-2026-0412",gap:0},
  {id:"s2",prof:"p4",data:"10/Mai",valor:840,recv:600,status:"parcial",prot:"BRA-2026-0389",gap:240},
  {id:"s3",prof:"p2",data:"18/Mai",valor:560,recv:null,status:"pendente",prot:"BRA-2026-0401",gap:560},
  {id:"s4",prof:"p3",data:"08/Mai",valor:440,recv:396,status:"reembolsado",prot:"BRA-2026-0380",gap:0},
];
const STATUS_DEF={
  sem_sol:  {label:"SEM SOL.",color:"#FCD34D"},
  pendente: {label:"PENDENTE",color:"#F97316"},
  parcial:  {label:"PARCIAL", color:"#7FB3C8"},
  reembolsado:{label:"REIMB.", color:"#10B981"},
};
const PROV_COLORS={
  "auto":"#D9B26F","claude":"#D4A27A","gemini":"#4285F4",
  "gpt4o":"#10A37F","qwen":"#6366F1","kimi":"#8B5CF6",
};

// ── PÁGINA: AI Consilium ──────────────────────────────────────────────────────
function AIConsilium() {
  const [provider,setProvider]=useState("auto");
  const [regime,setRegime]=useState("NEUTRO");
  const [confidence,setConfidence]=useState("MODERADA");
  const [msgs,setMsgs]=useState([
    {role:"system",text:"WikiAgent Financeiro v2.0 · M1 Quant · M2 Governance · M3 Context · Anti-BS · Fragility Score"},
    {role:"assistant",text:"Pronto para análise. Qual ativo ou decisão você quer avaliar? Matemática ancora — narrativa sem evidência não altera decisão."},
  ]);
  const [input,setInput]=useState("");
  const [loading,setLoading]=useState(false);

  const providers=["auto","claude","gemini","gpt4o","qwen","kimi"];
  const provLabels={"auto":"Auto-routing","claude":"Claude","gemini":"Gemini","gpt4o":"GPT-4o","qwen":"Qwen","kimi":"Kimi"};
  const regimes=["BAIXA_VOLATILIDADE","NEUTRO","ALTA_VOLATILIDADE","CRISE"];
  const confidences=["BAIXA","MODERADA","ALTA","MUITO_ALTA"];

  const sendMsg=()=>{
    if(!input.trim())return;
    const userMsg={role:"user",text:input};
    setMsgs(m=>[...m,userMsg]);
    setInput("");
    setLoading(true);
    setTimeout(()=>{
      setMsgs(m=>[...m,{role:"assistant",text:`[${provLabels[provider==="auto"?"claude":provider]}] Análise em curso. Score M1: 0.73 · Regime: ${regime} · Confidence: ${confidence}. Com base nos dados quantitativos disponíveis, a tese apresenta fundamentos sólidos, mas o contexto de mercado sugere prudência no dimensionamento da posição. Recomendo limitar a 8% do portfólio dado o fragility score atual de 0.28.`}]);
      setLoading(false);
    },1200);
  };

  const engines=[
    {id:"M1",name:"Quant Engine",status:"ok",desc:"score 0.73"},
    {id:"M2",name:"Governance",status:"ok",desc:"limites ok"},
    {id:"M3",name:"Context",status:"warn",desc:regime},
    {id:"AB",name:"Anti-BS",status:"ok",desc:"ativo"},
    {id:"FR",name:"Fragility",status:"ok",desc:"0.28 · baixa"},
  ];

  return(
    <div style={{flex:1,display:"flex",flexDirection:"column",overflow:"hidden"}} className="fade">
      {/* Header controles */}
      <div style={{padding:"20px 28px 0",borderBottom:`1px solid ${T.border}`,flexShrink:0}}>
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:14}}>
          <div>
            <div style={{fontSize:16,fontWeight:600,color:T.ink}}>Consilium · M4</div>
            <div style={{fontSize:11,color:T.ink4,marginTop:2}}>auditoria histórica · multi-provider · WikiAgent</div>
          </div>
          {/* Engines strip */}
          <div style={{display:"flex",gap:6,flexWrap:"wrap",justifyContent:"flex-end"}}>
            {engines.map(e=>(
              <div key={e.id} style={{display:"flex",alignItems:"center",gap:5,
                padding:"4px 10px",borderRadius:6,
                background:e.status==="ok"?"rgba(16,185,129,.08)":"rgba(245,158,11,.08)",
                border:`1px solid ${e.status==="ok"?"rgba(16,185,129,.25)":"rgba(245,158,11,.25)"}`}}>
                <span className="mono" style={{fontSize:9,fontWeight:700,
                  color:e.status==="ok"?T.emerald:T.warn}}>{e.id}</span>
                <span style={{fontSize:10,color:T.ink3}}>{e.name}</span>
                <span className="mono" style={{fontSize:9,color:T.ink4}}>· {e.desc}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Provider + context selectors */}
        <div style={{display:"grid",gridTemplateColumns:"auto 1fr 1fr 1fr",gap:10,
          alignItems:"center",paddingBottom:14}}>
          {/* Provider pills */}
          <div style={{display:"flex",gap:4}}>
            {providers.map(p=>{
              const c=PROV_COLORS[p];
              return(
                <button key={p} onClick={()=>setProvider(p)}
                  style={{padding:"5px 10px",borderRadius:8,border:`1px solid ${provider===p?c:T.border}`,
                    background:provider===p?`${c}18`:"transparent",
                    color:provider===p?c:T.ink4,fontSize:11,fontWeight:600,
                    cursor:"pointer",fontFamily:"'Geist',sans-serif",transition:"all .12s",
                    whiteSpace:"nowrap"}}>
                  {provLabels[p]}
                </button>
              );
            })}
          </div>
          <select className="k-select" value={regime} onChange={e=>setRegime(e.target.value)}
            style={{fontSize:12}}>
            {regimes.map(r=><option key={r}>{r}</option>)}
          </select>
          <select className="k-select" value={confidence} onChange={e=>setConfidence(e.target.value)}
            style={{fontSize:12}}>
            {confidences.map(c=><option key={c}>{c}</option>)}
          </select>
          <div style={{padding:"8px 12px",borderRadius:10,
            background:"rgba(16,185,129,.08)",border:"1px solid rgba(16,185,129,.2)",
            fontSize:11,color:T.emerald,fontWeight:500}}>
            ✓ Claude + Gemini + GPT-4o configurados
          </div>
        </div>
      </div>

      {/* Chat area */}
      <div style={{flex:1,overflowY:"auto",padding:"20px 28px",display:"flex",flexDirection:"column",gap:14}}>
        {msgs.map((m,i)=>(
          <div key={i} style={{display:"flex",
            justifyContent:m.role==="user"?"flex-end":"flex-start"}}>
            {m.role==="system"?(
              <div style={{background:"rgba(41,97,199,.08)",border:"1px solid rgba(41,97,199,.2)",
                borderRadius:10,padding:"8px 14px",maxWidth:"80%"}}>
                <span className="mono" style={{fontSize:10,color:T.sea}}>{m.text}</span>
              </div>
            ):m.role==="user"?(
              <div style={{background:"rgba(217,178,111,.12)",border:"1px solid rgba(217,178,111,.2)",
                borderRadius:"14px 14px 4px 14px",padding:"10px 16px",maxWidth:"70%"}}>
                <div style={{fontSize:13,color:T.ink,lineHeight:1.55}}>{m.text}</div>
              </div>
            ):(
              <div style={{display:"flex",gap:10,maxWidth:"78%"}}>
                <div style={{width:28,height:28,borderRadius:8,flexShrink:0,
                  background:`${PROV_COLORS[provider==="auto"?"claude":provider]}22`,
                  border:`1px solid ${PROV_COLORS[provider==="auto"?"claude":provider]}44`,
                  display:"flex",alignItems:"center",justifyContent:"center",
                  fontSize:10,fontWeight:700,color:PROV_COLORS[provider==="auto"?"claude":provider],
                  marginTop:2}}>
                  {(provLabels[provider==="auto"?"claude":provider]||"AI")[0]}
                </div>
                <div style={{background:T.card,border:`1px solid ${T.border}`,
                  borderRadius:"4px 14px 14px 14px",padding:"12px 16px"}}>
                  <div style={{fontSize:10,color:T.ink4,marginBottom:6,display:"flex",gap:8}}>
                    <span className="mono">{provLabels[provider==="auto"?"claude":provider]}</span>
                    <span>·</span><span>{regime}</span><span>·</span><span>{confidence}</span>
                  </div>
                  <div style={{fontSize:13,color:T.ink2,lineHeight:1.6}}>{m.text}</div>
                </div>
              </div>
            )}
          </div>
        ))}
        {loading&&(
          <div style={{display:"flex",gap:10}}>
            <div style={{width:28,height:28,borderRadius:8,background:T.active,
              display:"flex",alignItems:"center",justifyContent:"center",fontSize:10,
              color:T.brass,fontWeight:700}}>
              {(provLabels[provider==="auto"?"claude":provider]||"AI")[0]}
            </div>
            <div style={{background:T.card,border:`1px solid ${T.border}`,
              borderRadius:"4px 14px 14px 14px",padding:"14px 18px",display:"flex",gap:4,alignItems:"center"}}>
              {[0,1,2].map(i=>(
                <div key={i} style={{width:6,height:6,borderRadius:"50%",background:T.brass,
                  animation:`pulse 1.2s ease-in-out ${i*0.2}s infinite`}}/>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div style={{padding:"16px 28px",borderTop:`1px solid ${T.border}`,flexShrink:0}}>
        <div style={{display:"flex",gap:10,alignItems:"flex-end"}}>
          <div style={{flex:1,background:"rgba(255,255,255,.04)",border:`1px solid ${T.border}`,
            borderRadius:14,padding:"10px 14px",transition:"border-color .15s"}}
            onFocus={e=>e.currentTarget.style.borderColor=T.brass}
            onBlur={e=>e.currentTarget.style.borderColor=T.border}>
            <textarea className="k-input" placeholder="Analise MXRF11 · PETR4 está cara? · Qual meu risco de concentração?"
              value={input} onChange={e=>setInput(e.target.value)}
              onKeyDown={e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();sendMsg()}}}
              style={{background:"transparent",border:"none",resize:"none",height:48,
                padding:0,boxShadow:"none",fontSize:13}}/>
            <div style={{fontSize:10,color:T.ink4,marginTop:4}}>
              ↵ Enter para enviar · Shift+Enter para nova linha · Anti-BS ativo
            </div>
          </div>
          <button className="btn-p" onClick={sendMsg} disabled={!input.trim()}
            style={{padding:"12px 20px",flexShrink:0,opacity:input.trim()?1:0.5}}>
            Enviar
          </button>
        </div>
        <div style={{marginTop:10,display:"flex",gap:8,flexWrap:"wrap"}}>
          {["Analise MXRF11","Estou dentro do M2?","Qual meu maior risco?","Compare BOVA11 vs IVVB11"].map(s=>(
            <button key={s} className="chip" onClick={()=>setInput(s)}
              style={{fontSize:10,background:"rgba(255,255,255,.04)",
                color:T.ink3,borderColor:T.border,padding:"4px 10px"}}>
              {s}
            </button>
          ))}
        </div>
      </div>
      <style>{`@keyframes pulse{0%,80%,100%{transform:scale(0.6);opacity:.4}40%{transform:scale(1);opacity:1}}`}</style>
    </div>
  );
}

// ── PÁGINA: Saúde ─────────────────────────────────────────────────────────────
function Saude() {
  const [tab,setTab]=useState("sessoes");
  const [filtroProf,setFiltroProf]=useState("");
  const [filtroStatus,setFiltroStatus]=useState("todos");
  const [modalSessao,setModalSessao]=useState(false);

  const totalPago=sessoes.reduce((a,s)=>a+s.val,0);
  const totalReemb=solicitacoes.filter(s=>s.status==="reembolsado").reduce((a,s)=>a+(s.recv||0),0);
  const semSol=sessoes.filter(s=>s.status==="sem_sol").length;
  const aReaver=solicitacoes.filter(s=>["pendente","parcial"].includes(s.status))
    .reduce((a,s)=>a+s.gap,0);

  const profMap=Object.fromEntries(profissionais.map(p=>[p.id,p]));

  const sessFiltradas=sessoes.filter(s=>{
    if(filtroProf&&s.prof!==filtroProf)return false;
    if(filtroStatus!=="todos"&&s.status!==filtroStatus)return false;
    return true;
  });

  return(
    <div style={{flex:1,overflowY:"auto",padding:"28px 32px"}} className="fade">
      {/* Header */}
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:20}}>
        <div>
          <div className="serif" style={{fontSize:26,color:T.ink}}>Saúde</div>
          <div style={{fontSize:11,color:T.ink4,marginTop:4}}>Pedro · TEA · Bradesco Saúde · reembolsos</div>
        </div>
        <button className="btn-p btn-sm" onClick={()=>setModalSessao(true)}>＋ Registrar sessão</button>
      </div>

      {/* KPIs */}
      <div style={{display:"flex",gap:10,marginBottom:20}}>
        <KPICard label="Pago em 2026" value={fmtBRL(totalPago)} sub={`${sessoes.length} sessões`} tone="neg"/>
        <KPICard label="Reembolsado" value={fmtBRL(totalReemb)} sub="Bradesco Saúde" tone="pos"/>
        <KPICard label="A reaver" value={fmtBRL(aReaver)} sub="pendente + parcial" tone="warn"/>
        <KPICard label="Sem solicitação" value={String(semSol)} sub="sessões em aberto" tone={semSol>0?"warn":""}/>
      </div>

      {/* Tabs */}
      <div style={{display:"flex",gap:0,marginBottom:20,background:"rgba(255,255,255,.04)",
        borderRadius:12,padding:4,width:"fit-content"}}>
        {[["sessoes","Sessões"],["sol","Solicitações de reembolso"],["prof","Profissionais"]].map(([id,l])=>(
          <button key={id} onClick={()=>setTab(id)}
            style={{padding:"7px 16px",borderRadius:9,border:"none",cursor:"pointer",
              fontSize:12,fontFamily:"'Geist',sans-serif",fontWeight:tab===id?600:400,
              background:tab===id?T.card:"transparent",
              color:tab===id?T.ink:T.ink3,transition:"all .15s",
              boxShadow:tab===id?"0 2px 8px rgba(0,0,0,.3)":"none"}}>
            {l}
          </button>
        ))}
      </div>

      {/* TAB: Sessões */}
      {tab==="sessoes"&&(
        <div>
          {/* Filtros */}
          <div style={{display:"flex",gap:8,marginBottom:14,flexWrap:"wrap"}}>
            <select className="k-select" value={filtroProf} onChange={e=>setFiltroProf(e.target.value)}
              style={{width:"auto",fontSize:12,padding:"6px 12px"}}>
              <option value="">Todos os profissionais</option>
              {profissionais.map(p=><option key={p.id} value={p.id}>{p.nome}</option>)}
            </select>
            <select className="k-select" value={filtroStatus} onChange={e=>setFiltroStatus(e.target.value)}
              style={{width:"auto",fontSize:12,padding:"6px 12px"}}>
              <option value="todos">Todos os status</option>
              <option value="sem_sol">Sem solicitação</option>
              <option value="pendente">Pendente</option>
              <option value="parcial">Parcial</option>
              <option value="reembolsado">Reembolsado</option>
            </select>
            {semSol>0&&(
              <div style={{padding:"6px 12px",borderRadius:10,
                background:"rgba(245,158,11,.1)",border:"1px solid rgba(245,158,11,.25)",
                fontSize:11,color:T.warn,display:"flex",alignItems:"center",gap:6}}>
                ⚠ {semSol} sessões sem solicitação de reembolso
              </div>
            )}
          </div>

          {/* Lista */}
          <div style={{background:T.card,border:`1px solid ${T.border}`,borderRadius:20,
            padding:"4px 20px"}}>
            {sessFiltradas.map((s,i)=>{
              const st=STATUS_DEF[s.status];
              const prof=profMap[s.prof];
              return(
                <div key={i} style={{display:"grid",gridTemplateColumns:"auto 1fr auto auto",
                  gap:14,alignItems:"center",padding:"12px 0",
                  borderBottom:i<sessFiltradas.length-1?`1px solid ${T.border}`:"none"}}>
                  {/* Badge status */}
                  <div style={{padding:"3px 8px",borderRadius:6,fontSize:9,fontWeight:700,
                    letterSpacing:".08em",background:`${st.color}18`,
                    border:`1px solid ${st.color}45`,color:st.color,
                    whiteSpace:"nowrap"}}>
                    {st.label}
                  </div>
                  {/* Profissional + info */}
                  <div>
                    <div style={{fontSize:13,fontWeight:500,color:T.ink}}>{prof?.nome||"—"}</div>
                    <div style={{fontSize:10.5,color:T.ink3,marginTop:1}}>
                      {s.d} · {prof?.esp} · {s.nf}
                      {s.prot&&<span className="mono" style={{color:T.sea,marginLeft:8}}>#{s.prot}</span>}
                    </div>
                  </div>
                  {/* Valor pago */}
                  <div style={{textAlign:"right"}}>
                    <div className="mono" style={{fontSize:13,fontWeight:600,color:T.rust}}>
                      {fmtBRL(s.val)}
                    </div>
                    {s.recv&&(
                      <div className="mono" style={{fontSize:10,color:T.emerald,marginTop:2}}>
                        +{fmtBRL(s.recv)} reimb.
                      </div>
                    )}
                  </div>
                  {/* Ação */}
                  {s.status==="sem_sol"&&(
                    <button className="btn-p" style={{fontSize:10,padding:"5px 12px",whiteSpace:"nowrap"}}>
                      Solicitar reembolso
                    </button>
                  )}
                  {s.status!=="sem_sol"&&(
                    <button className="btn-g" style={{fontSize:10,padding:"5px 12px"}}>Ver</button>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* TAB: Solicitações */}
      {tab==="sol"&&(
        <div>
          <div style={{display:"flex",gap:10,marginBottom:16,flexWrap:"wrap"}}>
            {[["reembolsado",T.emerald,"Reembolsado"],["parcial",T.sea,"Parcial"],
              ["pendente",T.warn,"Pendente"]].map(([s,c,l])=>{
              const n=solicitacoes.filter(r=>r.status===s).length;
              return(
                <div key={s} style={{padding:"10px 16px",borderRadius:12,
                  background:`${c}0D`,border:`1px solid ${c}30`,display:"flex",gap:10,alignItems:"center"}}>
                  <div className="mono" style={{fontSize:20,fontWeight:700,color:c}}>{n}</div>
                  <div style={{fontSize:11,color:T.ink3}}>{l}</div>
                </div>
              );
            })}
            <div style={{flex:1}}/>
            <button className="btn-p btn-sm">＋ Nova solicitação</button>
          </div>

          <div style={{display:"flex",flexDirection:"column",gap:10}}>
            {solicitacoes.map((sol,i)=>{
              const st=STATUS_DEF[sol.status];
              const prof=profMap[sol.prof];
              const gap=sol.gap;
              return(
                <div key={i} style={{background:T.card,border:`1px solid ${T.border}`,
                  borderRadius:16,padding:"16px 20px"}}>
                  <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:10}}>
                    <div style={{display:"flex",alignItems:"center",gap:10}}>
                      <div style={{padding:"3px 8px",borderRadius:6,fontSize:9,fontWeight:700,
                        letterSpacing:".08em",background:`${st.color}18`,
                        border:`1px solid ${st.color}45`,color:st.color}}>
                        {st.label}
                      </div>
                      <div>
                        <div style={{fontSize:13,fontWeight:500,color:T.ink}}>{prof?.nome}</div>
                        <div style={{fontSize:10.5,color:T.ink3,marginTop:1}}>
                          {sol.data}
                          {sol.prot&&<span className="mono" style={{color:T.sea,marginLeft:8}}>#{sol.prot}</span>}
                        </div>
                      </div>
                    </div>
                    <div style={{textAlign:"right"}}>
                      <div className="mono" style={{fontSize:14,fontWeight:600,color:T.ink}}>
                        {fmtBRL(sol.valor)}
                      </div>
                      <div style={{fontSize:10,color:T.ink4,marginTop:2}}>solicitado</div>
                    </div>
                  </div>

                  {/* Progress bar reembolso */}
                  <div style={{marginBottom:8}}>
                    <div style={{display:"flex",justifyContent:"space-between",
                      fontSize:10,color:T.ink4,marginBottom:5}}>
                      <span>Recebido: <span className="mono" style={{color:sol.recv?T.emerald:T.ink4}}>
                        {sol.recv?fmtBRL(sol.recv):"aguardando"}</span>
                      </span>
                      {gap>0&&<span style={{color:T.warn}}>Gap: <span className="mono">{fmtBRL(gap)}</span></span>}
                    </div>
                    <div style={{height:4,background:"rgba(255,255,255,.08)",borderRadius:2}}>
                      <div style={{width:sol.recv?`${(sol.recv/sol.valor*100).toFixed(0)}%`:"0%",
                        height:"100%",borderRadius:2,
                        background:sol.status==="reembolsado"?T.emerald:
                          sol.status==="parcial"?T.sea:T.warn,
                        transition:"width .4s"}}/>
                    </div>
                  </div>

                  {sol.status!=="reembolsado"&&(
                    <div style={{display:"flex",gap:8}}>
                      <button className="btn-g" style={{fontSize:11,padding:"5px 14px"}}>Atualizar</button>
                      <button className="btn-g" style={{fontSize:11,padding:"5px 14px"}}>Registrar recurso</button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* TAB: Profissionais */}
      {tab==="prof"&&(
        <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:12}}>
          {profissionais.map(p=>{
            const sessProf=sessoes.filter(s=>s.prof===p.id);
            const totalPago=sessProf.reduce((a,s)=>a+s.val,0);
            const pendentes=sessProf.filter(s=>s.status==="sem_sol").length;
            return(
              <div key={p.id} style={{background:T.card,border:`1px solid ${T.border}`,
                borderRadius:16,padding:"16px 20px"}}>
                <div style={{display:"flex",alignItems:"center",gap:12,marginBottom:12}}>
                  <div style={{width:40,height:40,borderRadius:12,
                    background:T.electricSoft,border:`1px solid rgba(59,130,246,.2)`,
                    display:"flex",alignItems:"center",justifyContent:"center",
                    fontSize:16,fontWeight:700,color:T.electric}}>
                    {p.nome[3]||"P"}
                  </div>
                  <div>
                    <div style={{fontSize:13,fontWeight:600,color:T.ink}}>{p.nome}</div>
                    <div style={{fontSize:11,color:T.ink3,marginTop:1}}>{p.esp}</div>
                    <div className="mono" style={{fontSize:9,color:T.ink4,marginTop:1}}>{p.crp}</div>
                  </div>
                </div>
                <div style={{display:"flex",justifyContent:"space-between",
                  padding:"8px 0",borderTop:`1px solid ${T.border}`}}>
                  <div>
                    <div style={{fontSize:9,color:T.ink4,marginBottom:2}}>Sessões 2026</div>
                    <div className="mono" style={{fontSize:13,fontWeight:600,color:T.ink}}>{sessProf.length}</div>
                  </div>
                  <div style={{textAlign:"center"}}>
                    <div style={{fontSize:9,color:T.ink4,marginBottom:2}}>Total pago</div>
                    <div className="mono" style={{fontSize:13,fontWeight:600,color:T.rust}}>{fmtK(totalPago)}</div>
                  </div>
                  <div style={{textAlign:"right"}}>
                    <div style={{fontSize:9,color:T.ink4,marginBottom:2}}>Pendentes</div>
                    <div className="mono" style={{fontSize:13,fontWeight:600,
                      color:pendentes>0?T.warn:T.emerald}}>{pendentes}</div>
                  </div>
                </div>
              </div>
            );
          })}
          <div style={{background:"rgba(255,255,255,.03)",border:`1px dashed ${T.border}`,
            borderRadius:16,padding:"24px",display:"flex",flexDirection:"column",
            alignItems:"center",justifyContent:"center",gap:8,cursor:"pointer",
            transition:"background .15s"}}
            onMouseEnter={e=>e.currentTarget.style.background="rgba(255,255,255,.05)"}
            onMouseLeave={e=>e.currentTarget.style.background="rgba(255,255,255,.03)"}>
            <div style={{fontSize:24,color:T.ink4}}>＋</div>
            <div style={{fontSize:12,color:T.ink4}}>Novo profissional</div>
          </div>
        </div>
      )}

      {/* Modal registrar sessão */}
      {modalSessao&&(
        <div className="modal-bg" onClick={e=>{if(e.target===e.currentTarget)setModalSessao(false)}}>
          <div className="modal">
            <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:20}}>
              <div>
                <div style={{fontSize:16,fontWeight:600,color:T.ink}}>Registrar sessão</div>
                <div style={{fontSize:11,color:T.ink4,marginTop:2}}>Pedro · TEA</div>
              </div>
              <button onClick={()=>setModalSessao(false)}
                style={{background:"none",border:"none",color:T.ink3,fontSize:18,cursor:"pointer"}}>✕</button>
            </div>
            <div style={{marginBottom:10}}>
              <div className="section-label">Profissional</div>
              <select className="k-select">
                {profissionais.map(p=><option key={p.id}>{p.nome} · {p.esp}</option>)}
              </select>
            </div>
            <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:10,marginBottom:10}}>
              <div><div className="section-label">Data da sessão</div>
                <input type="date" className="k-input" defaultValue="2026-05-25"/></div>
              <div><div className="section-label">Valor pago (R$)</div>
                <input className="k-input mono" placeholder="350,00" style={{fontSize:14}}/></div>
            </div>
            <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:10,marginBottom:14}}>
              <div><div className="section-label">N.º NF / recibo</div>
                <input className="k-input" placeholder="NF-2025"/></div>
              <div><div className="section-label">Lançar em Transações</div>
                <select className="k-select"><option>✅ Sim — conta Nubank</option><option>❌ Não</option></select>
              </div>
            </div>
            <div style={{marginBottom:18}}>
              <div className="section-label">Observações</div>
              <textarea className="k-input" placeholder="Tipo de terapia, evolução, notas…"
                style={{height:68,resize:"none"}}/>
            </div>
            <div style={{display:"flex",gap:8,justifyContent:"flex-end"}}>
              <button className="btn-g" onClick={()=>setModalSessao(false)}>Cancelar</button>
              <button className="btn-p">Registrar sessão ✚</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ── App root ──────────────────────────────────────────────────────────────────
export default function App() {
  const [page,setPage]=useState("dash");
  const [modal,setModal]=useState(null);

  const pages={
    dash:<Dashboard onAddTx={()=>setModal("tx")}/>,
    tx:<Transacoes onAddTx={()=>setModal("tx")}/>,
    inv:<Investimentos onAddInv={()=>setModal("inv")}/>,
    contas:<Contas onAddConta={()=>{}}/>,
    ai:<AIConsilium/>,
    saude:<Saude/>,
    orc:<Orcamento/>,
  };

  return(
    <>
      <style>{css}</style>
      <div style={{display:"flex",height:"100vh",overflow:"hidden",
        background:T.bg,fontFamily:"'Geist',sans-serif"}}>
        <Sidebar active={page} onNav={setPage}/>
        {pages[page]||(
          <div style={{flex:1,display:"flex",alignItems:"center",justifyContent:"center",
            flexDirection:"column",gap:12,color:T.ink3}}>
            <KlipperMark size={48}/>
            <div style={{fontSize:14,marginTop:8}}>{NAVITEMS.find(n=>n.id===page)?.l}</div>
            <div style={{fontSize:11,color:T.ink4}}>disponível no app Streamlit</div>
          </div>
        )}
      </div>
      {modal==="tx"  &&<AddTxModal  onClose={()=>setModal(null)}/>}
      {modal==="inv" &&<AddInvModal onClose={()=>setModal(null)}/>}
    </>
  );
}
