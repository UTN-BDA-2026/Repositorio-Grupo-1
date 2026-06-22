import { useEffect, useState } from "react";

export default function Admin({ view, onViewChange }) {
  const [habits, setHabits] = useState([]);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [userFilter, setUserFilter] = useState("");
  const [skip, setSkip] = useState(0);
  const [limit, setLimit] = useState(10);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [backups, setBackups] = useState([]);
  const [selectedBackup, setSelectedBackup] = useState("");
  const [backupLoading, setBackupLoading] = useState(false);

  useEffect(() => {
    if (view === "admin") {
      loadHabits();
      loadBackups();
    }
  }, [view, skip, search, statusFilter, userFilter]);

  const loadHabits = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        skip: skip.toString(),
        limit: limit.toString(),
      });
      if (search) params.append("search", search);
      if (statusFilter) params.append("status", statusFilter);
      if (userFilter) params.append("user_id", userFilter);

      const response = await fetch(
        `http://localhost:8000/api/admin/habits?${params}`,
      );
      if (!response.ok) throw new Error("Error al cargar hábitos");

      const data = await response.json();
      setHabits(data.items);
      setTotal(data.total);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadBackups = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/admin/backups");
      if (!response.ok) throw new Error("Error al cargar backups");

      const data = await response.json();
      setBackups(data.backups);
    } catch (err) {
      console.error("Error loading backups:", err);
    }
  };

  const handleBackup = async () => {
    try {
      setBackupLoading(true);
      const response = await fetch("http://localhost:8000/api/admin/backup", {
        method: "POST",
      });
      if (!response.ok) throw new Error("Error al crear backup");

      const data = await response.json();
      alert(data.message);
      await loadBackups();
    } catch (err) {
      alert("Error: " + err.message);
    } finally {
      setBackupLoading(false);
    }
  };

  const handleRestore = async () => {
    if (!selectedBackup) {
      alert("Selecciona un backup para restaurar");
      return;
    }

    if (
      !window.confirm(
        "¿Estás seguro? Esto sobrescribirá la base de datos actual.",
      )
    ) {
      return;
    }

    try {
      setBackupLoading(true);
      const response = await fetch("http://localhost:8000/api/admin/restore", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ backup_file: selectedBackup }),
      });
      if (!response.ok) throw new Error("Error al restaurar backup");

      const data = await response.json();
      alert(data.message);
      await loadHabits();
    } catch (err) {
      alert("Error: " + err.message);
    } finally {
      setBackupLoading(false);
    }
  };

  const handleDelete = async (habitId) => {
    if (!window.confirm("¿Eliminar este hábito?")) return;

    try {
      const response = await fetch(
        `http://localhost:8000/api/habits/${habitId}`,
        { method: "DELETE" },
      );
      if (!response.ok) throw new Error("Error al eliminar");

      setHabits((prev) => prev.filter((h) => h.id !== habitId));
      setTotal((prev) => prev - 1);
    } catch (err) {
      alert("Error: " + err.message);
    }
  };

  const handleArchive = async (habitId) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/habits/${habitId}/archive`,
        { method: "PATCH", headers: { "Content-Type": "application/json" } },
      );
      if (!response.ok) throw new Error("Error al archivar");

      const updated = await response.json();
      setHabits((prev) => prev.map((h) => (h.id === habitId ? updated : h)));
    } catch (err) {
      alert("Error: " + err.message);
    }
  };

  const handleSearch = () => {
    setSkip(0);
  };

  const handleResetFilters = () => {
    setSearch("");
    setStatusFilter("");
    setUserFilter("");
    setSkip(0);
  };

  if (view !== "admin") return null;

  const totalPages = Math.ceil(total / limit);
  const currentPage = Math.floor(skip / limit) + 1;
  const uniqueUsers = [
    ...new Set(habits.map((h) => h.user_id).filter(Boolean)),
  ];

  return (
    <div className="container admin-container">
      <div className="header">
        <h1>🔧 Panel de Administración</h1>
        <button
          className="btn-dashboard"
          onClick={() => onViewChange("dashboard")}
        >
          📋 Dashboard
        </button>
      </div>

      <div className="admin-section">
        <h2>📊 Gestión de Hábitos</h2>

        <div className="filters-panel">
          <div className="filter-group">
            <input
              type="text"
              placeholder="Buscar por nombre o frecuencia..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="filter-input"
            />
            <button className="btn-search" onClick={handleSearch}>
              🔍 Buscar
            </button>
          </div>

          <div className="filter-row">
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setSkip(0);
              }}
              className="filter-select"
            >
              <option value="">Todos los estados</option>
              <option value="active">Activos</option>
              <option value="archived">Archivados</option>
            </select>

            <select
              value={userFilter}
              onChange={(e) => {
                setUserFilter(e.target.value);
                setSkip(0);
              }}
              className="filter-select"
            >
              <option value="">Todos los usuarios</option>
              {uniqueUsers.map((uid) => (
                <option key={uid} value={uid}>
                  {uid || "(sin usuario)"}
                </option>
              ))}
            </select>

            <button className="btn-reset" onClick={handleResetFilters}>
              🔄 Limpiar filtros
            </button>
          </div>
        </div>

        {error && <div className="error">{error}</div>}

        <div className="table-container">
          {loading ? (
            <p className="loading">Cargando...</p>
          ) : habits.length === 0 ? (
            <p className="empty">
              No hay hábitos que coincidan con los filtros
            </p>
          ) : (
            <table className="habits-table">
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Frecuencia</th>
                  <th>Usuario</th>
                  <th>Estado</th>
                  <th>Creado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {habits.map((habit) => (
                  <tr key={habit.id} className={`row-${habit.status}`}>
                    <td>{habit.name}</td>
                    <td>{habit.frequency}</td>
                    <td>{habit.user_id || "-"}</td>
                    <td>
                      <span className={`status-badge status-${habit.status}`}>
                        {habit.status === "active"
                          ? "✅ Activo"
                          : "📦 Archivado"}
                      </span>
                    </td>
                    <td>
                      {habit.date
                        ? new Date(habit.date).toLocaleDateString("es-AR", {
                            year: "2-digit",
                            month: "2-digit",
                            day: "2-digit",
                            hour: "2-digit",
                            minute: "2-digit",
                          })
                        : "-"}
                    </td>
                    <td>
                      <div className="action-buttons">
                        {habit.status === "active" && (
                          <button
                            className="btn-mini btn-archive"
                            onClick={() => handleArchive(habit.id)}
                            title="Archivar"
                          >
                            📦
                          </button>
                        )}
                        <button
                          className="btn-mini btn-delete"
                          onClick={() => handleDelete(habit.id)}
                          title="Eliminar"
                        >
                          🗑️
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="pagination">
          <button
            onClick={() => setSkip(Math.max(0, skip - limit))}
            disabled={skip === 0}
            className="btn-pagination"
          >
            ← Anterior
          </button>
          <span className="page-info">
            Página {currentPage} de {totalPages || 1} | Total: {total} hábitos
          </span>
          <button
            onClick={() => setSkip(skip + limit)}
            disabled={currentPage >= totalPages}
            className="btn-pagination"
          >
            Siguiente →
          </button>
        </div>
      </div>

      <div className="admin-section">
        <h2>💾 Backup y Restauración</h2>

        <div className="backup-panel">
          <button
            className="btn-backup"
            onClick={handleBackup}
            disabled={backupLoading}
          >
            {backupLoading ? "⏳ Creando..." : "💾 Crear Backup"}
          </button>

          {backups.length > 0 && (
            <div className="restore-group">
              <select
                value={selectedBackup}
                onChange={(e) => setSelectedBackup(e.target.value)}
                className="filter-select"
              >
                <option value="">Selecciona un backup para restaurar...</option>
                {backups.map((backup) => (
                  <option key={backup.path} value={backup.path}>
                    {backup.name} (
                    {new Date(backup.created).toLocaleString("es-AR")})
                  </option>
                ))}
              </select>

              <button
                className="btn-restore"
                onClick={handleRestore}
                disabled={backupLoading || !selectedBackup}
              >
                {backupLoading ? "⏳ Restaurando..." : "↩️ Restaurar"}
              </button>
            </div>
          )}

          {backups.length > 0 && (
            <div className="backups-list">
              <h3>Backups disponibles:</h3>
              <ul>
                {backups.map((backup) => (
                  <li key={backup.path}>
                    📁 {backup.name} - {backup.created}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
