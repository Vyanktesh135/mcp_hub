import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { ThemeProvider, useTheme } from "./context/ThemeContext";
import { LanguageProvider, useLanguage } from "./context/LanguageContext";
import { useAuth } from "./context/AuthContext";

const NAV_SECTIONS = [
  {
    items: [
      { to: "/",         labelKey: "Overview",     icon: GridIcon },
      { to: "/registry", labelKey: "API Registry", icon: LayersIcon },
    ],
  },
  {
    headingKey: "Create",
    items: [
      { to: "/create/chat",   labelKey: "Chat Builder", icon: ChatIcon },
      { to: "/create/upload", labelKey: "Doc Upload",   icon: UploadIcon },
    ],
  },
  {
    headingKey: "Integrations",
    items: [
      { to: "/chatgpt", labelKey: "ChatGPT Tools", icon: SparkleIcon },
    ],
  },
  {
    headingKey: "System",
    items: [
      { to: "/monitor", labelKey: "Monitor", icon: MonitorIcon },
    ],
  },
];

const ADMIN_NAV = { to: "/admin", labelKey: "Admin", icon: ShieldIcon };

export default function App() {
  return (
    <ThemeProvider>
      <LanguageProvider>
        <AppShell />
      </LanguageProvider>
    </ThemeProvider>
  );
}

function AppShell() {
  return (
    <div className="flex h-screen bg-zinc-950 overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto bg-zinc-950">
        <div className="px-8 py-8 animate-fade-in">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

function Sidebar() {
  const { t } = useLanguage();
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <aside className="w-56 flex-shrink-0 flex flex-col border-r border-zinc-800 bg-zinc-950">
      {/* Logo */}
      <div className="h-14 flex items-center px-5 border-b border-zinc-800">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center shadow-sm">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
              <path d="M3 8h10M8 3v10" stroke="white" strokeWidth="2.2" strokeLinecap="round"/>
            </svg>
          </div>
          <div>
            <span className="font-semibold text-zinc-100 text-sm tracking-tight">MCP Hub</span>
            <span className="block text-[9px] text-zinc-600 uppercase tracking-widest -mt-0.5">middleware</span>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-5 overflow-y-auto">
        {NAV_SECTIONS.map((section, i) => (
          <div key={i}>
            {section.headingKey && (
              <p className="px-2 mb-1.5 text-[10px] font-semibold text-zinc-600 uppercase tracking-widest">
                {t(section.headingKey)}
              </p>
            )}
            <ul className="space-y-0.5">
              {section.items.map(({ to, labelKey, icon: Icon }) => (
                <li key={to}>
                  <NavLink
                    to={to}
                    end={to === "/"}
                    className={({ isActive }) =>
                      `flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-sm transition-colors
                       ${isActive
                         ? "bg-blue-600/15 text-blue-300 font-medium border border-blue-500/20"
                         : "text-zinc-500 hover:text-zinc-200 hover:bg-zinc-800/70"}`
                    }
                  >
                    <Icon />
                    {t(labelKey)}
                  </NavLink>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-3 py-3 border-t border-zinc-800 space-y-1">
        {/* Admin link */}
        {user?.role === "admin" && (
          <NavLink
            to={ADMIN_NAV.to}
            className={({ isActive }) =>
              `flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-sm transition-colors mb-1
               ${isActive
                 ? "bg-amber-500/15 text-amber-300 font-medium border border-amber-500/20"
                 : "text-zinc-500 hover:text-zinc-200 hover:bg-zinc-800/70"}`
            }
          >
            <ShieldIcon />
            <span className="text-xs">Admin</span>
            <span className="ml-auto text-[9px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30 font-semibold uppercase tracking-wider">
              admin
            </span>
          </NavLink>
        )}

        {/* User info + logout */}
        {user && (
          <div className="flex items-center justify-between px-2.5 py-2 rounded-lg mb-1">
            <div className="flex items-center gap-2 min-w-0">
              <div className="w-6 h-6 rounded-full bg-blue-600/20 border border-blue-500/30 flex items-center justify-center flex-shrink-0">
                <span className="text-[10px] font-semibold text-blue-400 uppercase">
                  {user.email[0]}
                </span>
              </div>
              <span className="text-xs text-zinc-400 truncate">{user.email}</span>
            </div>
            <button
              onClick={handleLogout}
              title="Sign out"
              className="ml-1 flex-shrink-0 text-zinc-600 hover:text-zinc-300 transition-colors"
            >
              <LogoutIcon />
            </button>
          </div>
        )}
        <LanguageToggle />
        <ThemeToggle />
        <a
          href="http://localhost:8000/docs"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 px-2.5 py-2 rounded-lg text-xs text-zinc-600
                     hover:text-zinc-400 hover:bg-zinc-800/60 transition-colors"
        >
          <ApiIcon />
          {t("API Reference")}
        </a>
      </div>
    </aside>
  );
}

function LanguageToggle() {
  const { lang, toggle } = useLanguage();
  const isJa = lang === "ja";
  return (
    <button
      onClick={toggle}
      className="w-full flex items-center justify-between px-2.5 py-2 rounded-lg
                 text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800/60
                 transition-colors group"
      title={isJa ? "Switch to English" : "日本語に切り替え"}
    >
      <span className="flex items-center gap-2 text-xs">
        <GlobeIcon />
        {isJa ? "日本語" : "English"}
      </span>
      <span className="flex items-center gap-0.5 text-[10px] font-mono">
        <span className={`px-1.5 py-0.5 rounded transition-colors ${!isJa ? "bg-blue-600/20 text-blue-400 border border-blue-500/30" : "text-zinc-700"}`}>
          EN
        </span>
        <span className="text-zinc-700">·</span>
        <span className={`px-1.5 py-0.5 rounded transition-colors ${isJa ? "bg-blue-600/20 text-blue-400 border border-blue-500/30" : "text-zinc-700"}`}>
          JA
        </span>
      </span>
    </button>
  );
}

function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  const { t } = useLanguage();
  const isDark = theme === "dark";

  return (
    <button
      onClick={toggleTheme}
      className="w-full flex items-center justify-between px-2.5 py-2 rounded-lg
                 text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800/60
                 transition-colors group"
      title={isDark ? t("Switch to light mode") : t("Switch to dark mode")}
    >
      <span className="flex items-center gap-2 text-xs">
        {isDark ? <MoonIcon /> : <SunIcon />}
        {isDark ? t("Dark mode") : t("Light mode")}
      </span>
      <span className={`relative inline-flex h-4 w-7 flex-shrink-0 rounded-full
                        border transition-colors duration-200
                        ${isDark ? "bg-zinc-800 border-zinc-700" : "bg-amber-400/20 border-amber-400/40"}`}>
        <span className={`absolute top-0.5 h-3 w-3 rounded-full shadow transition-transform duration-200
                          ${isDark ? "translate-x-0.5 bg-zinc-400" : "translate-x-3.5 bg-amber-400"}`} />
      </span>
    </button>
  );
}

/* ── Icons ── */
function GridIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 15 15" fill="none" className="shrink-0">
      <rect x="1" y="1" width="5.5" height="5.5" rx="1" stroke="currentColor" strokeWidth="1.4"/>
      <rect x="8.5" y="1" width="5.5" height="5.5" rx="1" stroke="currentColor" strokeWidth="1.4"/>
      <rect x="1" y="8.5" width="5.5" height="5.5" rx="1" stroke="currentColor" strokeWidth="1.4"/>
      <rect x="8.5" y="8.5" width="5.5" height="5.5" rx="1" stroke="currentColor" strokeWidth="1.4"/>
    </svg>
  );
}
function LayersIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 15 15" fill="none" className="shrink-0">
      <path d="M7.5 1.5L13 4.5L7.5 7.5L2 4.5L7.5 1.5Z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round"/>
      <path d="M2 7.5L7.5 10.5L13 7.5" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round"/>
      <path d="M2 10.5L7.5 13.5L13 10.5" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round"/>
    </svg>
  );
}
function ChatIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 15 15" fill="none" className="shrink-0">
      <path d="M2 2h11a1 1 0 0 1 1 1v7a1 1 0 0 1-1 1H5l-3 3V3a1 1 0 0 1 1-1Z"
        stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round"/>
    </svg>
  );
}
function UploadIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 15 15" fill="none" className="shrink-0">
      <path d="M7.5 10V2M4 5l3.5-3.5L11 5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M2 11v1a1 1 0 0 0 1 1h9a1 1 0 0 0 1-1v-1" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
    </svg>
  );
}
function SparkleIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 15 15" fill="none" className="shrink-0">
      <path d="M7.5 1.5v2M7.5 11.5v2M1.5 7.5h2M11.5 7.5h2M3.4 3.4l1.4 1.4M10.2 10.2l1.4 1.4M3.4 11.6l1.4-1.4M10.2 4.8l1.4-1.4"
        stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
      <circle cx="7.5" cy="7.5" r="2" stroke="currentColor" strokeWidth="1.4"/>
    </svg>
  );
}
function MonitorIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 15 15" fill="none" className="shrink-0">
      <rect x="1" y="2" width="13" height="9" rx="1.5" stroke="currentColor" strokeWidth="1.4"/>
      <path d="M5 13h5M7.5 11v2" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
    </svg>
  );
}
function ApiIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 15 15" fill="none" className="shrink-0">
      <path d="M3 7.5h9M9 4l3 3.5L9 11" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}
function GlobeIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 15 15" fill="none" className="shrink-0">
      <circle cx="7.5" cy="7.5" r="6" stroke="currentColor" strokeWidth="1.4"/>
      <path d="M7.5 1.5c-2 2-2 8 0 12M7.5 1.5c2 2 2 8 0 12" stroke="currentColor" strokeWidth="1.4"/>
      <path d="M1.5 7.5h12" stroke="currentColor" strokeWidth="1.4"/>
      <path d="M2 5h11M2 10h11" stroke="currentColor" strokeWidth="1.1"/>
    </svg>
  );
}
function MoonIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 15 15" fill="none" className="shrink-0">
      <path d="M13 9.5A6.5 6.5 0 0 1 5.5 2a6.5 6.5 0 1 0 7.5 7.5Z"
        stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round"/>
    </svg>
  );
}
function SunIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 15 15" fill="none" className="shrink-0">
      <circle cx="7.5" cy="7.5" r="2.5" stroke="currentColor" strokeWidth="1.4"/>
      <path d="M7.5 1v1.5M7.5 12.5V14M1 7.5h1.5M12.5 7.5H14M3 3l1 1M11 11l1 1M3 12l1-1M11 4l1-1"
        stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
    </svg>
  );
}
function LogoutIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 15 15" fill="none" className="shrink-0">
      <path d="M9 2H3a1 1 0 0 0-1 1v9a1 1 0 0 0 1 1h6" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
      <path d="M11 10l2.5-2.5L11 5M13.5 7.5H6" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}
function ShieldIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 15 15" fill="none" className="shrink-0">
      <path d="M7.5 1.5L2 4v4c0 3 2.5 5.5 5.5 5.5S13 11 13 8V4L7.5 1.5Z"
        stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round"/>
      <path d="M5 7.5l2 2 3-3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}
