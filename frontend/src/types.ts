export type StudentProfile = {
  name: string;
  year: number;
  branch: string;
  location: string;
  interests: string[];
  skills: string[];
  opportunity_type:
    | "internship"
    | "hackathon"
    | "job"
    | "scholarship"
    | "competition";
};


export type Opportunity = {
  id: number;

  title: string;

  organization?: string | null;

  company?: string | null;

  description?: string | null;

  match_score?: number;

  type?: string | null;

  year?: string[];

  branches?: string[];

  skills?: string[];

  tags?: string[];

  location?: string | null;

  remote?: boolean | null;

  deadline?: string | null;

  stipend?: number | string | null;

  posted_time_ago?: string | null;

  is_still_accepting?: boolean | null;

  verification_score?:
    | "Low"
    | "Medium"
    | "High"
    | string;

  source_url?: string;

  application_url?: string | null;

  link?: string | null;

  url?: string | null;
};


export type MatchResponse = {
  opportunity: string;

  eligible: boolean;

  match_score: number;

  matched_skills: string[];

  missing_skills: string[];

  message?: string;
};


export type PreparationResponse = {
  opportunity: string;

  current_skills: string[];

  missing_skills: string[];

  roadmap: {
    skill: string;

    steps?: string[];

    project?: string;

    priority?: string;
  }[];
};


export type SearchResponse = {
  count: number;

  opportunities: Opportunity[];

  student?: StudentProfile | null;
};