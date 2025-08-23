import React from "react";
import { Outlet, Link } from "react-router-dom";
import UploadForm from "./components/UploadForm";

export default function Analyzer() {
  return (
    <div className="app">
      <header>
        <h1>ENEM Analyzer</h1>
        <nav>
          <Link to="/">Provas</Link>
        </nav>
      </header>

      <main>
        <section className="upload-section">
          <h2>Upload de Prova</h2>
          <UploadForm />
        </section>

        <section className="content">
          <Outlet />
        </section>
      </main>

      <footer>
        <small>ENEM Analyzer • Frontend Vite + React</small>
      </footer>
    </div>
  );
}
