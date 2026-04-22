import { createContext, useContext, useEffect, useState } from "react";
import { authApi } from "../lib/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user,    setUser]    = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("mcp_token");
    if (!token) { setLoading(false); return; }
    authApi.me()
      .then(setUser)
      .catch(() => localStorage.removeItem("mcp_token"))
      .finally(() => setLoading(false));
  }, []);

  async function login(email, password) {
    const { access_token } = await authApi.login(email, password);
    localStorage.setItem("mcp_token", access_token);
    const me = await authApi.me();
    setUser(me);
  }

  async function register(email, password, fullName) {
    const { access_token } = await authApi.register(email, password, fullName);
    localStorage.setItem("mcp_token", access_token);
    const me = await authApi.me();
    setUser(me);
  }

  function logout() {
    localStorage.removeItem("mcp_token");
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
