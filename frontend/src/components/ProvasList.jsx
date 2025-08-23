import React, { useEffect, useState } from "react";
import api from "../api";
import Pagination from "./Pagination";
import { Link } from "react-router-dom";

export default function ProvasList() {
  const [provas, setProvas] = useState([]);
  const [meta, setMeta] = useState(null);
  const [page, setPage] = useState(1);
  const [perPage] = useState(10);
  const [ano, setAno] = useState("");
  const [nome, setNome] = useState("");
  const [loading, setLoading] = useState(false);

  async function fetchProvas(p=1) {
    setLoading(true);
    try {
      const params = { page: p, per_page: perPage };
      if (ano) params.ano = ano;
      if (nome) params.nome = nome;
      const res = await api.get("/provas", { params });
      setProvas(res.data.items || []);
      setMeta(res.data.meta || null);
      setPage(res.data.meta?.page || 1);
    } catch (err) {
      console.error(err);
      alert("Erro ao buscar provas");
    } finally {
      setLoading(false);
    }
  }

  useEffect(()=>{ fetchProvas(page); }, []);

  function onPageChange(p) {
    fetchProvas(p);
  }

  function applyFilters(e) {
    e.preventDefault();
    fetchProvas(1);
  }

  return (
    <div className="card">
      <h3>Provas</h3>
      <form onSubmit={applyFilters} style={{display:"flex", gap:8, marginBottom:10}}>
        <input className="input" placeholder="Ano" value={ano} onChange={e=>setAno(e.target.value)} />
        <input className="input" placeholder="Nome (ENEM...)" value={nome} onChange={e=>setNome(e.target.value)} />
        <button className="button" type="submit">Filtrar</button>
      </form>

      {loading ? <div>Carregando...</div> : (
        <>
          <table>
            <thead>
              <tr><th>ID</th><th>Nome</th><th>Ano</th><th>Dia</th><th>Origem</th></tr>
            </thead>
            <tbody>
              {provas.map(p=>(
                <tr key={p.id}>
                  <td>{p.id}</td>
                  <td><Link to={`/provas/${p.id}`}>{p.nome}</Link></td>
                  <td>{p.ano}</td>
                  <td>{p.dia}</td>
                  <td title={p.origem}>{p.origem ? p.origem.replace(/^.*\/data\//,'.../data/') : ""}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <Pagination meta={meta} onPageChange={onPageChange} />
        </>
      )}
    </div>
  );
}
