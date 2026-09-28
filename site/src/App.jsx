import { useState, createContext, useContext } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { ScrollToTop } from "./hooks";
import Layout from "./components/Layout";
import Home from "./pages/Home";
import KonkursTest from "./pages/KonkursTest";
import Progress from "./pages/Progress";
import { PracticeList, PracticeTypeList, PracticeExercise } from "./pages/Practice";
import NotFound from "./pages/NotFound";
import QuestHome from "./pages/quest/QuestHome";
import QuestExercise from "./pages/quest/QuestExercise";
import QuestPlacement from "./pages/quest/QuestPlacement";
import OjajHome from "./pages/ojaj/OjajHome";
import { OJAJ_PRACTICE_CONFIG, OJAJ_TEST_CONFIG } from "./lib/ojaj";

const USERS = [
  { name: "Tadzio", password: "smart1" },
  { name: "Zosia", password: "smart2" },
  { name: "Lidia", password: "smart3", questOnly: true },
];

const UserContext = createContext(null);
export const useUser = () => useContext(UserContext);

function Gate({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("smarten_user");
    return USERS.find((u) => u.name === saved) || null;
  });
  const [val, setVal] = useState("");
  const [err, setErr] = useState(false);

  if (user) return <UserContext.Provider value={user}>{typeof children === "function" ? children(user) : children}</UserContext.Provider>;

  const submit = (e) => {
    e.preventDefault();
    const found = USERS.find((u) => u.password === val);
    if (found) {
      localStorage.setItem("smarten_user", found.name);
      setUser(found);
    } else {
      setErr(true);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "#0a0a12",
        fontFamily: "'DM Sans', sans-serif",
      }}
    >
      <form onSubmit={submit} style={{ textAlign: "center" }}>
        <h1 style={{ fontSize: 24, fontWeight: 800, color: "#e8e8f0", marginBottom: 24 }}>
          SmartEn
        </h1>
        <input
          type="password"
          placeholder="Haslo"
          value={val}
          onChange={(e) => { setVal(e.target.value); setErr(false); }}
          autoFocus
          style={{
            padding: "10px 16px",
            fontSize: 16,
            borderRadius: 8,
            border: err ? "2px solid #e05050" : "2px solid #2a2a3a",
            background: "#12121e",
            color: "#e8e8f0",
            outline: "none",
            width: 220,
          }}
        />
        <button
          type="submit"
          style={{
            marginLeft: 8,
            padding: "10px 20px",
            fontSize: 16,
            borderRadius: 8,
            border: "none",
            background: "#3a3aff",
            color: "#fff",
            cursor: "pointer",
            fontWeight: 600,
          }}
        >
          OK
        </button>
      </form>
    </div>
  );
}

function QuestOnlyRoutes() {
  return (
    <Layout>
      <ScrollToTop />
      <Routes>
        <Route path="/quest" element={<QuestHome />} />
        <Route path="/quest/placement" element={<QuestPlacement />} />
        <Route path="/quest/:track/:id" element={<QuestExercise />} />
        <Route path="*" element={<Navigate to="/quest" replace />} />
      </Routes>
    </Layout>
  );
}

function FullRoutes() {
  return (
    <Layout>
      <ScrollToTop />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/postepy" element={<Progress />} />
        <Route path="/cwiczenia" element={<PracticeList />} />
        <Route path="/cwiczenia/:type" element={<PracticeTypeList />} />
        <Route path="/cwiczenia/:type/:id" element={<PracticeExercise />} />
        <Route path="/quest" element={<QuestHome />} />
        <Route path="/quest/placement" element={<QuestPlacement />} />
        <Route path="/quest/:track/:id" element={<QuestExercise />} />
        {/* OJAJ, the second competition. These sit above /:year/:stage so an
            OJAJ paper is not mistaken for a kuratoryjny year. */}
        <Route path="/ojaj" element={<OjajHome />} />
        <Route path="/ojaj/cwiczenia/:id" element={<PracticeExercise config={OJAJ_PRACTICE_CONFIG} />} />
        <Route path="/ojaj/:year/:stage" element={<KonkursTest config={OJAJ_TEST_CONFIG} />} />
        <Route path="/:year/:stage" element={<KonkursTest />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Layout>
  );
}

export default function App() {
  return (
    <Gate>
      {(user) => user.questOnly ? <QuestOnlyRoutes /> : <FullRoutes />}
    </Gate>
  );
}
