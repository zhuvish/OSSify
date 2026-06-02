const API_URL = "http://127.0.0.1:8000";

export async function getDashboardStats(repoId: number) {
  const response = await fetch(
    `${API_URL}/repositories/${repoId}/dashboard`
  );

  if (!response.ok) {
    throw new Error("Failed to load stats");
  }

  return response.json();
}