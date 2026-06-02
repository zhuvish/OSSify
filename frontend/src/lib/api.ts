const API_URL = "http://127.0.0.1:8000";

export async function analyzeRepo(repoUrl: string) {
  try {
    const response = await fetch(
      `${API_URL}/analyze-repo`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repo_url: repoUrl,
        }),
      }
    );

    if (!response.ok) {
      throw new Error(
        `Backend returned ${response.status}`
      );
    }

    return response.json();

  } catch (error) {

    if (error instanceof TypeError) {
      throw new Error(
        "Cannot connect to backend server."
      );
    }

    throw error;
  }
}