import { useEffect, useMemo, useState } from "react";
import "./App.css";

import { getDemoPlantsWithInsights } from "./api/plantBrainApi";


function App() {
  const [plants, setPlants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        setError(null);

        const data = await getDemoPlantsWithInsights();
        setPlants(data);
      } catch (err) {
        console.error(err);
        setError("Could not connect to the PlantBrain API.");
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  const stats = useMemo(() => {
    const needsAttention = plants.filter((plant) =>
      ["due", "overdue"].includes(
        plant.insight?.watering?.status
      )
    ).length;

    const onSchedule = plants.filter(
      (plant) =>
        plant.insight?.watering?.status === "not_due"
    ).length;

    const learning = plants.filter(
      (plant) =>
        plant.insight?.watering?.status === "unknown"
    ).length;

    return {
      total: plants.length,
      needsAttention,
      onSchedule,
      learning,
    };
  }, [plants]);

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">P</div>

          <div>
            <h1>PlantBrain</h1>
            <span>Plant intelligence</span>
          </div>
        </div>

        <nav className="navigation">
          <a className="nav-item active" href="#">
            Dashboard
          </a>

          <a className="nav-item" href="#">
            Plants
          </a>

          <a className="nav-item" href="#">
            Insights
          </a>
        </nav>

        <div className="sidebar-footer">
          <span
            className={`status-dot ${
              error ? "status-dot-error" : ""
            }`}
          />

          {error ? "API unavailable" : "API connected"}
        </div>
      </aside>

      <main className="main-content">
        <header className="page-header">
          <div>
            <p className="eyebrow">
              PLANT CARE OVERVIEW
            </p>

            <h2>Good morning.</h2>

            <p className="subtitle">
              Here's what your plants need today.
            </p>
          </div>

          <button className="add-button">
            + Add plant
          </button>
        </header>

        <section className="summary-grid">
          <article className="summary-card">
            <span>Plants</span>
            <strong>{loading ? "—" : stats.total}</strong>
            <p>Currently tracked</p>
          </article>

          <article className="summary-card attention">
            <span>Needs attention</span>
            <strong>
              {loading ? "—" : stats.needsAttention}
            </strong>
            <p>Watering due or overdue</p>
          </article>

          <article className="summary-card">
            <span>On schedule</span>
            <strong>
              {loading ? "—" : stats.onSchedule}
            </strong>
            <p>Care pattern looks healthy</p>
          </article>

          <article className="summary-card">
            <span>Learning</span>
            <strong>
              {loading ? "—" : stats.learning}
            </strong>
            <p>Collecting more care data</p>
          </article>
        </section>

        <section className="plants-section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">
                YOUR COLLECTION
              </p>

              <h3>Plants</h3>
            </div>

            <button className="text-button">
              View all →
            </button>
          </div>

          {loading && (
            <div className="placeholder">
              <p>Loading plant intelligence...</p>
              <span>
                Fetching plants and insights from the API.
              </span>
            </div>
          )}

          {error && !loading && (
            <div className="placeholder error-state">
              <p>PlantBrain API unavailable</p>
              <span>{error}</span>
            </div>
          )}

          {!loading && !error && (
            <div className="plant-grid">
              {plants.map((plant) => (
                <PlantCard
                  key={plant.id}
                  plant={plant}
                />
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}


function PlantCard({ plant }) {
  const watering = plant.insight?.watering;
  const pattern = plant.insight?.pattern;
  const recommendation =
    plant.insight?.recommendation;

  const wateringStatus =
    watering?.status ?? "unknown";

  return (
    <article className="plant-card">
      <div className="plant-card-top">
        <div>
          <p className="plant-location">
            {plant.location || "No location"}
          </p>

          <h4>{plant.name}</h4>

          <p className="scientific-name">
            {plant.scientific_name ||
              plant.species ||
              "Species not specified"}
          </p>
        </div>

        <span
          className={`status-badge status-${wateringStatus}`}
        >
          {formatStatus(wateringStatus)}
        </span>
      </div>

      <div className="plant-metrics">
        <div>
          <span>Last watered</span>
          <strong>
            {formatDays(
              watering?.days_since_last_watering
            )}
          </strong>
        </div>

        <div>
          <span>Average cycle</span>
          <strong>
            {formatCycle(
              watering?.average_interval_days
            )}
          </strong>
        </div>
      </div>

      <div className="pattern-row">
        <span>Pattern</span>

        <strong>
          {formatStatus(
            pattern?.regularity ??
              "insufficient_data"
          )}
        </strong>
      </div>

      <div className="recommendation">
        <span>
          {recommendation?.priority || "low"} priority
        </span>

        <p>
          {recommendation?.message ||
            "PlantBrain is collecting more care data."}
        </p>
      </div>
    </article>
  );
}


function formatStatus(value) {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase()
    );
}


function formatDays(value) {
  if (value === null || value === undefined) {
    return "No data";
  }

  const rounded = Math.round(value);

  if (rounded === 0) {
    return "Today";
  }

  if (rounded === 1) {
    return "1 day ago";
  }

  return `${rounded} days ago`;
}


function formatCycle(value) {
  if (value === null || value === undefined) {
    return "Learning";
  }

  return `${value.toFixed(1)} days`;
}


export default App;