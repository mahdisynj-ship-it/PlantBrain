import {
  useEffect,
  useMemo,
  useState,
} from "react";

import "./App.css";

import {
  getDemoPlantsWithInsights,
  getPlantDetailData,
} from "./api/plantBrainApi";
import CareVisualizations from "./components/CareVisualizations";


function App() {
  const [plants, setPlants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [selectedPlant, setSelectedPlant] =
    useState(null);

  const [plantDetail, setPlantDetail] =
    useState(null);

  const [detailLoading, setDetailLoading] =
    useState(false);

  const [detailError, setDetailError] =
    useState(null);

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        setError(null);

        const data =
          await getDemoPlantsWithInsights();

        setPlants(data);
      } catch (err) {
        console.error(err);

        setError(
          "Could not connect to the PlantBrain API."
        );
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  async function openPlantDetail(plant) {
    try {
      setSelectedPlant(plant);
      setPlantDetail(null);
      setDetailLoading(true);
      setDetailError(null);

      const detail =
        await getPlantDetailData(plant);

      setPlantDetail(detail);
    } catch (err) {
      console.error(err);

      setDetailError(
        "Could not load plant detail data."
      );
    } finally {
      setDetailLoading(false);
    }
  }

  function closePlantDetail() {
    setSelectedPlant(null);
    setPlantDetail(null);
    setDetailError(null);
  }

  if (selectedPlant) {
    return (
      <AppLayout
        error={detailError}
        activeSection="plants"
      >
        <PlantDetail
          plant={
            plantDetail ||
            selectedPlant
          }
          loading={detailLoading}
          error={detailError}
          onBack={closePlantDetail}
        />
      </AppLayout>
    );
  }

  return (
    <AppLayout
      error={error}
      activeSection="dashboard"
    >
      <Dashboard
        plants={plants}
        loading={loading}
        error={error}
        onSelectPlant={openPlantDetail}
      />
    </AppLayout>
  );
}


function AppLayout({
  children,
  error,
  activeSection,
}) {
  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            P
          </div>

          <div>
            <h1>PlantBrain</h1>
            <span>
              Plant intelligence
            </span>
          </div>
        </div>

        <nav className="navigation">
          <a
            className={`nav-item ${
              activeSection === "dashboard"
                ? "active"
                : ""
            }`}
            href="#"
          >
            Dashboard
          </a>

          <a
            className={`nav-item ${
              activeSection === "plants"
                ? "active"
                : ""
            }`}
            href="#"
          >
            Plants
          </a>

          <a
            className="nav-item"
            href="#"
          >
            Insights
          </a>
        </nav>

        <div className="sidebar-footer">
          <span
            className={`status-dot ${
              error
                ? "status-dot-error"
                : ""
            }`}
          />

          {error
            ? "API unavailable"
            : "API connected"}
        </div>
      </aside>

      <main className="main-content">
        {children}
      </main>
    </div>
  );
}


function Dashboard({
  plants,
  loading,
  error,
  onSelectPlant,
}) {
  const stats = useMemo(() => {
    const needsAttention =
      plants.filter((plant) =>
        ["due", "overdue"].includes(
          plant.insight?.watering?.status
        )
      ).length;

    const onSchedule =
      plants.filter(
        (plant) =>
          plant.insight?.watering?.status ===
          "not_due"
      ).length;

    const learning =
      plants.filter(
        (plant) =>
          plant.insight?.watering?.status ===
          "unknown"
      ).length;

    return {
      total: plants.length,
      needsAttention,
      onSchedule,
      learning,
    };
  }, [plants]);

  return (
    <>
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
        <SummaryCard
          label="Plants"
          value={
            loading
              ? "—"
              : stats.total
          }
          description="Currently tracked"
        />

        <SummaryCard
          label="Needs attention"
          value={
            loading
              ? "—"
              : stats.needsAttention
          }
          description="Watering due or overdue"
          className="attention"
        />

        <SummaryCard
          label="On schedule"
          value={
            loading
              ? "—"
              : stats.onSchedule
          }
          description="Care pattern looks healthy"
        />

        <SummaryCard
          label="Learning"
          value={
            loading
              ? "—"
              : stats.learning
          }
          description="Collecting more care data"
        />
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
            <p>
              Loading plant intelligence...
            </p>

            <span>
              Fetching plants and insights from the API.
            </span>
          </div>
        )}

        {error && !loading && (
          <div className="placeholder error-state">
            <p>
              PlantBrain API unavailable
            </p>

            <span>{error}</span>
          </div>
        )}

        {!loading &&
          !error && (
            <div className="plant-grid">
              {plants.map((plant) => (
                <PlantCard
                  key={plant.id}
                  plant={plant}
                  onClick={() =>
                    onSelectPlant(plant)
                  }
                />
              ))}
            </div>
          )}
      </section>
    </>
  );
}


