import type {
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
  WeeklyMission,
  QualityReport,
} from "./types";


// ============================================================
// API BASE URL
// ============================================================
//
// Local development:
//   http://127.0.0.1:8000
//
// Production:
//   https://student-opportunity-engine.onrender.com
//
// VITE_API_URL can override this when supplied.
// ============================================================

const API =
  import.meta.env.VITE_API_URL ||
  (
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1"
      ? "http://127.0.0.1:8000"
      : "https://student-opportunity-engine.onrender.com"
  );


// ============================================================
// TYPES
// ============================================================

type ApiErrorResponse = {
  detail?: unknown;
  message?: unknown;
  error?: unknown;
};

type HealthResponse = {
  status: string;
  service?: string;
  [key: string]: unknown;
};

type SaveStudentResponse = {
  message?: string;
  student: StudentProfile;
};

type ComparisonResponse = {
  comparison: any[];
  summary?: any;
};

type ExportPreparationPlanResponse = {
  filename: string;
  content: string;
};


// ============================================================
// GENERIC ERROR HANDLING
// ============================================================

async function getErrorMessage(
  response: Response,
): Promise<string> {
  try {
    const data =
      (await response.json()) as ApiErrorResponse;

    if (
      typeof data?.detail === "string"
    ) {
      return data.detail;
    }

    if (
      typeof data?.message === "string"
    ) {
      return data.message;
    }

    if (
      typeof data?.error === "string"
    ) {
      return data.error;
    }

    if (data) {
      return JSON.stringify(data);
    }
  } catch {
    // Response was not JSON.
  }

  return (
    response.statusText ||
    `Request failed with status ${response.status}.`
  );
}


// ============================================================
// GENERIC REQUEST HELPER
// ============================================================

async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(
    `${API}${path}`,
    {
      ...options,
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        ...(options?.headers || {}),
      },
    },
  );

  if (!response.ok) {
    throw new Error(
      await getErrorMessage(response),
    );
  }

  /*
   * Some endpoints may theoretically return
   * an empty response. Handle that safely.
   */
  const contentType =
    response.headers.get("content-type") || "";

  if (
    !contentType.includes("application/json")
  ) {
    const text = await response.text();

    return text as T;
  }

  return (
    await response.json()
  ) as T;
}


// ============================================================
// URL HELPERS
// ============================================================

function safeId(
  id: number,
): string {
  return encodeURIComponent(
    String(id),
  );
}


// ============================================================
// CORE API
// ============================================================


// ------------------------------------------------------------
// HEALTH
// ------------------------------------------------------------

export async function getHealth(): Promise<
  HealthResponse
> {
  return request<HealthResponse>(
    "/api/health",
  );
}


// ------------------------------------------------------------
// GET STUDENT PROFILE
// ------------------------------------------------------------

export async function getStudentProfile(): Promise<
  StudentProfile
> {
  return request<StudentProfile>(
    "/api/student",
  );
}


// ------------------------------------------------------------
// SAVE STUDENT PROFILE
// ------------------------------------------------------------

export async function saveStudentProfile(
  profile: StudentProfile,
): Promise<StudentProfile> {
  const data =
    await request<SaveStudentResponse>(
      "/api/student/profile",
      {
        method: "POST",
        body: JSON.stringify(profile),
      },
    );

  return data.student;
}


// ============================================================
// OPPORTUNITIES
// ============================================================


// ------------------------------------------------------------
// GET OPPORTUNITIES
// ------------------------------------------------------------
//
// IMPORTANT:
// App.tsx should use this to populate
// "Opportunities Worth Your Attention".
//
// This is intentionally kept as a direct GET
// to the backend opportunity endpoint.
// ------------------------------------------------------------

export async function getOpportunities(): Promise<
  Opportunity[]
> {
  const data =
    await request<unknown>(
      "/api/opportunities",
    );

  /*
   * Most versions of your backend return
   * an array directly.
   */
  if (Array.isArray(data)) {
    return data as Opportunity[];
  }

  /*
   * Defensive compatibility for backends that
   * wrap the list inside "opportunities".
   */
  if (
    data &&
    typeof data === "object" &&
    Array.isArray(
      (data as {
        opportunities?: unknown;
      }).opportunities,
    )
  ) {
    return (
      data as {
        opportunities: Opportunity[];
      }
    ).opportunities;
  }

  return [];
}


// ------------------------------------------------------------
// AI OPPORTUNITY SEARCH
// ------------------------------------------------------------

export async function searchOpportunities(
  profile: StudentProfile,
): Promise<SearchResponse> {
  return request<SearchResponse>(
    "/api/ai/search-opportunities",
    {
      method: "POST",
      body: JSON.stringify(profile),
    },
  );
}


// ============================================================
// MATCHING
// ============================================================


// ------------------------------------------------------------
// MATCH
// ------------------------------------------------------------

