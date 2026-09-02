import {
  ArrowRight,
  CheckCircle2,
  Clock3,
  ExternalLink,
  FileCheck2,
  FolderKanban,
  ShieldCheck,
  Sparkles,
  Target,
  TrendingUp,
} from "lucide-react";

import type { ReactNode } from "react";

import type {
  Opportunity,
} from "../types";


// ============================================================
// WORKSPACE DATA TYPES
// ============================================================

export type WorkspaceFactor = {
  factor: string;
  points: number;
  maximum: number;
};

export type WorkspaceChecklistItem = {
  item: string;
  complete: boolean;
  category: string;
  importance?: string;
};

export type WorkspaceFreshness = {
  freshness_score?: number;
  freshness_label?: string;
};

export type WorkspaceSourceEvidence = {
  source_url?: string | null;
  application_url?: string | null;
  verification_score?: string;
  evidence?: string[];
};

export type WorkspaceDeadline = {
  days_remaining?: number | null;
  urgency?: string;
};

export type WorkspaceNextAction = {
  action: string;
  reason: string;
  priority?: string;
};

export type WorkspacePortfolioImpact = {
  existing_projects?: number;
  missing_skill_count?: number;
  recommended_project?: string;
  portfolio_value?: number;
};

export type WorkspaceRanking = {
  score?: number;
  matched_skills?: string[];
  missing_skills?: string[];
  factors?: WorkspaceFactor[];
};

export type OpportunityWorkspaceData = {
  opportunity: Opportunity;

  ranking: WorkspaceRanking;

  freshness: WorkspaceFreshness;

  source_evidence: WorkspaceSourceEvidence;

  readiness_checklist: WorkspaceChecklistItem[];

  deadline: WorkspaceDeadline;

  best_next_action: WorkspaceNextAction;

  portfolio_impact: WorkspacePortfolioImpact;

  fingerprint?: string;
};


// ============================================================
// PROPS
// ============================================================

type OpportunityWorkspaceProps = {
  data: OpportunityWorkspaceData | null;

  loading?: boolean;

  onClose: () => void;

  onApply?: (
    opportunity: Opportunity,
  ) => void;
};


// ============================================================
// MAIN COMPONENT
// ============================================================

