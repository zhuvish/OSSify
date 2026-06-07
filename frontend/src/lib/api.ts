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

export async function getRepoStatus(repoId: number) {
  try {
    const response = await fetch(`${API_URL}/repositories/${repoId}/status`);

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    return response.json();
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error("Cannot connect to backend server.");
    }
    throw error;
  }
}

export async function getRepositories() {
  try {
    const response = await fetch(`${API_URL}/repositories`);
    if (!response.ok) throw new Error(`Backend returned ${response.status}`);
    return response.json();
  } catch (err) {
    if (err instanceof TypeError) throw new Error("Cannot connect to backend server.");
    throw err;
  }
}

export async function getRepoGraph(repoId: number) {
  try {
    const response = await fetch(`${API_URL}/repositories/${repoId}/graph`);
    if (!response.ok) throw new Error(`Backend returned ${response.status}`);
    return response.json();
  } catch (err) {
    if (err instanceof TypeError) throw new Error("Cannot connect to backend server.");
    throw err;
  }
}

export async function askExperts(question: string) {
  try {
    const response = await fetch(
      `${API_URL}/experts/ask`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      }
    );

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    return response.json();
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error("Cannot connect to backend server.");
    }
    throw error;
  }
}

export async function searchExperts(query: string, repoId?: number) {
  try {
    let url = `${API_URL}/experts/search?query=${encodeURIComponent(query)}`;
    if (repoId !== undefined) {
      url += `&repo_id=${repoId}`;
    }

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    return response.json();
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error("Cannot connect to backend server.");
    }
    throw error;
  }
}