function SummaryCard({
  label,
  value,
  description,
  className = "",
}) {
  return (
    <article
      className={`summary-card ${className}`}
    >
      <span>{label}</span>
      <strong>{value}</strong>
      <p>{description}</p>
    </article>
  );
}


function PlantCard({
  plant,
  onClick,
}) {
  const watering =
    plant.insight?.watering;

  const pattern =
    plant.insight?.pattern;

  const recommendation =
    plant.insight?.recommendation;

  const wateringStatus =
    watering?.status ??
    "unknown";

  return (
    <article
      className="plant-card"
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(event) => {
        if (
          event.key === "Enter" ||
          event.key === " "
        ) {
          onClick();
        }
      }}
    >
      <div className="plant-card-top">
        <div>
          <p className="plant-location">
            {plant.location ||
              "No location"}
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
          {formatStatus(
            wateringStatus
          )}
        </span>
      </div>

      <div className="plant-metrics">
        <div>
          <span>
            Last watered
          </span>

          <strong>
            {formatDays(
              watering?.days_since_last_watering
            )}
          </strong>
        </div>

        <div>
          <span>
            Average cycle
          </span>

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
          {recommendation?.priority ||
            "low"}{" "}
          priority
        </span>

        <p>
          {recommendation?.message ||
            "PlantBrain is collecting more care data."}
        </p>
      </div>
    </article>
  );
}


