// ============================================================
// CORE ENUMS & REUSABLE TYPES
// ============================================================

export type OpportunityType =
  | "internship"
  | "hackathon"
  | "job"
  | "scholarship"
  | "competition";

export type DeadlineIntelligence = {
  urgency:
    | "Expired"
    | "Critical"
    | "Urgent"
    | "Soon"
    | "Normal"
    | "Unknown";

  days_remaining: number | null;
};

export type MatchBreakdownItem = {
  factor: string;
  points: number;
  maximum: number;
};

// Consolidated AI factor type to use MatchBreakdownItem structure perfectly
export type IntelligenceFactor = MatchBreakdownItem;


// ============================================================
// STUDENT PROFILE & EVIDENCE TRACKING (RETAINED)
// ============================================================

export type StudentProfile = {
  name: string;
  year: number;
  branch: string;
  location: string;
  interests: string[];
  skills: string[];
  opportunity_type: OpportunityType;
  projects?: string[];
  evidence?: string[];
};

export type SkillProof = {
  skill: string;
  proof_score: number;
  claimed: boolean;
  demonstrated: boolean;
  missing_proof: string[];
};


// ============================================================
// OPPORTUNITY DATA STRUCTURES
// ============================================================

export type Opportunity = {
  id: number;
  title: string;
  organization?: string | null;
  company?: string | null;
  type?: string | null;
  description?: string | null;
  year?: string[];
  branches?: string[];
  skills?: string[];
  tags?: string[];
  location?: string | null;
  remote?: boolean | null;
  deadline?: string | null;
  stipend?: string | number | null;
  posted_time_ago?: string | null;
  
  // Consolidated URL fields (safeguarding your original & AI additions)
  source_url?: string | null;
  application_url?: string | null;
  link?: string | null;
  url?: string | null;

  verification_score?: string | null;
  trust_score?: number;
  trust_label?: string;
  trust_reasons?: string[];
  match_score?: number;
  deadline_intelligence?: DeadlineIntelligence | null;
  readiness?: number;
  readiness_level?: string;
  ranking_score?: number;
  suspicion_flags?: string[];
};


// ============================================================
// MATCHING & RESPONSE ANALYTICS (RETAINED)
// ============================================================

export type MatchResponse = {
  opportunity: string;
  eligible: boolean;
  match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  breakdown?: MatchBreakdownItem[];
  message?: string;
};

export type WhyNotResponse = {
  opportunity: string;
  blockers: string[];
  recommendations: string[];
};

export type PreparationRoadmapItem = {
  skill: string;
  priority?: string;
  steps?: string[];
  topics?: string[];
  project?: string;
  estimated_time?: string;
};

export type PreparationResponse = {
  opportunity: string;
  readiness_percentage: number;
  current_skills: string[];
  missing_skills: string[];
  roadmap: PreparationRoadmapItem[];
};

export type FuturePathItem = {
  skill: string;
  goal: string;
  priority?: string;
  why_it_matters?: string;
  milestones?: string[];
  projects?: string[];
  estimated_time?: string;
};

export type FuturePathResponse = {
  opportunity: string;
  message: string;
  future_path: FuturePathItem[];
};

export type HiddenRecommendation = {
  type: string;
  reason: string;
};


// ============================================================
// COMPARISON ENGINE
// ============================================================

export type ComparisonItem = {
  id: number;
  title: string;
  organization: string;
  match_score: number;
  trust_score: number;
  deadline?: string | null;
  deadline_urgency?: string;
  days_remaining?: number | null;
  location?: string | null;
  remote?: boolean | null;
  missing_skills?: string[];
  estimated_learning_hours?: number;
  readiness?: number;
  eligibility?: boolean;
  competition_estimate?: number;
  career_alignment?: number;
  portfolio_value?: number;
  growth_potential?: number;
  ready_before_deadline?: boolean;
};

export type ComparisonSummary = {
  best_match?: number;
  most_trusted?: number;
  easiest_to_prepare?: number;
  most_ready?: number;
  recommended?: number;
  recommendation_reason?: string;
};

export type ComparisonResponse = {
  comparison: ComparisonItem[];
  summary?: ComparisonSummary;
};

export type SearchResponse = {
  count: number;
  opportunities: Opportunity[];
  student?: StudentProfile | null;
};


// ============================================================
// DEEP PROFILE INTELLIGENCE & SIMULATION ENGINE (RETAINED)
// ============================================================

export type TimelineItem = {
  id: number;
  title: string;
  match_score: number;
  readiness: number;
  days_remaining: number | null;
  action: string;
};

export type ProfileIntelligence = {
  profile_weaknesses: string[];
  skill_proof: SkillProof[];
  evidence_locker: Array<{
    skill: string;
    status: string;
    proof_score: number;
    missing_proof: string[];
  }>;
  direction_drift: {
    detected: boolean;
    focus: string;
    message: string;
    action: string;
  };
  opportunity_patterns: Array<{
    skill: string;
    frequency: number;
    percentage: number;
  }>;
  skill_investments: Array<{
    skill: string;
    learning_hours: number;
    opportunities_impacted: number;
    return_per_hour: number;
  }>;
  best_skill_investment: {
    skill: string;
    learning_hours: number;
    opportunities_impacted: number;
    return_per_hour: number;
  } | null;
  decision_counts: Record<string, number>;
  timeline: {
    apply_now: TimelineItem[];
    prepare_this_week: TimelineItem[];
    prepare_this_month: TimelineItem[];
    future_targets: TimelineItem[];
  };
  summary: Record<string, number>;
};

export type ReadinessSimulationResponse = {
  current_readiness: number;
  simulated_readiness: number;
  added_skills: string[];
  added_projects: number;
  new_missing_skills: string[];
  unlocked_opportunities: string[];
  preparation_hours: number;
};

export type ApplicationStrategyResponse = {
  strongest_selling_points: string[];
  weaknesses: string[];
  what_to_emphasize: string[];
  improvements_before_applying: string[];
  decision: string;
  readiness: number;
  estimated_hours: number;
  days_remaining: number | null;
};


// ============================================================
// INTEGRATED WORKSPACE & WORKFLOW INTELLIGENCE (ADDED FROM AI)
// ============================================================

export type OpportunityWorkspace = {
  opportunity: Opportunity;

  ranking: {
    score: number;
    matched_skills: string[];
    missing_skills: string[];
    factors: IntelligenceFactor[];
  };

  freshness: {
    freshness_score: number;
    freshness_label: string;
  };

  source_evidence: {
    source_url?: string | null;
    application_url?: string | null;
    verification_score: string;
    evidence: string[];
  };

  readiness_checklist: {
    item: string;
    complete: boolean;
    category: string;
    importance: string;
  }[];

  deadline: DeadlineIntelligence;

  best_next_action: {
    action: string;
    reason: string;
    priority: string;
  };

  portfolio_impact: {
    existing_projects: number;
    missing_skill_count: number;
    recommended_project: string;
    portfolio_value: number;
  };
};

export type WeeklyMission = {
  title: string;
  skill: string | null;
  goal: string;
  tasks: string[];
};

export type QualityReport = {
  passed: boolean;
  issue_count: number;
  issues: string[];
};
