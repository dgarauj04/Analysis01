import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api";

export default function ProvaDetail(){
  const { id } = useParams();
  const [assuntos, setAssuntos] = useState(null);
  const [questoes, setQuestoes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(()=>{
    async function load() {
      setLoading(true);
      try {
        const [r1, r2] = await Promise.all([
          api.get(`/provas/${id}/assuntos`),
          api.get(`/provas/${id}/questoes`)
        ]);
        setAssuntos(r1.data);
        setQuestoes(r2.data || []);
      } catch (err) {
        console.error(err);
        alert("Erro ao carregar prova");
      } finally { setLoading(false); }
    }
    load();
  }, [id]);

  if (loading) return <div className="card">Carregando...</div>;

  return (
    <div>
      <div className="card">
        <h3>Assuntos sugeridos</h3>
        {assuntos ? (
          Object.entries(assuntos).map(([mat, data]) => (
            <div key={mat} style={{marginBottom:12}}>
              <strong>{mat}</strong> — <span className="small">Total questões: {data.total_questoes}</span>
              <ul>
                {data.top_assuntos.length === 0 && <li className="small">nenhum assunto detectado</li>}
                {data.top_assuntos.map((a,i)=>(
                  <li key={i}>
                    <b>{a.assunto}</b> (score: {a.score}) — exemplos:
                    <ul>
                      {a.exemplos.map((ex,j)=>(<li key={j} className="small">Q{ex.numero}: {ex.excerpt}...</li>))}
                    </ul>
                  </li>
                ))}
              </ul>
            </div>
          ))
        ) : <div>Nenhum assunto encontrado.</div>}
      </div>

      <div className="card">
        <h3>Questões</h3>
        <table>
          <thead><tr><th>#</th><th>Enunciado</th><th>Gabarito</th><th>Matéria</th><th>Assunto</th></tr></thead>
          <tbody>
            {questoes.map(q=>(
              <tr key={q.id||q.numero}>
                <td>{q.numero}</td>
                <td style={{maxWidth:600}}>{q.enunciado?.slice(0,300)}{q.enunciado && q.enunciado.length>300 ? "..." : ""}</td>
                <td>{q.gabarito||"?"}</td>
                <td>{q.materia||"-"}</td>
                <td>{q.assunto||"-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