export async function getMatch(
  id: number,
): Promise<MatchResponse> {
  return request<MatchResponse>(
    `/api/match/${safeId(id)}`,
  );
}


// ------------------------------------------------------------
// WHY NOT
// ------------------------------------------------------------

export async function getWhyNot(
  id: number,
): Promise<WhyNotResponse> {
  return request<WhyNotResponse>(
    `/api/why-not/${safeId(id)}`,
  );
}


// ------------------------------------------------------------
// PREPARATION
// ------------------------------------------------------------

export async function getPreparation(
  id: number,
): Promise<PreparationResponse> {
  return request<PreparationResponse>(
    `/api/prepare/${safeId(id)}`,
  );
}


// ------------------------------------------------------------
// FUTURE PATH
// ------------------------------------------------------------

export async function getFuturePath(
  id: number,
): Promise<FuturePathResponse> {
  return request<FuturePathResponse>(
    `/api/future-path/${safeId(id)}`,
  );
}


// ============================================================
// HIDDEN OPPORTUNITIES
// ============================================================

export async function getHiddenOpportunities(): Promise<
  HiddenRecommendation[]
> {
  const data =
    await request<unknown>(
      "/api/hidden-opportunities",
    );

  if (Array.isArray(data)) {
    return data as HiddenRecommendation[];
  }

  /*
   * Defensive support if backend returns:
   *
   * {
   *   opportunities: [...]
   * }
   */
  if (
    data &&
    typeof data === "object" &&
    Array.isArray(
      (
        data as {
          opportunities?: unknown;
        }
      ).opportunities,
    )
  ) {
    return (
      data as {
        opportunities: HiddenRecommendation[];
      }
    ).opportunities;
  }

  return [];
}


// ============================================================
// OPPORTUNITY COMPARISON
// ============================================================

