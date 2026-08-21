import type {
  MatchResponse,
  Opportunity,
  StudentProfile,
} from "./types";



const API = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
  ? "http://127.0.0.1:8000"                                    // Use this when testing on your laptop
  : "https://onrender.com";

export async function getOpportunities(): Promise<Opportunity[]> {

  const response = await fetch(
    `${API}/api/opportunities`
  );


  if (!response.ok) {
    throw new Error(
      "Failed to fetch opportunities"
    );
  }


  return response.json();

}


export async function getStudentProfile(): Promise<StudentProfile> {

  const response = await fetch(
    `${API}/api/student`
  );


  if (!response.ok) {
    throw new Error(
      "Failed to fetch student profile"
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
      "Failed to save student profile"
    );
  }


  return response.json();

}


export async function searchOpportunities(
  profile: StudentProfile
): Promise<{
  opportunities: Opportunity[];
  count: number;
}> {

  const response = await fetch(
    `${API}/api/ai/search-opportunities`,
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
      "Failed to search opportunities"
    );
  }


  return response.json();

}


export async function getMatch(
  id: number
): Promise<MatchResponse> {

  const response = await fetch(
    `${API}/api/match/${id}`
  );


  if (!response.ok) {
    throw new Error(
      "Failed to fetch match"
    );
  }


  return response.json();

}


export async function getEligibility(
  id: number
) {

  const response = await fetch(
    `${API}/api/eligibility/${id}`
  );


  if (!response.ok) {
    throw new Error(
      "Failed to fetch eligibility"
    );
  }


  return response.json();

}


export async function getGaps(
  id: number
) {

  const response = await fetch(
    `${API}/api/gap_analysis/${id}`
  );


  if (!response.ok) {
    throw new Error(
      "Failed to fetch skill gaps"
    );
  }


  return response.json();

}


export async function getPreparation(
  id: number
) {

  const response = await fetch(
    `${API}/api/prepare/${id}`
  );


  if (!response.ok) {
    throw new Error(
      "Failed to fetch preparation plan"
    );
  }


  return response.json();

}