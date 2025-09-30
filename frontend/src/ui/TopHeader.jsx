
import React from "react";
export default function TopHeader(){
  return (
    <div className="header">
      <div className="logo"><div className="dot"></div><div>CIBC</div></div>
      <div className="right"><span>EN</span><div style={{width:28,height:28,borderRadius:999,background:"#fff",color:"#000",display:"flex",alignItems:"center",justifyContent:"center"}}>HB</div></div>
    </div>
  );
}
