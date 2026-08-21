import type {
  MatchResponse,
  Opportunity,
  StudentProfile,
} from "./types";


// ============================================================
// API BASE URL
// ============================================================

const API =
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000"
    : "https://student-opportunity-engine.onrender.com";


// ============================================================
// HELPER
// ============================================================

async function getErrorMessage(response: Response): Promise<string> {
  try {
    const data = await response.json();

    if (typeof data?.detail === "string") {
      return data.detail;
    }

    return JSON.stringify(data);
  } catch {
    return response.statusText || "Unknown backend error";
  }
}


// ============================================================
// OPPORTUNITIES
// ============================================================

export async function getOpportunities(): Promise<Opportunity[]> {
  const response = await fetch(
    `${API}/api/opportunities`
  );

  if (!response.ok) {
    throw new Error(
      `Failed to fetch opportunities: ${await getErrorMessage(response)}`
    );
  }

  return response.json();
}


// ============================================================
// STUDENT PROFILE
// ============================================================

export async function getStudentProfile(): Promise<StudentProfile> {
  const response = await fetch(
    `${API}/api/student`
  );

  if (!response.ok) {
    throw new Error(
      `Failed to fetch student profile: ${await getErrorMessage(response)}`
    );
  }

  return response.json();
}


export async function saveStudentProfile(
  profile: StudentProfile
): Promise<StudentProfile> {

  const response = await fetch(
    `${API}/api/student/profile`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify(profile),
    }
  );

  if (!response.ok) {
    throw new Error(
      `Failed to save student profile: ${await getErrorMessage(response)}`
    );
  }

  const data = await response.json();

  // Backend returns:
  // {
  //   message: "...",
  //   student: {...}
  // }

  return data.student;
}


// ============================================================
// LIVE AI SEARCH
// ============================================================

export async function searchOpportunities(
  profile: StudentProfile
): Promise<{
  opportunities: Opportunity[];
  count: number;
}> {

  console.log(
    "Current student profile:",
    profile
  );

  const response = await fetch(
    `${API}/api/ai/search-opportunities`
  );

  if (!response.ok) {
    const errorText =
      await getErrorMessage(response);

    console.error(
      "Search API error:",
      response.status,
      errorText
    );

    throw new Error(
      `Failed to search opportunities: ${errorText}`
    );
  }

  return response.json();
}


// ============================================================
// BASIC MATCH
// ============================================================

export async function getMatch(
  id: number
): Promise<MatchResponse> {

  const response = await fetch(
    `${API}/api/match/${id}`
  );

  if (!response.ok) {
    throw new Error(
      `Failed to fetch match: ${await getErrorMessage(response)}`
    );
  }

  return response.json();
}


// ============================================================
// ELIGIBILITY
// ============================================================

export async function getEligibility(
  id: number
) {

  const response = await fetch(
    `${API}/api/eligibility/${id}`
  );

  if (!response.ok) {
    throw new Error(
      `Failed to fetch eligibility: ${await getErrorMessage(response)}`
    );
  }

  return response.json();
}


// ============================================================
// SEMANTIC MATCH
// ============================================================

export async function getSemanticMatch(
  id: number
) {

  const response = await fetch(
    `${API}/api/semantic-match/${id}`
  );

  if (!response.ok) {
    throw new Error(
      `Failed to fetch semantic match: ${await getErrorMessage(response)}`
    );
  }

  return response.json();
}


// ============================================================
// GAP ANALYSIS
// ============================================================

export async function getGaps(
  id: number
) {

  const response = await fetch(
    `${API}/api/gap_analysis/${id}`
  );

  if (!response.ok) {
    throw new Error(
      `Failed to fetch skill gaps: ${await getErrorMessage(response)}`
    );
  }

  return response.json();
}


// ============================================================
// RESOURCE ROADMAP
// ============================================================

export async function getPreparation(
  id: number
) {

  const response = await fetch(
    `${API}/api/resource-roadmap/${id}`
  );

  if (!response.ok) {
    throw new Error(
      `Failed to fetch preparation plan: ${await getErrorMessage(response)}`
    );
  }

  return response.json();
}