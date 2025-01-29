// TODO: Update to use a real API endpoint
const API_BASE_URL = "/data";

async function fetchPackages() {
  try {
    const response = await fetch(`${API_BASE_URL}/packages.json`);
    if (!response.ok) throw new Error("Failed to fetch packages");
    return await response.json();
  } catch (error) {
    console.error("Error loading packages:", error);
    return [];
  }
}

export { fetchPackages };