export default function OpportunityWorkspace({
  data,
  loading = false,
  onClose,
  onApply,
}: OpportunityWorkspaceProps) {

  // ----------------------------------------------------------
  // LOADING STATE
  // ----------------------------------------------------------

  if (loading) {
    return (
      <section className="glass rounded-3xl p-6 sm:p-8">

        <div className="animate-pulse space-y-6">

          <div className="flex items-start justify-between gap-5">

            <div className="space-y-3">

              <div className="h-5 w-40 rounded bg-white/10" />

              <div className="h-8 w-80 max-w-full rounded bg-white/10" />

              <div className="h-4 w-48 rounded bg-white/5" />

            </div>

            <div className="h-10 w-24 rounded-xl bg-white/5" />

          </div>


          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

            {[
              1,
              2,
              3,
              4,
            ].map((item) => (
              <div
                key={item}
                className="h-24 rounded-2xl bg-white/[0.035]"
              />
            ))}

          </div>


          <div className="grid gap-6 lg:grid-cols-2">

            {[
              1,
              2,
              3,
              4,
            ].map((item) => (
              <div
                key={item}
                className="h-56 rounded-2xl bg-white/[0.03]"
              />
            ))}

          </div>

        </div>

      </section>
    );
  }


  // ----------------------------------------------------------
  // EMPTY STATE
  // ----------------------------------------------------------

  if (!data) {
    return (
      <section className="glass rounded-3xl p-8">

        <div className="flex min-h-[240px] flex-col items-center justify-center text-center">

          <div className="rounded-2xl bg-cyan-300/10 p-4">

            <Target className="h-8 w-8 text-cyan-300" />

          </div>

          <h2 className="mt-5 text-xl font-semibold text-white">

            Opportunity Workspace

          </h2>

          <p className="mt-2 max-w-md text-sm leading-6 text-zinc-500">

            Select an opportunity to open its complete intelligence workspace.

          </p>

        </div>

      </section>
    );
  }


  // ----------------------------------------------------------
  // SAFE DATA NORMALIZATION
  // ----------------------------------------------------------

  const opportunity =
    data.opportunity;


  const ranking =
    data.ranking || {
      score: 0,
      matched_skills: [],
      missing_skills: [],
      factors: [],
    };


  const freshness =
    data.freshness || {
      freshness_score: 0,
      freshness_label: "Unknown",
    };


  const sourceEvidence =
    data.source_evidence || {
      source_url: null,
      application_url: null,
      verification_score: "Unknown",
      evidence: [],
    };


  const readinessChecklist =
    Array.isArray(
      data.readiness_checklist,
    )
      ? data.readiness_checklist
      : [];


  const deadline =
    data.deadline || {
      days_remaining: null,
      urgency: "Unknown",
    };


  const bestNextAction =
    data.best_next_action || {
      action: "Review opportunity",
      reason:
        "Review the opportunity details before deciding your next step.",
      priority: "Medium",
    };


  const portfolioImpact =
    data.portfolio_impact || {
      existing_projects: 0,
      missing_skill_count: 0,
      recommended_project:
        "Strengthen your strongest relevant project.",
      portfolio_value: 0,
    };


  const matchedSkills =
    Array.isArray(
      ranking.matched_skills,
    )
      ? ranking.matched_skills
      : [];


  const missingSkills =
    Array.isArray(
      ranking.missing_skills,
    )
      ? ranking.missing_skills
      : [];


  const factors =
    Array.isArray(
      ranking.factors,
    )
      ? ranking.factors
      : [];


  const evidence =
    Array.isArray(
      sourceEvidence.evidence,
    )
      ? sourceEvidence.evidence
      : [];


  const applicationUrl =
    sourceEvidence.application_url ||
    opportunity.application_url ||
    sourceEvidence.source_url ||
    opportunity.source_url ||
    null;


  const organization =
    opportunity.organization ||
    opportunity.company ||
    "Organization unavailable";


  const matchScore =
    Math.round(
      Number(ranking.score || 0),
    );


  const trustScore =
    opportunity.trust_score !== undefined
      ? Math.round(
          Number(
            opportunity.trust_score,
          ),
        )
      : 0;


  const portfolioValue =
    Math.round(
      Number(
        portfolioImpact.portfolio_value ||
        0,
      ),
    );


  const deadlineDays =
    deadline.days_remaining;


  const completedChecklistCount =
    readinessChecklist.filter(
      (item) =>
        item.complete,
    ).length;


  const checklistPercentage =
    readinessChecklist.length > 0
      ? Math.round(
          (
            completedChecklistCount /
            readinessChecklist.length
          ) *
            100,
        )
      : 0;


  // ----------------------------------------------------------
  // APPLY HANDLER
  // ----------------------------------------------------------

  function handleApply() {

    if (
      onApply
    ) {
      onApply(
        opportunity,
      );

      return;
    }


    if (
      applicationUrl
    ) {

      window.open(
        applicationUrl,
        "_blank",
        "noopener,noreferrer",
      );

      return;
    }

  }


  // ----------------------------------------------------------
  // RENDER
  // ----------------------------------------------------------

  return (
    <section className="glass rounded-3xl p-6 shadow-2xl sm:p-8">

      {/* ======================================================
          HEADER
      ====================================================== */}

      <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">

        <div className="min-w-0">

          <div className="flex flex-wrap items-center gap-2">

            <span className="inline-flex items-center gap-2 rounded-full border border-cyan-300/20 bg-cyan-300/10 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.16em] text-cyan-200">

              <Sparkles className="h-3.5 w-3.5" />

              Opportunity Workspace

            </span>


            <span className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1.5 text-[10px] uppercase tracking-[0.14em] text-zinc-500">

              {freshness.freshness_label || "Freshness unknown"}

            </span>


            {opportunity.type && (
              <span className="rounded-full border border-violet-300/15 bg-violet-400/10 px-3 py-1.5 text-[10px] uppercase tracking-[0.14em] text-violet-200">

                {opportunity.type}

              </span>
            )}

          </div>


          <h2 className="mt-5 break-words text-2xl font-semibold leading-tight text-white sm:text-3xl">

            {opportunity.title || "Untitled Opportunity"}

          </h2>


          <p className="mt-2 text-sm text-zinc-500">

            {organization}

          </p>


          {opportunity.location && (
            <p className="mt-2 text-xs text-zinc-600">

              {opportunity.location}

              {opportunity.remote
                ? " • Remote available"
                : ""}

            </p>
          )}

        </div>


        <div className="flex shrink-0 gap-2">

          {applicationUrl && (
            <button
              onClick={handleApply}
              className="inline-flex items-center gap-2 rounded-xl bg-cyan-300 px-4 py-2.5 text-sm font-semibold text-black transition hover:bg-cyan-200"
            >

              Apply

              <ExternalLink className="h-4 w-4" />

            </button>
          )}


          <button
            onClick={onClose}
            className="rounded-xl border border-white/10 bg-white/[0.03] px-4 py-2.5 text-sm text-zinc-300 transition hover:border-white/20 hover:text-white"
          >

            Close

          </button>

        </div>

      </div>


      {/* ======================================================
          EXECUTIVE METRICS
      ====================================================== */}

      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

        <Metric
          icon={<Target className="h-4 w-4" />}
          label="Profile Match"
          value={`${matchScore}%`}
          detail={
            matchScore >= 80
              ? "Strong fit"
              : matchScore >= 60
                ? "Worth pursuing"
                : "Needs preparation"
          }
        />


        <Metric
          icon={<ShieldCheck className="h-4 w-4" />}
          label="Source Trust"
          value={
            trustScore > 0
              ? `${trustScore}%`
              : "Unknown"
          }
          detail={
            opportunity.trust_label ||
            sourceEvidence.verification_score ||
            "Review source"
          }
        />


        <Metric
          icon={<Clock3 className="h-4 w-4" />}
          label="Deadline"
          value={
            deadlineDays === null ||
            deadlineDays === undefined
              ? "Unknown"
              : deadlineDays < 0
                ? "Expired"
                : `${deadlineDays}d`
          }
          detail={
            deadline.urgency ||
            "Unknown urgency"
          }
        />


        <Metric
          icon={<FolderKanban className="h-4 w-4" />}
          label="Portfolio Value"
          value={
            portfolioValue > 0
              ? `${portfolioValue}%`
              : "—"
          }
          detail={
            portfolioImpact.missing_skill_count
              ? `${portfolioImpact.missing_skill_count} skill gap(s)`
              : "Proof opportunity"
          }
        />

      </div>


      {/* ======================================================
          BEST NEXT ACTION
      ====================================================== */}

      <div className="mt-6 rounded-2xl border border-cyan-300/15 bg-cyan-300/[0.045] p-5">

        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">

          <div className="flex items-start gap-3">

            <div className="rounded-xl bg-cyan-300/10 p-3 text-cyan-300">

              <Sparkles className="h-5 w-5" />

            </div>


            <div>

              <p className="text-[10px] uppercase tracking-[0.18em] text-cyan-300/70">

                Recommended next move

              </p>


              <h3 className="mt-1 text-lg font-semibold text-white">

                {bestNextAction.action}

              </h3>


              <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-400">

                {bestNextAction.reason}

              </p>

            </div>

          </div>


          {bestNextAction.priority && (
            <span className="shrink-0 rounded-full border border-cyan-300/15 bg-cyan-300/10 px-3 py-1.5 text-[10px] uppercase tracking-wider text-cyan-200">

              {bestNextAction.priority}

            </span>
          )}

        </div>

      </div>


      {/* ======================================================
          MAIN INTELLIGENCE GRID
      ====================================================== */}

      <div className="mt-6 grid gap-6 lg:grid-cols-2">

        {/* ----------------------------------------------------
            MATCH EXPLANATION
        ---------------------------------------------------- */}

        <Panel
          title="Why this opportunity matches you"
          icon={
            <Target className="h-4 w-4 text-cyan-300" />
          }
        >

          {factors.length > 0 ? (
            <div className="space-y-4">

              {factors.map(
                (
                  factor,
                  index,
                ) => {

                  const percentage =
                    factor.maximum > 0
                      ? Math.max(
                          0,
                          Math.min(
                            100,
                            (
                              factor.points /
                              factor.maximum
                            ) *
                              100,
                          ),
                        )
                      : 0;


                  return (
                    <div
                      key={`${factor.factor}-${index}`}
                    >

                      <div className="flex items-center justify-between gap-4 text-xs">

                        <span className="text-zinc-500">

                          {factor.factor}

                        </span>


                        <span className="font-medium text-zinc-300">

                          {factor.points}/
                          {factor.maximum}

                        </span>

                      </div>


                      <div className="mt-2 h-2 overflow-hidden rounded-full bg-white/[0.06]">

                        <div
                          className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-violet-400 transition-all"
                          style={{
                            width:
                              `${percentage}%`,
                          }}
                        />

                      </div>

                    </div>
                  );

                },
              )}

            </div>
          ) : (
            <EmptyText text="Detailed ranking factors are unavailable for this opportunity." />
          )}


          <div className="mt-6">

            <p className="text-[10px] uppercase tracking-[0.16em] text-zinc-600">

              Skills already aligned

            </p>


            <div className="mt-3 flex flex-wrap gap-2">

              {matchedSkills.length > 0 ? (
                matchedSkills.map(
                  (
                    skill,
                    index,
                  ) => (
                    <span
                      key={`${skill}-${index}`}
                      className="rounded-full border border-emerald-300/15 bg-emerald-400/10 px-3 py-1.5 text-xs text-emerald-200"
                    >

                      ✓ {skill}

                    </span>
                  ),
                )
              ) : (
                <EmptyText text="No directly matched skills detected." />
              )}

            </div>

          </div>


          <div className="mt-5">

            <p className="text-[10px] uppercase tracking-[0.16em] text-zinc-600">

              Skills to close

            </p>


            <div className="mt-3 flex flex-wrap gap-2">

              {missingSkills.length > 0 ? (
                missingSkills.map(
                  (
                    skill,
                    index,
                  ) => (
                    <span
                      key={`${skill}-${index}`}
                      className="rounded-full border border-amber-300/15 bg-amber-400/10 px-3 py-1.5 text-xs text-amber-200"
                    >

                      Gap: {skill}

                    </span>
                  ),
                )
              ) : (
                <EmptyText text="No direct skill gaps were detected." />
              )}

            </div>

          </div>

        </Panel>


        {/* ----------------------------------------------------
            READINESS CHECKLIST
        ---------------------------------------------------- */}

        <Panel
          title="Application readiness"
          icon={
            <FileCheck2 className="h-4 w-4 text-cyan-300" />
          }
        >

          <div className="mb-5 rounded-xl bg-white/[0.025] p-4">

            <div className="flex items-center justify-between gap-4">

              <div>

                <p className="text-xs text-zinc-500">

                  Readiness checklist

                </p>

                <p className="mt-1 text-sm font-semibold text-white">

                  {completedChecklistCount}/
                  {readinessChecklist.length} completed

                </p>

              </div>


              <span className="text-lg font-semibold text-cyan-300">

                {checklistPercentage}%

              </span>

            </div>


            <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/[0.06]">

              <div
                className="h-full rounded-full bg-cyan-300"
                style={{
                  width:
                    `${checklistPercentage}%`,
                }}
              />

            </div>

          </div>


          {readinessChecklist.length > 0 ? (
            <div className="space-y-2">

              {readinessChecklist.map(
                (
                  item,
                  index,
                ) => (
                  <div
                    key={`${item.category}-${item.item}-${index}`}
                    className={`flex items-start gap-3 rounded-xl p-3 ${
                      item.complete
                        ? "bg-emerald-400/[0.045]"
                        : "bg-white/[0.025]"
                    }`}
                  >

                    <CheckCircle2
                      className={`mt-0.5 h-4 w-4 shrink-0 ${
                        item.complete
                          ? "text-emerald-300"
                          : "text-zinc-700"
                      }`}
                    />


                    <div className="min-w-0">

                      <p
                        className={`text-sm ${
                          item.complete
                            ? "text-zinc-200"
                            : "text-zinc-400"
                        }`}
                      >

                        {item.item}

                      </p>


                      <p className="mt-1 text-[10px] uppercase tracking-wider text-zinc-700">

                        {item.category}

                        {item.importance
                          ? ` • ${item.importance}`
                          : ""}

                      </p>

                    </div>

                  </div>
                ),
              )}

            </div>
          ) : (
            <EmptyText text="No readiness checklist was returned." />
          )}

        </Panel>


        {/* ----------------------------------------------------
            SOURCE EVIDENCE
        ---------------------------------------------------- */}

        <Panel
          title="Source evidence & verification"
          icon={
            <ShieldCheck className="h-4 w-4 text-cyan-300" />
          }
        >

          <div className="grid gap-3 sm:grid-cols-2">

            <InfoBox
              label="Verification level"
              value={
                sourceEvidence.verification_score ||
                opportunity.trust_label ||
                "Unknown"
              }
            />


            <InfoBox
              label="Freshness"
              value={
                freshness.freshness_label ||
                "Unknown"
              }
            />

          </div>


          <div className="mt-5 space-y-2">

            {evidence.length > 0 ? (
              evidence.map(
                (
                  item,
                  index,
                ) => (
                  <div
                    key={`${item}-${index}`}
                    className="rounded-xl bg-white/[0.025] p-3 text-xs leading-5 text-zinc-400"
                  >

                    • {item}

                  </div>
                ),
              )
            ) : (
              <EmptyText text="No additional source evidence was returned." />
            )}

          </div>


          <div className="mt-5 flex flex-wrap gap-2">

            {sourceEvidence.source_url && (
              <a
                href={
                  sourceEvidence.source_url
                }
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-2.5 text-xs font-medium text-zinc-300 transition hover:border-cyan-300/25 hover:text-white"
              >

                View Source

                <ExternalLink className="h-3.5 w-3.5" />

              </a>
            )}


            {applicationUrl && (
              <button
                onClick={handleApply}
                className="inline-flex items-center gap-2 rounded-xl bg-cyan-300 px-4 py-2.5 text-xs font-semibold text-black transition hover:bg-cyan-200"
              >

                Open Application

                <ArrowRight className="h-3.5 w-3.5" />

              </button>
            )}

          </div>

        </Panel>


        {/* ----------------------------------------------------
            PORTFOLIO IMPACT
        ---------------------------------------------------- */}

        <Panel
          title="Portfolio impact"
          icon={
            <FolderKanban className="h-4 w-4 text-violet-300" />
          }
        >

          <div className="rounded-xl border border-violet-300/10 bg-violet-400/[0.04] p-4">

            <p className="text-[10px] uppercase tracking-[0.16em] text-violet-200/70">

              Recommended portfolio move

            </p>


            <p className="mt-2 text-sm leading-6 text-zinc-300">

              {portfolioImpact.recommended_project ||
                "Strengthen an existing project with opportunity-relevant evidence."}

            </p>

          </div>


          <div className="mt-4 grid gap-3 sm:grid-cols-3">

            <InfoBox
              label="Existing projects"
              value={String(
                portfolioImpact.existing_projects ??
                  0,
              )}
            />


            <InfoBox
              label="Skill gaps"
              value={String(
                portfolioImpact.missing_skill_count ??
                  missingSkills.length,
              )}
            />


            <InfoBox
              label="Portfolio value"
              value={
                portfolioValue > 0
                  ? `${portfolioValue}%`
                  : "—"
              }
            />

          </div>


          <div className="mt-5 rounded-xl bg-black/20 p-4">

            <p className="text-xs font-medium text-white">

              Proof strategy

            </p>


            <p className="mt-2 text-xs leading-5 text-zinc-500">

              Convert the strongest missing requirement into
              something a recruiter can actually inspect:
              a working project, repository, demo, case study,
              assessment result or documented contribution.

            </p>

          </div>

        </Panel>

      </div>


      {/* ======================================================
          BOTTOM ACTION BAR
      ====================================================== */}

      <div className="mt-6 flex flex-col gap-4 rounded-2xl border border-white/8 bg-white/[0.02] p-5 sm:flex-row sm:items-center sm:justify-between">

        <div className="flex items-start gap-3">

          <div className="rounded-xl bg-violet-400/10 p-2.5">

            <TrendingUp className="h-4 w-4 text-violet-300" />

          </div>


          <div>

            <p className="text-xs uppercase tracking-wider text-zinc-600">

              Decision signal

            </p>


            <p className="mt-1 text-sm text-zinc-300">

              {matchScore >= 80
                ? "This is a strong profile fit. Focus on application quality and evidence."
                : matchScore >= 60
                  ? "This is worth pursuing. Close the highest-impact gaps without delaying the application."
                  : "This opportunity requires meaningful preparation. Use the workspace to prioritize the highest-return gaps."}

            </p>

          </div>

        </div>


        <div className="flex shrink-0 gap-2">

          <button
            onClick={onClose}
            className="rounded-xl border border-white/10 px-4 py-2.5 text-sm text-zinc-400 transition hover:border-white/20 hover:text-white"
          >

            Back

          </button>


          {applicationUrl && (
            <button
              onClick={handleApply}
              className="inline-flex items-center gap-2 rounded-xl bg-cyan-300 px-5 py-2.5 text-sm font-semibold text-black transition hover:bg-cyan-200"
            >

              Continue to Application

              <ArrowRight className="h-4 w-4" />

            </button>
          )}

        </div>

      </div>

    </section>
  );
}


