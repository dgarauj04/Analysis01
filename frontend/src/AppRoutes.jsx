import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Analyzer from "./Analyzer";
import ProvasList from "./components/ProvasList";
import ProvaDetail from "./components/ProvaDetail";
import "./styles.css";

export default function AppRoutes() {
return (
  <>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Analyzer />}>
          <Route index element={<ProvasList />} />
          <Route path="provas/:id" element={<ProvaDetail />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </>
);
}