function PlantDetail({
  plant,
  loading,
  error,
  onBack,
}) {
  if (loading) {
    return (
      <section className="detail-page">
        <button
          className="back-button"
          onClick={onBack}
        >
          ← Back to dashboard
        </button>

        <div className="placeholder">
          <p>
            Loading plant history...
          </p>

          <span>
            Analyzing care data and patterns.
          </span>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="detail-page">
        <button
          className="back-button"
          onClick={onBack}
        >
          ← Back to dashboard
        </button>

        <div className="placeholder error-state">
          <p>
            Could not load plant detail
          </p>

          <span>{error}</span>
        </div>
      </section>
    );
  }

  const watering =
    plant.insight?.watering;

  const recommendation =
    plant.insight?.recommendation;

  const wateringHistory =
    plant.history?.event_types?.watering;

  const wateringPattern =
    plant.pattern?.event_types?.watering;

  return (
    <section className="detail-page">
      <button
        className="back-button"
        onClick={onBack}
      >
        ← Back to dashboard
      </button>

      <header className="detail-header">
        <div>
          <p className="eyebrow">
            PLANT DETAIL
          </p>

          <h2>{plant.name}</h2>

          <p className="scientific-name detail-scientific">
            {plant.scientific_name ||
              plant.species}
          </p>
        </div>

        <span
          className={`status-badge detail-status status-${
            watering?.status ||
            "unknown"
          }`}
        >
          {formatStatus(
            watering?.status ||
              "unknown"
          )}
        </span>
      </header>

      <div className="detail-summary-grid">
        <DetailMetric
          label="Last watered"
          value={formatDays(
            watering?.days_since_last_watering
          )}
        />

        <DetailMetric
          label="Average watering cycle"
          value={formatCycle(
            watering?.average_interval_days
          )}
        />

        <DetailMetric
          label="Expected next watering"
          value={formatDate(
            watering?.expected_next_watering_at
          )}
        />

        <DetailMetric
          label="Priority"
          value={formatStatus(
            recommendation?.priority ||
              "low"
          )}
        />
      </div>

      <section className="detail-section">
        <div className="detail-section-heading">
          <div>
            <p className="eyebrow">
              CURRENT INSIGHT
            </p>

            <h3>
              Recommendation
            </h3>
          </div>
        </div>

        <div className="insight-panel">
          <span>
            {formatStatus(
              recommendation?.action ||
                "collect_more_data"
            )}
          </span>

          <p>
            {recommendation?.message ||
              "More care data is needed."}
          </p>
        </div>
      </section>

      <section className="detail-section">
        <div className="detail-section-heading">
          <div>
            <p className="eyebrow">
              CARE HISTORY
            </p>

            <h3>
              Last 90 days
            </h3>
          </div>

          <span className="detail-total">
            {plant.history?.total_events ||
              0}{" "}
            events
          </span>
        </div>

        <div className="history-grid">
          {Object.entries(
            plant.history?.event_types || {}
          ).map(
            ([eventType, data]) => (
              <HistoryCard
                key={eventType}
                eventType={eventType}
                data={data}
              />
            )
          )}
        </div>
      </section>
      <CareVisualizations events={plant.events || []} />

      <section className="detail-section">
        <div className="detail-section-heading">
          <div>
            <p className="eyebrow">
              CARE PATTERN
            </p>

            <h3>
              Watering analysis
            </h3>
          </div>
        </div>

        <div className="pattern-analysis-grid">
          <DetailMetric
            label="Watering events"
            value={
              wateringHistory?.count ??
              0
            }
          />

          <DetailMetric
            label="Average interval"
            value={formatCycle(
              wateringPattern?.average_interval_days
            )}
          />

          <DetailMetric
            label="Variability"
            value={formatVariation(
              wateringPattern?.interval_std_dev_days
            )}
          />

          <DetailMetric
            label="Regularity"
            value={formatStatus(
              wateringPattern?.regularity ||
                "insufficient_data"
            )}
          />

          <DetailMetric
            label="Trend"
            value={formatStatus(
              wateringPattern?.trend ||
                "insufficient_data"
            )}
          />
        </div>
      </section>
    </section>
  );
}


function DetailMetric({
  label,
  value,
}) {
  return (
    <article className="detail-metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}


function HistoryCard({
  eventType,
  data,
}) {
  return (
    <article className="history-card">
      <div>
        <span>
          {formatStatus(eventType)}
        </span>

        <strong>
          {data.count}{" "}
          {data.count === 1
            ? "event"
            : "events"}
        </strong>
      </div>

      <p>
        Last activity:{" "}
        {formatDate(
          data.last_at
        )}
      </p>

      {data.average_interval_days !==
        null && (
        <p>
          Average interval:{" "}
          {formatCycle(
            data.average_interval_days
          )}
        </p>
      )}
    </article>
  );
}


function formatStatus(value) {
  if (!value) {
    return "Unknown";
  }

  return value
    .replaceAll("_", " ")
    .replace(
      /\b\w/g,
      (letter) =>
        letter.toUpperCase()
    );
}


function formatDays(value) {
  if (
    value === null ||
    value === undefined
  ) {
    return "No data";
  }

  const rounded =
    Math.round(value);

  if (rounded === 0) {
    return "Today";
  }

  if (rounded === 1) {
    return "1 day ago";
  }

  return `${rounded} days ago`;
}


function formatCycle(value) {
  if (
    value === null ||
    value === undefined
  ) {
    return "Learning";
  }

  return `${value.toFixed(1)} days`;
}


function formatVariation(value) {
  if (
    value === null ||
    value === undefined
  ) {
    return "Learning";
  }

  return `${value.toFixed(1)} days`;
}


function formatDate(value) {
  if (!value) {
    return "No data";
  }

  const date = new Date(value);

  return new Intl.DateTimeFormat(
    "en",
    {
      month: "short",
      day: "numeric",
      year: "numeric",
    }
  ).format(date);
}


export default App;