// ============================================================
// METRIC
// ============================================================

function Metric({
  icon,
  label,
  value,
  detail,
}: {
  icon: ReactNode;
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/[0.025] p-4">

      <div className="flex items-center gap-2 text-zinc-600">

        {icon}

        <span className="text-[10px] uppercase tracking-[0.16em]">

          {label}

        </span>

      </div>


      <div className="mt-3 text-2xl font-semibold text-white">

        {value}

      </div>


      <p className="mt-1 text-[11px] text-zinc-600">

        {detail}

      </p>

    </div>
  );
}


// ============================================================
// PANEL
// ============================================================

function Panel({
  title,
  icon,
  children,
}: {
  title: string;
  icon: ReactNode;
  children: ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/[0.02] p-5">

      <div className="mb-5 flex items-center gap-2">

        {icon}

        <h3 className="text-sm font-semibold text-white">

          {title}

        </h3>

      </div>

      {children}

    </div>
  );
}


// ============================================================
// INFO BOX
// ============================================================

function InfoBox({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-xl bg-white/[0.025] p-3">

      <p className="text-[9px] uppercase tracking-wider text-zinc-700">

        {label}

      </p>

      <p className="mt-1 text-sm font-medium text-zinc-200">

        {value}

      </p>

    </div>
  );
}


// ============================================================
// EMPTY TEXT
// ============================================================

function EmptyText({
  text,
}: {
  text: string;
}) {
  return (
    <p className="text-xs leading-5 text-zinc-600">

      {text}

    </p>
  );
}