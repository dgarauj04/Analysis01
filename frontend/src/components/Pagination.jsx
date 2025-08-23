import React from "react";

export default function Pagination({meta, onPageChange}) {
  if (!meta) return null;
  const { page, pages } = meta;
  const prev = () => { if (page>1) onPageChange(page-1); }
  const next = () => { if (page<pages) onPageChange(page+1); }
  return (
    <div style={{display:"flex", gap:8, alignItems:"center", marginTop:8}}>
      <button className="button" onClick={prev} disabled={page<=1}>« Prev</button>
      <div className="small">Página {page} de {pages}</div>
      <button className="button" onClick={next} disabled={page>=pages}>Next »</button>
    </div>
  );
}
