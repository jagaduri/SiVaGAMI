
import React, { useState } from "react";

export default function ChatArea({ messages, onSend }){
  const [q,setQ]=useState("");
  return (<>
    <div className="ask">
      <div className="box">
        <input placeholder="Ask AI a question..." value={q} onChange={e=>setQ(e.target.value)} onKeyDown={e=>e.key==='Enter'&&onSend(q)} />
        <button onClick={()=>onSend(q)}>Send</button>
      </div>
    </div>
    <div className="chatWrap">
      <div className="chat"><div className="messages">
        {messages.map((m,i)=>(
          <div key={i} className={"msg "+(m.sender==="user"?"user":"")}>
            <span className="bubble">{m.text}</span>
          </div>
        ))}
        {messages.length===0 && <div style={{color:"#6b7280"}}>Start a conversation by asking a question above.</div>}
      </div></div>

      <div className="tools">
        <div className="row"><strong>Tools</strong></div>
        <div style={{height:160,border:"1px dashed var(--border)",display:"flex",alignItems:"center",justifyContent:"center",color:"var(--muted)"}}>
          (Add charts/controls here as needed)
        </div>
      </div>
    </div>
  </>);
}
