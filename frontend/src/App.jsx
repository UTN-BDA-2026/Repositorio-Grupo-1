import { useEffect, useState } from "react";
import "./App.css";

export default function App({ view, onViewChange }) {
  const [habits, setHabits] = useState([]);
  const [name, setName] = useState("");
  const [frequency, setFrequency] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadHabits();
  }, []);

  const loadHabits = async () => {
    try {
      setLoading(true);
      const response = await fetch("http://localhost:8000/api/habits");
      if (!response.ok) {
        throw new Error("No se pudieron cargar los hábitos.");
      }
      setHabits(await response.json());
    } catch (fetchError) {
      setError(fetchError.message);
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = async (event) => {
    event.preventDefault();
    setError("");
    try {
      const response = await fetch("http://localhost:8000/api/habits", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, frequency, status: "active" }),
      });
      if (!response.ok) {
        throw new Error("No se pudo crear el hábito.");
      }
      const created = await response.json();
      setHabits((previous) => [created, ...previous]);
      setName("");
      setFrequency("");
    } catch (submitError) {
      setError(submitError.message);
    }
  };

  const onDelete = async (habitId) => {
    if (!window.confirm("¿Estás seguro de que deseas eliminar este hábito?")) {
      return;
    }
    try {
      const response = await fetch(
        `http://localhost:8000/api/habits/${habitId}`,
        {
          method: "DELETE",
        },
      );
      if (!response.ok) {
        throw new Error("No se pudo eliminar el hábito.");
      }
      setHabits((previous) => previous.filter((h) => h.id !== habitId));
    } catch (deleteError) {
      setError(deleteError.message);
    }
  };

  const onArchive = async (habitId) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/habits/${habitId}/archive`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
        },
      );
      if (!response.ok) {
        throw new Error("No se pudo archivar el hábito.");
      }
      const updated = await response.json();
      setHabits((previous) =>
        previous.map((h) => (h.id === habitId ? updated : h)),
      );
    } catch (archiveError) {
      setError(archiveError.message);
    }
  };

  if (view !== "dashboard") return null;

  return (
    <div className="container">
      <div className="header">
        <h1>📋 Dashboard de Hábitos</h1>
        <button className="btn-admin" onClick={() => onViewChange("admin")}>
          🔧 Panel de Admin
        </button>
      </div>

      <form onSubmit={onSubmit} className="form">
        <input
          type="text"
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder="Nombre del hábito"
          required
        />
        <input
          type="text"
          value={frequency}
          onChange={(event) => setFrequency(event.target.value)}
          placeholder="Ej: daily, 3x/week"
          required
        />
        <button type="submit">➕ Crear hábito</button>
      </form>

      {error && <div className="error">{error}</div>}

      <div className="habits-list">
        <h2>Mis Hábitos ({habits.length})</h2>
        {loading ? (
          <p className="empty">Cargando...</p>
        ) : habits.length === 0 ? (
          <p className="empty">No hay hábitos registrados aún</p>
        ) : (
          <ul>
            {habits.map((habit) => (
              <li key={habit.id} className={`habit ${habit.status}`}>
                <span className="name">{habit.name}</span>
                <span className="frequency">{habit.frequency}</span>
                <span className="status">{habit.status}</span>
                <div className="actions">
                  {habit.status === "active" && (
                    <button
                      className="btn-archive"
                      onClick={() => onArchive(habit.id)}
                      title="Archivar"
                    >
                      📦
                    </button>
                  )}
                  <button
                    className="btn-delete"
                    onClick={() => onDelete(habit.id)}
                    title="Eliminar"
                  >
                    🗑️
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
