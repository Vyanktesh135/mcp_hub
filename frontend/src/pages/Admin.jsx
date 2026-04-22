import { useEffect, useState } from "react";
import { adminApi } from "../lib/api";
import { useAuth } from "../context/AuthContext";
import { Navigate } from "react-router-dom";
import Spinner from "../components/Spinner";

export default function Admin() {
  const { user } = useAuth();
  if (user?.role !== "admin") return <Navigate to="/" replace />;
  return <AdminPanel />;
}

function AdminPanel() {
  const { user: me } = useAuth();
  const [users,   setUsers]   = useState([]);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);
  const [busy,    setBusy]    = useState({});

  async function load() {
    setLoading(true);
    try { setUsers(await adminApi.listUsers()); }
    catch { setError("Failed to load users."); }
    finally { setLoading(false); }
  }

  useEffect(() => { load(); }, []);

  async function toggleRole(u) {
    setBusy(b => ({ ...b, [u.id]: true }));
    try {
      const updated = await adminApi.updateRole(u.id, u.role === "admin" ? "user" : "admin");
      setUsers(us => us.map(x => x.id === updated.id ? updated : x));
    } catch (e) {
      alert(e.response?.data?.detail || "Failed to update role");
    } finally {
      setBusy(b => ({ ...b, [u.id]: false }));
    }
  }

  async function toggleActive(u) {
    setBusy(b => ({ ...b, [u.id + "_a"]: true }));
    try {
      const updated = await adminApi.setActive(u.id, !u.is_active);
      setUsers(us => us.map(x => x.id === updated.id ? updated : x));
    } catch (e) {
      alert(e.response?.data?.detail || "Failed to update status");
    } finally {
      setBusy(b => ({ ...b, [u.id + "_a"]: false }));
    }
  }

  return (
    <div className="max-w-4xl animate-slide-up">
      <div className="mb-7">
        <h1 className="page-title">Admin</h1>
        <p className="page-subtitle mt-1">User management · {users.length} total</p>
      </div>

      {error && <p className="text-red-400 text-sm mb-4">{error}</p>}

      {loading ? (
        <div className="flex justify-center py-16"><Spinner size={24} /></div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-zinc-800">
                {["User", "Role", "Status", "Joined", "Actions"].map(h => (
                  <th key={h} className="text-left text-[10px] font-semibold text-zinc-600 uppercase tracking-wider px-4 py-3">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/60">
              {users.map(u => (
                <tr key={u.id} className="hover:bg-zinc-900/40 transition-colors">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2.5">
                      <div className="w-7 h-7 rounded-full bg-blue-600/20 border border-blue-500/30 flex items-center justify-center flex-shrink-0">
                        <span className="text-[10px] font-semibold text-blue-400 uppercase">
                          {u.email[0]}
                        </span>
                      </div>
                      <div>
                        <p className="text-zinc-200 text-xs font-medium">{u.email}</p>
                        {u.full_name && <p className="text-zinc-600 text-[11px]">{u.full_name}</p>}
                      </div>
                      {u.id === me?.id && (
                        <span className="text-[9px] px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30 font-semibold">
                          you
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded border ${
                      u.role === "admin"
                        ? "bg-amber-500/15 text-amber-400 border-amber-500/30"
                        : "bg-zinc-800 text-zinc-500 border-zinc-700"
                    }`}>
                      {u.role}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded border ${
                      u.is_active
                        ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30"
                        : "bg-red-500/10 text-red-400 border-red-500/20"
                    }`}>
                      {u.is_active ? "active" : "inactive"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-zinc-500 text-xs">
                    {new Date(u.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3">
                    {u.id !== me?.id && (
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => toggleRole(u)}
                          disabled={busy[u.id]}
                          className="text-xs px-2.5 py-1 rounded border border-zinc-700 text-zinc-400
                                     hover:border-amber-500/40 hover:text-amber-300 transition-colors
                                     disabled:opacity-40"
                        >
                          {busy[u.id] ? <Spinner size={10} /> : u.role === "admin" ? "Demote" : "Make Admin"}
                        </button>
                        <button
                          onClick={() => toggleActive(u)}
                          disabled={busy[u.id + "_a"]}
                          className={`text-xs px-2.5 py-1 rounded border transition-colors disabled:opacity-40 ${
                            u.is_active
                              ? "border-zinc-700 text-zinc-500 hover:border-red-500/40 hover:text-red-400"
                              : "border-zinc-700 text-zinc-500 hover:border-emerald-500/40 hover:text-emerald-400"
                          }`}
                        >
                          {busy[u.id + "_a"] ? <Spinner size={10} /> : u.is_active ? "Deactivate" : "Activate"}
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
