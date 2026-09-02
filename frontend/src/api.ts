
import type {
  ComparisonResponse,
  FuturePathResponse,
  HiddenRecommendation,
  MatchResponse,
  Opportunity,
  PreparationResponse,
  SearchResponse,
  StudentProfile,
  WhyNotResponse,
  ProfileIntelligence,
  ReadinessSimulationResponse,
  ApplicationStrategyResponse,
} from "./types";


const API =
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000"
    : "https://student-opportunity-engine.onrender.com";


async function getErrorMessage(
  response: Response,
): Promise<string> {

  try {

    const data =
      await response.json();

    if (
      typeof data?.detail ===
      "string"
    ) {
      return data.detail;
    }

    return JSON.stringify(data);

  } catch {

    return (
      response.statusText ||
      "Unknown backend error"
    );
  }
}


async function request<T>(
  endpoint: string,
  options?: RequestInit,
): Promise<T> {

  const response =
    await fetch(
      `${API}${endpoint}`,
      {
        ...options,

        headers: {
          "Content-Type":
            "application/json",

          ...(options?.headers || {}),
        },
      },
    );

  if (!response.ok) {

    throw new Error(
      `${response.status}: ${
        await getErrorMessage(response)
      }`
    );
  }

  return response.json();
}


// ============================================================
// HEALTH
// ============================================================

export async function getHealth() {

  return request<{
    status: string;
    message: string;
  }>("/api/health");
}


// ============================================================
// STUDENT
// ============================================================

export async function getStudentProfile() {

  return request<StudentProfile>(
    "/api/student",
  );
}


export async function saveStudentProfile(
  profile: StudentProfile,
) {

  const response =
    await request<{
      message: string;
      student: StudentProfile;
    }>(
      "/api/student/profile",
      {
        method: "POST",

        body:
          JSON.stringify(
            profile,
          ),
      },
    );

  return response.student;
}


// ============================================================
// OPPORTUNITIES
// ============================================================

export async function getOpportunities() {

  return request<Opportunity[]>(
    "/api/opportunities",
  );
}


export async function searchOpportunities(
  profile: StudentProfile,
) {

  return request<SearchResponse>(
    "/api/ai/search-opportunities",
    {
      method: "POST",

      body:
        JSON.stringify(
          profile,
        ),
    },
  );
}


// ============================================================
// MATCH
// ============================================================

export async function getMatch(
  id: number,
) {

  return request<MatchResponse>(
    `/api/match/${id}`,
  );
}


export async function getWhyNot(
  id: number,
) {

  return request<WhyNotResponse>(
    `/api/why-not/${id}`,
  );
}


// ============================================================
// PREPARATION
// ============================================================

export async function getPreparation(
  id: number,
) {

  return request<PreparationResponse>(
    `/api/prepare/${id}`,
  );
}


// ============================================================
// FUTURE PATH
// ============================================================

export async function getFuturePath(
  id: number,
) {

  return request<FuturePathResponse>(
    `/api/future-path/${id}`,
  );
}


// ============================================================
// HIDDEN OPPORTUNITIES
// ============================================================

export async function getHiddenOpportunities() {

  return request<
    HiddenRecommendation[]
  >(
    "/api/hidden-opportunities",
  );
}


// ============================================================
// COMPARISON
// ============================================================

export async function compareOpportunities(
  ids: number[],
) {

  const params =
    new URLSearchParams();

  ids.forEach(
    (id) => {
      params.append(
        "opportunity_ids",
        String(id),
      );
    },
  );

  return request<ComparisonResponse>(
    `/api/compare?${params.toString()}`,
  );
}

// ============================================================
// ADVANCED INTELLIGENCE
// ============================================================

export async function getProfileIntelligence() {
  return request<ProfileIntelligence>(
    "/api/profile-intelligence",
  );
}

export async function simulateReadiness(
  opportunityId: number,
  addedSkills: string[],
  addedProjects = 0,
) {
  return request<ReadinessSimulationResponse>(
    `/api/readiness-simulator/${opportunityId}`,
    {
      method: "POST",
      body: JSON.stringify({
        added_skills: addedSkills,
        added_projects: addedProjects,
      }),
    },
  );
}

export async function getApplicationStrategy(
  opportunityId: number,
) {
  return request<ApplicationStrategyResponse>(
    `/api/application-strategy/${opportunityId}`,
  );
}

export async function parseResume(text: string) {
  return request<unknown>(
    "/api/resume/parse",
    {
      method: "POST",
      body: JSON.stringify({ text }),
    },
  );
}


// ============================================================
// STEPS 36–55 — INTELLIGENCE
// ============================================================

export async function getWorkspace(
  id: number,
) {
  return request<any>(
    `/api/intelligence/workspace/${id}`,
  );
}


export async function getRanking(
  id: number,
) {
  return request<any>(
    `/api/intelligence/ranking/${id}`,
  );
}


export async function getReadinessChecklist(
  id: number,
) {
  return request<any>(
    `/api/intelligence/readiness/${id}`,
  );
}


export async function getDeadlineIntelligence(
  id: number,
) {
  return request<any>(
    `/api/intelligence/deadline/${id}`,
  );
}


export async function getBestNextAction(
  id: number,
) {
  return request<any>(
    `/api/intelligence/action/${id}`,
  );
}


export async function getPortfolioImpact(
  id: number,
) {
  return request<any>(
    `/api/intelligence/portfolio/${id}`,
  );
}


export async function getFreshness(
  id: number,
) {
  return request<any>(
    `/api/intelligence/freshness/${id}`,
  );
}


export async function getSourceEvidence(
  id: number,
) {
  return request<any>(
    `/api/intelligence/source/${id}`,
  );
}


export async function getWeeklyMission() {
  return request<any>(
    "/api/intelligence/weekly-mission",
  );
}


export async function getQualityReport() {
  return request<any>(
    "/api/intelligence/quality",
  );
}


export async function getDeduplicatedOpportunities() {
  return request<Opportunity[]>(
    "/api/intelligence/deduplicated",
  );
}


export async function exportPreparationPlan(
  id: number,
) {
  return request<{
    filename: string;
    content: string;
  }>(
    `/api/intelligence/export/${id}`,
  );
}


export async function getDemoSnapshot() {
  return request<any>(
    "/api/demo",
  );
}