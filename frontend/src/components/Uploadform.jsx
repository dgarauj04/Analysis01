import React, { useState } from "react";
import api from "../api";

export default function UploadForm() {
  const [file, setFile] = useState(null);
  const [gabaritoFile, setGabaritoFile] = useState(null);
  const [prova, setProva] = useState("ENEM");
  const [ano, setAno] = useState(new Date().getFullYear());
  const [dia, setDia] = useState(1);
  const [materia, setMateria] = useState("Geral");
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setMsg(null);
    if (!file) { setMsg({ type: "error", text: "Selecione um arquivo PDF." }); return; }
    const form = new FormData();
    form.append("file", file);
    if (gabaritoFile) form.append("gabarito_file", gabaritoFile);
    form.append("prova", prova);
    form.append("ano", String(ano));
    form.append("dia", String(dia));
    form.append("materia", materia);

    try {
      setLoading(true);
      const res = await api.post("/upload", form, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setMsg({ type: "success", text: `Upload ok — questões extraídas: ${res.data.questions_extracted || "-"}` });
    } catch (err) {
      console.error(err);
      const text = err?.response?.data?.error || err.message || "Erro no upload";
      setMsg({ type: "error", text });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <form onSubmit={handleSubmit}>
        <label>Arquivo (PDF)</label>
        <input className="input" type="file" accept="application/pdf" onChange={(e)=>setFile(e.target.files[0])} />

        <label>Gabarito (opcional)</label>
        <input className="input" type="file" accept="application/pdf" onChange={(e)=>setGabaritoFile(e.target.files[0])} />

        <label>Prova</label>
        <input className="input" value={prova} onChange={e=>setProva(e.target.value)} />

        <label>Ano</label>
        <input className="input" type="number" value={ano} onChange={e=>setAno(e.target.value)} />

        <label>Dia</label>
        <input className="input" type="number" value={dia} onChange={e=>setDia(e.target.value)} />

        <label>Matéria</label>
        <input className="input" value={materia} onChange={e=>setMateria(e.target.value)} />

        <div style={{display:"flex", gap:10}}>
          <button className="button" type="submit" disabled={loading}>{loading ? "Enviando..." : "Upload"}</button>
        </div>
      </form>

      {msg && <div className="small" style={{marginTop:10, color: msg.type === "error" ? "crimson" : "green"}}>{msg.text}</div>}
      <div className="small" style={{marginTop:10}}>Dica: envie o arquivo de gabarito caso o sistema não detecte as respostas.</div>
    </div>
  );
}
