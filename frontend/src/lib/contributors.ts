const API_URL = "http://127.0.0.1:8000";

export async function getContributors(
  repoId: number
) {
  const response = await fetch(
    `${API_URL}/repositories/${repoId}/contributors`
  );

  if (!response.ok) {
    throw new Error(
      "Failed to load contributors"
    );
  }

  return response.json();
}

export async function getContributor(contributorId: number) {
  const res = await fetch(`${API_URL}/contributors/${contributorId}`);
  if (!res.ok) throw new Error("Failed to load contributor");
  return res.json();
}