import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";


function CareVisualizations({ events = [] }) {
  const activityData = buildActivityData(events);
  const wateringIntervals = buildWateringIntervals(events);

  return (
    <section className="visualization-section">
      <div className="detail-section-heading">
        <div>
          <p className="eyebrow">DATA VISUALIZATION</p>
          <h3>Care activity</h3>
        </div>

        <span className="detail-total">
          Based on recorded events
        </span>
      </div>

      <div className="visualization-grid">
        <article className="chart-card">
          <div className="chart-heading">
            <div>
              <span className="chart-label">
                ACTIVITY BREAKDOWN
              </span>

              <h4>Care events</h4>
            </div>

            <span className="chart-caption">
              Last 90 days
            </span>
          </div>

          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={activityData}
                layout="vertical"
                margin={{
                  top: 8,
                  right: 20,
                  bottom: 8,
                  left: 12,
                }}
              >
                <CartesianGrid
                  horizontal={false}
                  stroke="#e5e8e1"
                />

                <XAxis
                  type="number"
                  allowDecimals={false}
                  axisLine={false}
                  tickLine={false}
                  tick={{
                    fill: "#7d8780",
                    fontSize: 11,
                  }}
                />

                <YAxis
                  dataKey="label"
                  type="category"
                  axisLine={false}
                  tickLine={false}
                  width={78}
                  tick={{
                    fill: "#56635a",
                    fontSize: 11,
                  }}
                />

                <Tooltip
                  cursor={{
                    fill: "#f1f3ed",
                  }}
                  contentStyle={{
                    border: "1px solid #dde2da",
                    borderRadius: "10px",
                    fontSize: "12px",
                  }}
                />

                <Bar
                  dataKey="count"
                  fill="#667c68"
                  radius={[0, 6, 6, 0]}
                  barSize={18}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </article>

        <article className="chart-card">
          <div className="chart-heading">
            <div>
              <span className="chart-label">
                WATERING CONSISTENCY
              </span>

              <h4>Interval history</h4>
            </div>

            <span className="chart-caption">
              Actual event timing
            </span>
          </div>

          {wateringIntervals.length > 0 ? (
            <div className="interval-list">
              {wateringIntervals.map((item) => (
                <div
                  className="interval-item"
                  key={`${item.from}-${item.to}`}
                >
                  <div className="interval-date">
                    <span>{item.toLabel}</span>
                    <small>
                      Previous: {item.fromLabel}
                    </small>
                  </div>

                  <div className="interval-track">
                    <span />
                  </div>

                  <strong>
                    {formatInterval(item.days)}
                  </strong>
                </div>
              ))}
            </div>
          ) : (
            <div className="chart-empty">
              <p>Not enough watering events yet.</p>
              <span>
                At least two watering records are needed.
              </span>
            </div>
          )}
        </article>
      </div>
    </section>
  );
}


function buildActivityData(events) {
  const counts = events.reduce((result, event) => {
    result[event.event_type] =
      (result[event.event_type] || 0) + 1;

    return result;
  }, {});

  return Object.entries(counts)
    .map(([eventType, count]) => ({
      eventType,
      label: formatStatus(eventType),
      count,
    }))
    .sort((a, b) => b.count - a.count);
}


function buildWateringIntervals(events) {
  const wateringEvents = events
    .filter((event) => event.event_type === "watering")
    .map((event) => ({
      ...event,
      date: new Date(event.occurred_at),
    }))
    .sort((a, b) => a.date - b.date);

  const intervals = [];

  for (let index = 1; index < wateringEvents.length; index += 1) {
    const previous = wateringEvents[index - 1];
    const current = wateringEvents[index];

    const differenceMs =
      current.date.getTime() - previous.date.getTime();

    const differenceDays =
      differenceMs / (1000 * 60 * 60 * 24);

    intervals.push({
      from: previous.occurred_at,
      to: current.occurred_at,
      fromLabel: formatShortDate(previous.date),
      toLabel: formatShortDate(current.date),
      days: differenceDays,
    });
  }

  return intervals;
}


function formatStatus(value) {
  return value
    .replaceAll("_", " ")
    .replace(
      /\b\w/g,
      (letter) => letter.toUpperCase()
    );
}


function formatShortDate(date) {
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
  }).format(date);
}


function formatInterval(value) {
  const rounded = Math.round(value * 10) / 10;

  return `${rounded} ${rounded === 1 ? "day" : "days"}`;
}


export default CareVisualizations;