const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";


async function request(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);

  if (!response.ok) {
    throw new Error(
      `PlantBrain API request failed: ${response.status}`
    );
  }

  return response.json();
}


export async function getPlants() {
  return request("/plants");
}


export async function getPlantInsight(plantId) {
  return request(`/plants/${plantId}/insights`);
}


export async function getDemoPlantsWithInsights() {
  const plants = await getPlants();

  const demoPlants = plants.filter((plant) =>
    plant.notes?.startsWith("[DEMO]")
  );

  return Promise.all(
    demoPlants.map(async (plant) => {
      const insight = await getPlantInsight(plant.id);

      return {
        ...plant,
        insight,
      };
    })
  );
}