export async function compareOpportunities(
  opportunityIds: number[],
): Promise<ComparisonResponse> {
  const params =
    new URLSearchParams();

  opportunityIds.forEach(
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
// RESUME
// ============================================================


// ------------------------------------------------------------
// PARSE RESUME
// ------------------------------------------------------------

export async function parseResume(
  text: string,
): Promise<any> {
  return request<any>(
    "/api/resume/parse",
    {
      method: "POST",
      body: JSON.stringify({
        text,
      }),
    },
  );
}


// ------------------------------------------------------------
// RESUME MATCH
// ------------------------------------------------------------

export async function getResumeMatch(
  id: number,
  text: string,
): Promise<any> {
  return request<any>(
    `/api/resume/match/${safeId(id)}`,
    {
      method: "POST",
      body: JSON.stringify({
        text,
      }),
    },
  );
}


// ============================================================
// STEPS 36–55 — INTELLIGENCE
// ============================================================
//
// These endpoints connect the upgraded intelligence layer
// in intelligence_features.py to the React frontend.
// ============================================================


// ------------------------------------------------------------
// COMPLETE OPPORTUNITY WORKSPACE
// ------------------------------------------------------------

export async function getWorkspace(
  id: number,
): Promise<any> {
  return request<any>(
    `/api/intelligence/workspace/${safeId(id)}`,
  );
}


// ------------------------------------------------------------
// EXPLAINABLE RANKING
// ------------------------------------------------------------

export async function getRanking(
  id: number,
): Promise<any> {
  return request<any>(
    `/api/intelligence/ranking/${safeId(id)}`,
  );
}


// ------------------------------------------------------------
// READINESS CHECKLIST
// ------------------------------------------------------------

export async function getReadinessChecklist(
  id: number,
): Promise<any> {
  return request<any>(
    `/api/intelligence/readiness/${safeId(id)}`,
  );
}


// ------------------------------------------------------------
// DEADLINE INTELLIGENCE
// ------------------------------------------------------------

export async function getDeadlineIntelligence(
  id: number,
): Promise<any> {
  return request<any>(
    `/api/intelligence/deadline/${safeId(id)}`,
  );
}


// ------------------------------------------------------------
// BEST NEXT ACTION
// ------------------------------------------------------------

export async function getBestNextAction(
  id: number,
): Promise<any> {
  return request<any>(
    `/api/intelligence/action/${safeId(id)}`,
  );
}


// ------------------------------------------------------------
// PORTFOLIO IMPACT
// ------------------------------------------------------------

export async function getPortfolioImpact(
  id: number,
): Promise<any> {
  return request<any>(
    `/api/intelligence/portfolio/${safeId(id)}`,
  );
}


// ------------------------------------------------------------
// FRESHNESS
// ------------------------------------------------------------

export async function getFreshness(
  id: number,
): Promise<any> {
  return request<any>(
    `/api/intelligence/freshness/${safeId(id)}`,
  );
}


// ------------------------------------------------------------
// SOURCE EVIDENCE
// ------------------------------------------------------------

export async function getSourceEvidence(
  id: number,
): Promise<any> {
  return request<any>(
    `/api/intelligence/source/${safeId(id)}`,
  );
}


// ------------------------------------------------------------
// WEEKLY MISSION
// ------------------------------------------------------------

export async function getWeeklyMission(): Promise<any> {
  return request<any>(
    "/api/intelligence/weekly-mission",
  );
}


// ------------------------------------------------------------
// QUALITY REPORT
// ------------------------------------------------------------

export async function getQualityReport(): Promise<any> {
  return request<any>(
    "/api/intelligence/quality",
  );
}


// ------------------------------------------------------------
// DEDUPLICATED OPPORTUNITIES
// ------------------------------------------------------------

export async function getDeduplicatedOpportunities(): Promise<
  Opportunity[]
> {
  const data =
    await request<unknown>(
      "/api/intelligence/deduplicated",
    );

  if (Array.isArray(data)) {
    return data as Opportunity[];
  }

  if (
    data &&
    typeof data === "object" &&
    Array.isArray(
      (
        data as {
          opportunities?: unknown;
        }
      ).opportunities,
    )
  ) {
    return (
      data as {
        opportunities: Opportunity[];
      }
    ).opportunities;
  }

  return [];
}


// ------------------------------------------------------------
// EXPORT PREPARATION PLAN
// ------------------------------------------------------------

export async function exportPreparationPlan(
  id: number,
): Promise<ExportPreparationPlanResponse> {
  return request<ExportPreparationPlanResponse>(
    `/api/intelligence/export/${safeId(id)}`,
  );
}


// ------------------------------------------------------------
// DEMO SNAPSHOT
// ------------------------------------------------------------

export async function getDemoSnapshot(): Promise<any> {
  return request<any>(
    "/api/demo",
  );
}


// ============================================================
// PROFILE INTELLIGENCE
// ============================================================
//
// This powers profile-level intelligence such as:
//
// - profile weaknesses
// - skill proof
// - evidence locker
// - direction drift
// - opportunity patterns
// - skill investments
// - timeline
// - decision counts
// ============================================================

export async function getProfileIntelligence(): Promise<
  ProfileIntelligence
> {
  return request<ProfileIntelligence>(
    "/api/profile-intelligence",
  );
}


// ============================================================
// READINESS SIMULATOR
// ============================================================
//
// Simulates the effect of adding skills/projects.
// ============================================================

export async function simulateReadiness(
  opportunityId: number,
  addedSkills: string[],
  addedProjects = 0,
): Promise<ReadinessSimulationResponse> {
  return request<ReadinessSimulationResponse>(
    `/api/readiness-simulator/${safeId(
      opportunityId,
    )}`,
    {
      method: "POST",
      body: JSON.stringify({
        added_skills: addedSkills,
        added_projects: addedProjects,
      }),
    },
  );
}


// ============================================================
// APPLICATION STRATEGY
// ============================================================
//
// IMPORTANT:
// This export was missing in your earlier api.ts,
// which caused:
//
// Uncaught SyntaxError:
// The requested module '/src/api.ts' does not provide
// an export named 'getApplicationStrategy'
//
// It is included here.
// ============================================================

export async function getApplicationStrategy(
  opportunityId: number,
): Promise<ApplicationStrategyResponse> {
  return request<ApplicationStrategyResponse>(
    `/api/application-strategy/${safeId(
      opportunityId,
    )}`,
  );
}


// ============================================================
// OPTIONAL INTELLIGENCE BATCH HELPER
// ============================================================
//
// This is useful when App.tsx wants all intelligence
// for one opportunity at once.
//
// It does NOT replace the individual functions above.
// ============================================================

export async function getOpportunityIntelligence(
  opportunityId: number,
): Promise<{
  workspace: any;
  ranking: any;
  readiness: any;
  deadline: any;
  action: any;
  portfolio: any;
  freshness: any;
  source: any;
  applicationStrategy: ApplicationStrategyResponse;
}> {
  const [
    workspace,
    ranking,
    readiness,
    deadline,
    action,
    portfolio,
    freshness,
    source,
    applicationStrategy,
  ] = await Promise.all([
    getWorkspace(opportunityId),
    getRanking(opportunityId),
    getReadinessChecklist(opportunityId),
    getDeadlineIntelligence(opportunityId),
    getBestNextAction(opportunityId),
    getPortfolioImpact(opportunityId),
    getFreshness(opportunityId),
    getSourceEvidence(opportunityId),
    getApplicationStrategy(opportunityId),
  ]);

  return {
    workspace,
    ranking,
    readiness,
    deadline,
    action,
    portfolio,
    freshness,
    source,
    applicationStrategy,
  };
}



// ============================================================
// API INFORMATION
// ============================================================
//
// Helpful for debugging without exposing secrets.
// ============================================================

export function getApiBaseUrl(): string {
  return API;
}