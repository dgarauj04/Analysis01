import axios from "axios";

const base = import.meta.env.VITE_BACKEND_URL || "/api";

const api = axios.create({
  baseURL: base,
  headers: {
    "Accept": "application/json"
  }
});

export default api;
