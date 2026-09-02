import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Activity,
  AlertTriangle,
  ArrowLeft,
  Brain,
  CheckCircle2,
  ChevronRight,
  GitCompare,
  LoaderCircle,
  MapPin,
  Radar,
  Search,
  ShieldCheck,
  Sparkles,
  TrendingUp,
} from "lucide-react";

import {
  compareOpportunities,
  getFuturePath,
  getHealth,
  getProfileIntelligence,
  getWorkspace,
  simulateReadiness,
  getApplicationStrategy,
  parseResume,
  getHiddenOpportunities,
  getMatch,
  getPreparation,
  getStudentProfile,
  getWhyNot,
  saveStudentProfile,
  searchOpportunities,
} from "./api";

import ProfileModal from "./components/ProfileModal";
import OpportunityWorkspace from "./components/OpportunityWorkspace";

import {
  demoProfile,
} from "./data/demoProfile";

import type {
  ComparisonItem,
  FuturePathResponse,
  HiddenRecommendation,
  MatchResponse,
  Opportunity,
  PreparationResponse,
  StudentProfile,
  WhyNotResponse,
  ProfileIntelligence,
  ReadinessSimulationResponse,
  ApplicationStrategyResponse,
  OpportunityWorkspace as WorkspaceData,
} from "./types";


type AppView =
  | "dashboard"
  | "preparation"
  | "future"
  | "comparison";


const filters = [
  "All",
  "Internship",
  "Hackathon",
  "Scholarship",
  "Competition",
  "Job",
];


function formatTrustLabel(
  score: number,
): string {

  if (score >= 90) {
    return "High confidence";
  }

  if (score >= 75) {
    return "Good confidence";
  }

  if (score >= 60) {
    return "Moderate confidence";
  }

  return "Limited evidence";
}


function getTrustScore(
  opportunity: Opportunity,
): number {

  const backendScore =
    Number(
      opportunity.trust_score,
    );

  if (
    Number.isFinite(
      backendScore,
    ) &&
    backendScore > 0
  ) {
    return Math.max(
      0,
      Math.min(
        100,
        backendScore,
      ),
    );
  }

  const source =
    (
      opportunity.source_url ||
      opportunity.application_url ||
      ""
    ).toLowerCase();

  if (
    source.includes(".gov") ||
    source.includes(".edu") ||
    source.includes("careers") ||
    source.includes("jobs")
  ) {
    return 85;
  }

  if (
    opportunity.verification_score ===
    "High"
  ) {
    return 90;
  }

  if (
    opportunity.verification_score ===
    "Medium"
  ) {
    return 75;
  }

  return 55;
}


function App() {

  // ==========================================================
  // CORE STATE
  // ==========================================================

  const [
    profile,
    setProfile,
  ] = useState<StudentProfile>(
    demoProfile,
  );


  const [
    opportunities,
    setOpportunities,
  ] = useState<Opportunity[]>(
    [],
  );


  const [
    selected,
    setSelected,
  ] = useState<Opportunity | null>(
    null,
  );


  const [
    match,
    setMatch,
  ] = useState<MatchResponse | null>(
    null,
  );


  const [
    whyNot,
    setWhyNot,
  ] = useState<WhyNotResponse | null>(
    null,
  );


  const [
    preparation,
    setPreparation,
  ] = useState<PreparationResponse | null>(
    null,
  );


  const [
    futurePath,
    setFuturePath,
  ] = useState<FuturePathResponse | null>(
    null,
  );


  const [
    hidden,
    setHidden,
  ] = useState<HiddenRecommendation[]>(
    [],
  );


  const [
    compareIds,
    setCompareIds,
  ] = useState<number[]>(
    [],
  );


  const [
    comparison,
    setComparison,
  ] = useState<ComparisonItem[]>(
    [],
  );


  const [
    view,
    setView,
  ] = useState<AppView>(
    "dashboard",
  );


  // ==========================================================
  // SEARCH / LOADING STATE
  // ==========================================================

  const [
    query,
    setQuery,
  ] = useState("");


  const [
    filter,
    setFilter,
  ] = useState("All");


  const [
    loading,
    setLoading,
  ] = useState(false);


  const [
    analysisLoading,
    setAnalysisLoading,
  ] = useState(false);


  const [
    backendOnline,
    setBackendOnline,
  ] = useState(false);


  const [
    status,
    setStatus,
  ] = useState(
    "Engine ready. Build your profile and launch discovery.",
  );


  const [
    profileOpen,
    setProfileOpen,
  ] = useState(false);


  // ==========================================================
  // PROFILE INTELLIGENCE
  // ==========================================================

  const [
    profileIntel,
    setProfileIntel,
  ] = useState<ProfileIntelligence | null>(
    null,
  );


  // ==========================================================
  // READINESS SIMULATOR
  // ==========================================================

  const [
    simulation,
    setSimulation,
  ] = useState<ReadinessSimulationResponse | null>(
    null,
  );


  const [
    simulationSkills,
    setSimulationSkills,
  ] = useState("");


  const [
    simulationProjects,
    setSimulationProjects,
  ] = useState(0);


  // ==========================================================
  // APPLICATION STRATEGY
  // ==========================================================

  const [
    strategy,
    setStrategy,
  ] = useState<ApplicationStrategyResponse | null>(
    null,
  );


  const [
    strategyLoading,
    setStrategyLoading,
  ] = useState(false);


  // ==========================================================
  // RESUME
  // ==========================================================

  const [
    resumeResult,
    setResumeResult,
  ] = useState<unknown>(
    null,
  );


  const [
    resumeLoading,
    setResumeLoading,
  ] = useState(false);


  // ==========================================================
  // OPPORTUNITY WORKSPACE
  // ==========================================================

  const [
    workspace,
    setWorkspace,
  ] = useState<WorkspaceData | null>(
    null,
  );


  const [
    workspaceLoading,
    setWorkspaceLoading,
  ] = useState(false);


  const [
    workspaceOpen,
    setWorkspaceOpen,
  ] = useState(false);


  // ==========================================================
  // INITIALIZATION
  // ==========================================================

  useEffect(() => {

    async function initialize() {

      try {

        await getHealth();

        setBackendOnline(true);


        const saved =
          await getStudentProfile();


        if (
          saved?.name ||
          saved?.skills?.length
        ) {
          setProfile(saved);
        }


        try {

          const hiddenData =
            await getHiddenOpportunities();

          setHidden(
            Array.isArray(hiddenData)
              ? hiddenData
              : [],
          );

        } catch {

          setHidden([]);

        }


        try {

          const intelligence =
            await getProfileIntelligence();

          setProfileIntel(
            intelligence,
          );

        } catch {

          setProfileIntel(null);

        }

      } catch (error) {

        console.error(
          "Initialization failed:",
          error,
        );

        setBackendOnline(false);

      }

    }


    void initialize();

  }, []);


  // ==========================================================
  // SAFE DATA
  // ==========================================================

  const safeOpportunities =
    Array.isArray(opportunities)
      ? opportunities
      : [];


  const safeHidden =
    Array.isArray(hidden)
      ? hidden
      : [];


  const safeComparison =
    Array.isArray(comparison)
      ? comparison
      : [];


  // ==========================================================
  // FILTERED OPPORTUNITIES
  // ==========================================================

  const filtered =
    useMemo(() => {

      const normalizedQuery =
        query
          .trim()
          .toLowerCase();


      return safeOpportunities.filter(
        (item) => {

          const text = [
            item.title,
            item.organization,
            item.company,
            item.type,
            item.description,
            ...(item.skills || []),
          ]
            .filter(Boolean)
            .join(" ")
            .toLowerCase();


          const searchMatch =
            !normalizedQuery ||
            text.includes(
              normalizedQuery,
            );


          const filterMatch =
            filter === "All" ||
            (
              item.type
                ?.toLowerCase()
                .includes(
                  filter.toLowerCase(),
                )
            ) ||
            text.includes(
              filter.toLowerCase(),
            );


          return (
            searchMatch &&
            filterMatch
          );

        },
      );

    }, [
      safeOpportunities,
      query,
      filter,
    ]);


  // ==========================================================
  // OPEN WORKSPACE
  // ==========================================================

  async function openWorkspace(
    opportunity: Opportunity,
  ) {

    setSelected(
      opportunity,
    );

    setWorkspaceOpen(true);

    setWorkspaceLoading(true);

    setWorkspace(null);

    try {

      const data =
        await getWorkspace(
          opportunity.id,
        );

      setWorkspace(
        data,
      );

    } catch (error) {

      console.error(
        "Workspace loading failed:",
        error,
      );

      setStatus(
        "Opportunity workspace could not be loaded.",
      );

    } finally {

      setWorkspaceLoading(false);

    }

  }


  // ==========================================================
  // LAUNCH ENGINE
  // ==========================================================

  async function launchEngine() {

    setLoading(true);

    setStatus(
      "Running multi-query discovery...",
    );

    try {

      const saved =
        await saveStudentProfile(
          profile,
        );

      setProfile(
        saved,
      );


      setStatus(
        "Searching live opportunity sources...",
      );


      const result =
        await searchOpportunities(
          saved,
        );


      const discovered =
        Array.isArray(
          result?.opportunities,
        )
          ? result.opportunities
          : [];


      setOpportunities(
        discovered,
      );


      setSelected(
        discovered[0] ||
        null,
      );


      setComparison([]);

      setCompareIds([]);

      setPreparation(null);

      setFuturePath(null);

      setWorkspace(null);

      setWorkspaceOpen(false);


      setStatus(
        `${discovered.length} opportunities discovered and ranked.`,
      );


      if (
        discovered[0]
      ) {

        await selectOpportunity(
          discovered[0],
        );

      }


      try {

        const hiddenData =
          await getHiddenOpportunities();

        setHidden(
          Array.isArray(hiddenData)
            ? hiddenData
            : [],
        );

      } catch {

        setHidden([]);

      }


      try {

        setProfileIntel(
          await getProfileIntelligence(),
        );

      } catch {

        setProfileIntel(null);

      }

    } catch (error) {

      console.error(
        "Search failed:",
        error,
      );

      setStatus(
        "Search failed. Check backend health and API configuration.",
      );

    } finally {

      setLoading(false);

    }

  }


  // ==========================================================
  // SELECT OPPORTUNITY
  // ==========================================================

  async function selectOpportunity(
    opportunity: Opportunity,
  ) {

    setSelected(
      opportunity,
    );


    setMatch(null);

    setWhyNot(null);

    setPreparation(null);

    setFuturePath(null);

    setStrategy(null);

    setSimulation(null);


    setView(
      "dashboard",
    );


    const [
      matchResult,
      whyNotResult,
    ] =
      await Promise.allSettled([
        getMatch(
          opportunity.id,
        ),

        getWhyNot(
          opportunity.id,
        ),
      ]);


    if (
      matchResult.status ===
      "fulfilled"
    ) {

      setMatch(
        matchResult.value,
      );

    } else {

      console.error(
        "Match request failed:",
        matchResult.reason,
      );

    }


    if (
      whyNotResult.status ===
      "fulfilled"
    ) {

      setWhyNot(
        whyNotResult.value,
      );

    } else {

      console.error(
        "Why Not request failed:",
        whyNotResult.reason,
      );

    }

  }


  // ==========================================================
  // PREPARATION
  // ==========================================================

  async function openPreparation() {

    if (!selected) {
      return;
    }


    setAnalysisLoading(true);

    try {

      const data =
        await getPreparation(
          selected.id,
        );


      setPreparation(
        data,
      );


      setView(
        "preparation",
      );


      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });

    } catch (error) {

      console.error(
        error,
      );

      setStatus(
        "Could not generate the preparation plan.",
      );

    } finally {

      setAnalysisLoading(false);

    }

  }


  // ==========================================================
  // FUTURE PATH
  // ==========================================================

  async function openFuturePath() {

    if (!selected) {
      return;
    }


    setAnalysisLoading(true);

    try {

      const data =
        await getFuturePath(
          selected.id,
        );


      setFuturePath(
        data,
      );


      setView(
        "future",
      );


      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });

    } catch (error) {

      console.error(
        error,
      );

      setStatus(
        "Could not generate the future opportunity path.",
      );

    } finally {

      setAnalysisLoading(false);

    }

  }


  // ==========================================================
  // COMPARISON
  // ==========================================================

  function toggleCompare(
    id: number,
  ) {

    setCompareIds(
      (current) => {

        if (
          current.includes(id)
        ) {

          return current.filter(
            (item) =>
              item !== id,
          );

        }


        if (
          current.length >= 3
        ) {

          setStatus(
            "You can compare a maximum of 3 opportunities.",
          );

          return current;

        }


        return [
          ...current,
          id,
        ];

      },
    );

  }


  async function runComparison() {

    if (
      compareIds.length < 2
    ) {

      setStatus(
        "Select at least 2 opportunities to compare.",
      );

      return;

    }


    setAnalysisLoading(true);

    try {

      const data =
        await compareOpportunities(
          compareIds,
        );


      setComparison(
        Array.isArray(
          data.comparison,
        )
          ? data.comparison
          : [],
      );


      setView(
        "comparison",
      );


      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });

    } catch (error) {

      console.error(
        error,
      );

      setStatus(
        "Comparison could not be generated.",
      );

    } finally {

      setAnalysisLoading(false);

    }

  }


  // ==========================================================
  // READINESS SIMULATION
  // ==========================================================

  async function runSimulation() {

    if (!selected) {
      return;
    }


    const skills =
      simulationSkills
        .split(",")
        .map(
          (skill) =>
            skill.trim(),
        )
        .filter(Boolean);


    try {

      setAnalysisLoading(
        true,
      );


      const result =
        await simulateReadiness(
          selected.id,
          skills,
          simulationProjects,
        );


      setSimulation(
        result,
      );

    } catch (error) {

      console.error(
        error,
      );

      setStatus(
        "Readiness simulation could not be generated.",
      );

    } finally {

      setAnalysisLoading(
        false,
      );

    }

  }


  // ==========================================================
  // RESUME
  // ==========================================================

  async function handleResumeUpload(
    file: File,
  ) {

    try {

      setResumeLoading(
        true,
      );


      const text =
        await file.text();


      const parsed =
        await parseResume(
          text,
        );


      setResumeResult(
        parsed,
      );


      setStatus(
        "Resume analysed. Extracted profile evidence is ready to review.",
      );

    } catch (error) {

      console.error(
        error,
      );

      setStatus(
        "Resume analysis failed. Check the backend resume parser.",
      );

    } finally {

      setResumeLoading(
        false,
      );

    }

  }


  // ==========================================================
  // APPLICATION STRATEGY
  // ==========================================================

  async function openApplicationStrategy() {

    if (!selected) {
      return;
    }


    try {

      setStrategyLoading(
        true,
      );


      const result =
        await getApplicationStrategy(
          selected.id,
        );


      setStrategy(
        result,
      );

    } catch (error) {

      console.error(
        error,
      );

      setStatus(
        "Application strategy could not be generated.",
      );

    } finally {

      setStrategyLoading(
        false,
      );

    }

  }


  // ==========================================================
  // APPLY
  // ==========================================================

  function claim(
    opportunity: Opportunity,
  ) {

    const url =
      opportunity.application_url ||
      opportunity.source_url;


    if (!url) {

      setStatus(
        "No verified application destination was returned.",
      );

      return;

    }


    window.open(
      url,
      "_blank",
      "noopener,noreferrer",
    );

  }


  // ==========================================================
  // BACK TO DASHBOARD
  // ==========================================================

  function backToDashboard() {

    setView(
      "dashboard",
    );


    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });

  }


  // ==========================================================
  // PIPELINE METRICS
  // ==========================================================

  const pipeline = {

    discovered:
      safeOpportunities.length,

    strongMatches:
      safeOpportunities.filter(
        (item) =>
          Number(
            item.match_score || 0,
          ) >= 70,
      ).length,

    urgent:
      safeOpportunities.filter(
        (item) =>
          [
            "Urgent",
            "Critical",
          ].includes(
            item
              .deadline_intelligence
              ?.urgency || "",
          ),
      ).length,

    selected:
      selected
        ? 1
        : 0,

  };


  // ==========================================================
  // BACK BUTTON
  // ==========================================================

  function BackButton() {

    return (
      <button
        onClick={backToDashboard}
        className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-2.5 text-sm text-zinc-300 transition hover:border-cyan-300/30 hover:bg-white/[0.06]"
      >

        <ArrowLeft className="h-4 w-4" />

        Back to Dashboard

      </button>
    );

  }


  // ==========================================================
  // PREPARATION VIEW
  // ==========================================================

  if (
    view === "preparation"
  ) {

    return (
      <main className="min-h-screen bg-[#0a0a0c] text-white">

        <header className="border-b border-white/8 bg-[#0a0a0c]/90">

          <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-4">

            <BackButton />

            <span className="text-xs text-zinc-500">
              Preparation Intelligence
            </span>

          </div>

        </header>


        <section className="mx-auto max-w-6xl px-5 py-10">

          <div className="glass rounded-3xl p-6 sm:p-8">

            <div className="flex flex-col justify-between gap-6 lg:flex-row">

              <div>

                <div className="inline-flex items-center gap-2 rounded-full border border-cyan-300/20 bg-cyan-300/10 px-3 py-1.5 text-xs text-cyan-200">

                  <Brain className="h-4 w-4" />

                  Personalised gap-closing plan

                </div>


                <h1 className="mt-5 text-3xl font-semibold">
                  Preparation Roadmap
                </h1>


                <p className="mt-3 text-sm text-zinc-400">
                  {selected?.title ||
                    preparation?.opportunity}
                </p>

              </div>


              <div className="rounded-2xl border border-cyan-300/20 bg-cyan-300/[0.06] px-6 py-5 text-center">

                <div className="text-4xl font-semibold text-cyan-300">
                  {preparation?.readiness_percentage ?? 0}%
                </div>

                <div className="mt-1 text-xs text-zinc-500">
                  CURRENT READINESS
                </div>

              </div>

            </div>


            <div className="mt-8 grid gap-4 md:grid-cols-2">

              <div className="rounded-2xl border border-emerald-400/15 bg-emerald-400/[0.04] p-5">

                <div className="flex items-center gap-2 text-sm text-emerald-200">

                  <CheckCircle2 className="h-4 w-4" />

                  Skills you already have

                </div>


                <div className="mt-4 flex flex-wrap gap-2">

                  {(preparation?.current_skills || [])
                    .map(
                      (skill, index) => (
                        <span
                          key={`${skill}-${index}`}
                          className="rounded-lg bg-emerald-400/10 px-3 py-1.5 text-xs text-emerald-200"
                        >
                          {skill}
                        </span>
                      ),
                    )}

                </div>

              </div>


              <div className="rounded-2xl border border-amber-400/15 bg-amber-400/[0.04] p-5">

                <div className="flex items-center gap-2 text-sm text-amber-200">

                  <AlertTriangle className="h-4 w-4" />

                  Priority skill gaps

                </div>


                <div className="mt-4 flex flex-wrap gap-2">

                  {(preparation?.missing_skills || [])
                    .map(
                      (skill, index) => (
                        <span
                          key={`${skill}-${index}`}
                          className="rounded-lg bg-amber-400/10 px-3 py-1.5 text-xs text-amber-200"
                        >
                          {skill}
                        </span>
                      ),
                    )}

                </div>

              </div>

            </div>


            <div className="mt-10">

              <h2 className="text-2xl font-semibold">
                Close the gap step by step
              </h2>


              <div className="mt-6 space-y-5">

                {(preparation?.roadmap || [])
                  .map(
                    (item, index) => (

                      <div
                        key={`${item.skill}-${index}`}
                        className="rounded-2xl border border-white/8 bg-white/[0.025] p-5"
                      >

                        <div className="flex justify-between gap-4">

                          <div>

                            <div className="text-xs text-zinc-500">
                              STEP {index + 1}
                            </div>

                            <h3 className="mt-1 text-xl font-semibold text-cyan-100">
                              {item.skill}
                            </h3>

                          </div>


                          {item.priority && (
                            <span className="h-fit rounded-full bg-violet-500/10 px-3 py-1 text-xs text-violet-200">
                              {item.priority} priority
                            </span>
                          )}

                        </div>


                        {(item.steps || []).length > 0 && (

                          <div className="mt-5 grid gap-2 sm:grid-cols-2">

                            {(item.steps || [])
                              .map(
                                (
                                  step,
                                  stepIndex,
                                ) => (

                                  <div
                                    key={`${step}-${stepIndex}`}
                                    className="rounded-xl bg-black/20 p-3 text-sm text-zinc-300"
                                  >
                                    {stepIndex + 1}. {step}
                                  </div>

                                ),
                              )}

                          </div>

                        )}


                        {item.project && (

                          <div className="mt-5 rounded-xl border border-cyan-300/10 bg-cyan-300/[0.04] p-4">

                            <div className="text-xs uppercase tracking-wider text-cyan-200">
                              Portfolio mission
                            </div>

                            <p className="mt-2 text-sm text-zinc-400">
                              {item.project}
                            </p>

                          </div>

                        )}

                      </div>

                    ),
                  )}

              </div>

            </div>

          </div>

        </section>

      </main>
    );

  }


  // ==========================================================
  // FUTURE VIEW
  // ==========================================================

  if (
    view === "future"
  ) {

    return (
      <main className="min-h-screen bg-[#0a0a0c] text-white">

        <header className="border-b border-white/8 bg-[#0a0a0c]/90">

          <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-4">

            <BackButton />

            <span className="text-xs text-zinc-500">
              Future Intelligence
            </span>

          </div>

        </header>


        <section className="mx-auto max-w-6xl px-5 py-10">

          <div className="glass rounded-3xl p-6 sm:p-8">

            <div className="max-w-3xl">

              <div className="inline-flex items-center gap-2 rounded-full border border-violet-400/20 bg-violet-500/10 px-3 py-1.5 text-xs text-violet-200">

                <TrendingUp className="h-4 w-4" />

                Long-term opportunity strategy

              </div>


              <h1 className="mt-5 text-3xl font-semibold">
                Your Future Opportunity Path
              </h1>


              <p className="mt-4 text-sm leading-7 text-zinc-400">
                {futurePath?.message}
              </p>

            </div>


            <div className="mt-10 space-y-6">

              {(futurePath?.future_path || [])
                .map(
                  (item, index) => (

                    <div
                      key={`${item.skill}-${index}`}
                      className="rounded-2xl border border-white/8 bg-white/[0.025] p-6"
                    >

                      <div className="flex justify-between gap-4">

                        <div>

                          <div className="text-xs uppercase tracking-wider text-zinc-500">
                            Growth Phase {index + 1}
                          </div>

                          <h2 className="mt-2 text-2xl font-semibold text-violet-100">
                            {item.skill}
                          </h2>

                        </div>


                        {item.priority && (

                          <span className="h-fit rounded-full bg-violet-500/10 px-3 py-1 text-xs text-violet-200">
                            {item.priority}
                          </span>

                        )}

                      </div>


                      <p className="mt-5 text-sm leading-7 text-zinc-400">
                        {item.goal}
                      </p>


                      {item.why_it_matters && (

                        <div className="mt-5 rounded-xl bg-violet-500/[0.06] p-4">

                          <div className="text-xs uppercase tracking-wider text-violet-200">
                            Why this matters
                          </div>

                          <p className="mt-2 text-sm text-zinc-400">
                            {item.why_it_matters}
                          </p>

                        </div>

                      )}


                      {(item.milestones || []).length > 0 && (

                        <div className="mt-5">

                          <div className="text-xs uppercase tracking-wider text-zinc-500">
                            Milestones
                          </div>

                          <div className="mt-3 space-y-2">

                            {(item.milestones || [])
                              .map(
                                (
                                  milestone,
                                  milestoneIndex,
                                ) => (

                                  <div
                                    key={`${milestone}-${milestoneIndex}`}
                                    className="flex gap-3 rounded-xl bg-black/20 p-3 text-sm text-zinc-300"
                                  >

                                    <ChevronRight className="h-4 w-4 shrink-0 text-violet-300" />

                                    {milestone}

                                  </div>

                                ),
                              )}

                          </div>

                        </div>

                      )}


                      {(item.projects || []).length > 0 && (

                        <div className="mt-5">

                          <div className="text-xs uppercase tracking-wider text-zinc-500">
                            Portfolio Proof
                          </div>

                          <div className="mt-3 grid gap-3 md:grid-cols-2">

                            {(item.projects || [])
                              .map(
                                (
                                  project,
                                  projectIndex,
                                ) => (

                                  <div
                                    key={`${project}-${projectIndex}`}
                                    className="rounded-xl border border-cyan-300/10 bg-cyan-300/[0.04] p-4 text-sm text-zinc-300"
                                  >
                                    {project}
                                  </div>

                                ),
                              )}

                          </div>

                        </div>

                      )}

                    </div>

                  ),
                )}

            </div>

          </div>

        </section>

      </main>
    );

  }


  // ==========================================================
  // COMPARISON VIEW
  // ==========================================================

  if (
    view === "comparison"
  ) {

    return (
      <main className="min-h-screen bg-[#0a0a0c] text-white">

        <header className="border-b border-white/8 bg-[#0a0a0c]/90">

          <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-4">

            <BackButton />

            <span className="text-xs text-zinc-500">
              Decision Intelligence
            </span>

          </div>

        </header>


        <section className="mx-auto max-w-6xl px-5 py-10">

          <div className="glass rounded-3xl p-6 sm:p-8">

            <h1 className="text-3xl font-semibold">
              Opportunity Comparison
            </h1>


            <p className="mt-3 text-sm text-zinc-400">
              Compare profile fit, source confidence and application timing before deciding where to focus.
            </p>


            <div className="mt-8 grid gap-5 md:grid-cols-2 xl:grid-cols-3">

              {safeComparison.map(
                (item, index) => (

                  <div
                    key={`${item.id}-${index}`}
                    className="rounded-2xl border border-white/8 bg-white/[0.025] p-5"
                  >

                    <div className="text-xs uppercase tracking-wider text-zinc-500">
                      {item.organization}
                    </div>


                    <h2 className="mt-2 text-lg font-semibold">
                      {item.title}
                    </h2>


                    <div className="mt-6 grid grid-cols-2 gap-3">

                      <div className="rounded-xl bg-cyan-300/[0.06] p-4">

                        <div className="text-2xl font-semibold text-cyan-300">
                          {item.match_score}%
                        </div>

                        <div className="text-xs text-zinc-500">
                          Profile Match
                        </div>

                      </div>


                      <div className="rounded-xl bg-violet-500/[0.06] p-4">

                        <div className="text-2xl font-semibold text-violet-200">
                          {item.trust_score}%
                        </div>

                        <div className="text-xs text-zinc-500">
                          Trust
                        </div>

                      </div>

                    </div>


                    <div className="mt-5 rounded-xl bg-black/20 p-4">

                      <div className="text-xs uppercase tracking-wider text-zinc-500">
                        Deadline
                      </div>

                      <div className="mt-2 text-sm text-zinc-300">
                        {item.deadline ||
                          "Not specified"}
                      </div>

                    </div>

                  </div>

                ),
              )}

            </div>

          </div>

        </section>

      </main>
    );

  }


  // ==========================================================
  // MAIN DASHBOARD
  // ==========================================================

  return (
    <main className="min-h-screen bg-[#0a0a0c] text-white">

      {/* HEADER */}

      <header className="sticky top-0 z-50 border-b border-white/8 bg-[#0a0a0c]/85 backdrop-blur-xl">

        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 lg:px-8">

          <div className="flex items-center gap-3">

            <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-300/25 bg-cyan-300/10">

              <Radar className="h-5 w-5 text-cyan-300" />

            </div>


            <div>

              <div className="font-semibold">
                Student Opportunity Engine
              </div>

              <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-500">
                Opportunity Intelligence
              </div>

            </div>

          </div>


          <div className="flex items-center gap-3">

            <div className="hidden items-center gap-2 text-xs text-zinc-500 sm:flex">

              <span
                className={`h-2 w-2 rounded-full ${
                  backendOnline
                    ? "bg-emerald-400"
                    : "bg-red-400"
                }`}
              />

              {backendOnline
                ? "Backend online"
                : "Backend offline"}

            </div>


            <button
              onClick={() =>
                setProfileOpen(true)
              }
              className="rounded-xl border border-white/10 px-4 py-2 text-sm text-zinc-200"
            >
              Edit Profile
            </button>

          </div>

        </div>

      </header>


      {/* HERO */}

      <section className="grid-background border-b border-white/5">

        <div className="mx-auto max-w-7xl px-5 py-20 lg:px-8">

          <div className="max-w-4xl">

            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-cyan-300/20 bg-cyan-300/[0.06] px-4 py-2 text-xs text-cyan-200">

              <Sparkles className="h-4 w-4" />

              AI-ranked student opportunity intelligence

            </div>


            <h1 className="text-5xl font-semibold tracking-tight sm:text-6xl">

              Fuel Your Future.

              <span className="block text-cyan-300">
                Discover Better Opportunities.
              </span>

            </h1>


            <p className="mt-6 max-w-2xl text-base leading-7 text-zinc-400">

              Discover → Verify → Match → Diagnose → Prepare → Apply.

              <br />

              Not just opportunity listings. Understand your fit, identify your gaps and build a path to stronger opportunities.

            </p>


            {/* SEARCH */}

            <div className="mt-10 glass rounded-2xl p-3">

              <div className="flex flex-col gap-3 lg:flex-row">

                <div className="flex flex-1 items-center gap-3 rounded-xl bg-black/20 px-4">

                  <Search className="h-5 w-5 text-zinc-500" />

                  <input
                    value={query}
                    onChange={(event) =>
                      setQuery(
                        event.target.value,
                      )
                    }
                    placeholder="Search discovered opportunities..."
                    className="h-12 w-full bg-transparent text-sm outline-none"
                  />

                </div>


                <button
                  onClick={() =>
                    void launchEngine()
                  }
                  disabled={loading}
                  className="neon-button flex min-h-12 items-center justify-center gap-2 rounded-xl px-6 font-semibold disabled:opacity-60"
                >

                  {loading ? (
                    <LoaderCircle className="h-5 w-5 animate-spin" />
                  ) : (
                    <Activity className="h-5 w-5" />
                  )}

                  {loading
                    ? "Scanning..."
                    : "Launch Engine"}

                </button>

              </div>


              <div className="mt-3 flex flex-wrap gap-2">

                {filters.map(
                  (item) => (

                    <button
                      key={item}
                      onClick={() =>
                        setFilter(item)
                      }
                      className={`rounded-lg px-3 py-2 text-xs ${
                        filter === item
                          ? "bg-cyan-300 text-black"
                          : "bg-white/[0.04] text-zinc-400"
                      }`}
                    >
                      {item}
                    </button>

                  ),
                )}

              </div>

            </div>


            <div className="mt-5 flex items-center gap-2 text-sm text-zinc-500">

              <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-300" />

              {status}

            </div>

          </div>

        </div>

      </section>


      {/* PIPELINE */}

      <section className="mx-auto max-w-7xl px-5 py-10 lg:px-8">

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

          {[
            [
              "Discovered",
              pipeline.discovered,
            ],
            [
              "Strong Matches",
              pipeline.strongMatches,
            ],
            [
              "Deadline Pressure",
              pipeline.urgent,
            ],
            [
              "Currently Analysing",
              pipeline.selected,
            ],
          ].map(
            ([label, value], index) => (

              <div
                key={`${String(label)}-${index}`}
                className="glass rounded-2xl p-5"
              >

                <div className="text-xs uppercase tracking-[0.16em] text-zinc-500">
                  {String(label)}
                </div>

                <div className="mt-4 text-3xl font-semibold">
                  {String(value)}
                </div>

              </div>

            ),
          )}

        </div>

      </section>


      {/* OPPORTUNITIES */}

      <section className="mx-auto max-w-7xl px-5 pb-16 lg:px-8">

        <div className="mb-8 flex flex-col justify-between gap-4 md:flex-row md:items-end">

          <div>

            <p className="text-xs uppercase tracking-[0.2em] text-zinc-500">
              Ranked Live Feed
            </p>

            <h2 className="mt-2 text-3xl font-semibold">
              Opportunities worth your attention
            </h2>

          </div>


          <button
            onClick={() =>
              void runComparison()
            }
            disabled={
              compareIds.length < 2 ||
              analysisLoading
            }
            className="flex items-center gap-2 rounded-xl border border-violet-400/30 bg-violet-500/10 px-4 py-3 text-sm text-violet-200 disabled:opacity-40"
          >

            <GitCompare className="h-4 w-4" />

            Compare {compareIds.length}/3

          </button>

        </div>


        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_380px]">

          {/* OPPORTUNITY LIST */}

          <div className="space-y-4">

            {filtered.map(
              (
                opportunity,
                index,
              ) => {

                const isSelected =
                  selected?.id ===
                  opportunity.id;


                const comparing =
                  compareIds.includes(
                    opportunity.id,
                  );


                const trustScore =
                  getTrustScore(
                    opportunity,
                  );


                return (

                  <article
                    key={`${opportunity.id}-${index}`}
                    className={`glass glass-hover rounded-2xl p-5 ${
                      isSelected
                        ? "border-cyan-300/40"
                        : ""
                    }`}
                  >

                    <div className="flex flex-col gap-5 sm:flex-row sm:justify-between">

                      <div className="min-w-0">

                        <div className="mb-3 flex flex-wrap gap-2">

                          <span className="rounded-full bg-cyan-300/10 px-3 py-1 text-[11px] text-cyan-200">
                            {opportunity.type ||
                              "Opportunity"}
                          </span>


                          <span className="rounded-full bg-white/[0.05] px-3 py-1 text-[11px] text-zinc-400">

                            <ShieldCheck className="mr-1 inline h-3 w-3 text-emerald-300" />

                            Trust {trustScore}%

                          </span>

                        </div>


                        <h3 className="text-lg font-semibold">
                          {opportunity.title}
                        </h3>


                        <p className="mt-1 text-sm text-zinc-500">
                          {opportunity.organization ||
                            opportunity.company ||
                            "Unknown organization"}
                        </p>


                        <p className="mt-4 text-sm leading-6 text-zinc-400">
                          {opportunity.description ||
                            "No description available."}
                        </p>


                        <div className="mt-4 flex flex-wrap gap-2">

                          {(opportunity.skills || [])
                            .slice(0, 5)
                            .map(
                              (
                                skill,
                                skillIndex,
                              ) => (

                                <span
                                  key={`${skill}-${skillIndex}`}
                                  className="rounded-lg border border-white/8 px-2 py-1 text-xs text-zinc-400"
                                >
                                  {skill}
                                </span>

                              ),
                            )}

                        </div>


                        {opportunity.location && (

                          <div className="mt-4 flex items-center gap-2 text-xs text-zinc-500">

                            <MapPin className="h-4 w-4" />

                            {opportunity.location}

                          </div>

                        )}


                        <div className="mt-3 text-xs text-zinc-600">
                          {formatTrustLabel(
                            trustScore,
                          )}
                        </div>

                      </div>


                      <div className="flex min-w-[150px] flex-col gap-2">

                        <div className="rounded-xl bg-black/20 p-3 text-center">

                          <div className="text-2xl font-semibold text-cyan-300">
                            {opportunity.match_score ||
                              0}%
                          </div>

                          <div className="text-[10px] text-zinc-600">
                            MATCH
                          </div>

                        </div>


                        <button
                          onClick={() =>
                            void selectOpportunity(
                              opportunity,
                            )
                          }
                          className="rounded-xl border border-white/10 px-3 py-2 text-xs"
                        >
                          Analyse
                        </button>


                        <button
                          onClick={() =>
                            void openWorkspace(
                              opportunity,
                            )
                          }
                          className="rounded-xl border border-cyan-300/20 bg-cyan-300/10 px-3 py-2 text-xs font-semibold text-cyan-200"
                        >
                          Open Workspace
                        </button>


                        <button
                          onClick={() =>
                            claim(
                              opportunity,
                            )
                          }
                          className="rounded-xl bg-cyan-300 px-3 py-2 text-xs font-semibold text-black"
                        >
                          Apply
                        </button>


                        <button
                          onClick={() =>
                            toggleCompare(
                              opportunity.id,
                            )
                          }
                          className={`rounded-xl px-3 py-2 text-xs ${
                            comparing
                              ? "bg-violet-500 text-white"
                              : "border border-white/10 text-zinc-400"
                          }`}
                        >

                          {comparing
                            ? "Selected"
                            : "Compare"}

                        </button>

                      </div>

                    </div>

                  </article>

                );

              },
            )}


            {filtered.length === 0 && (

              <div className="glass rounded-2xl p-8 text-center">

                <Radar className="mx-auto h-8 w-8 text-zinc-600" />

                <p className="mt-4 text-sm text-zinc-500">
                  No opportunities match your current search.
                </p>

                <button
                  onClick={() => {
                    setQuery("");
                    setFilter("All");
                  }}
                  className="mt-4 rounded-xl border border-white/10 px-4 py-2 text-xs text-zinc-300"
                >
                  Clear filters
                </button>

              </div>

            )}

          </div>


          {/* SMART MATCH SIDEBAR */}

          <aside className="space-y-4 lg:sticky lg:top-24 lg:h-fit">

            <div className="glass violet-glow rounded-2xl p-5">

              <div className="flex items-center gap-3">

                <div className="rounded-xl bg-violet-500/10 p-3">

                  <Brain className="h-5 w-5 text-violet-300" />

                </div>


                <div>

                  <div className="text-xs uppercase tracking-[0.18em] text-zinc-500">
                    Smart Match
                  </div>

                  <div className="text-sm text-zinc-300">
                    Explainable profile intelligence
                  </div>

                </div>

              </div>


              {selected ? (

                <>

                  <h3 className="mt-6 font-semibold">
                    {selected.title}
                  </h3>


                  <div className="mt-5 text-5xl font-semibold text-cyan-300">
                    {match?.match_score ||
                      selected.match_score ||
                      0}%
                  </div>


                  <div className="mt-5">

                    <div className="text-xs uppercase tracking-wider text-zinc-500">
                      Skills you match
                    </div>


                    <div className="mt-3 flex flex-wrap gap-2">

                      {(match?.matched_skills || [])
                        .map(
                          (
                            skill,
                            index,
                          ) => (

                            <span
                              key={`${skill}-${index}`}
                              className="rounded-lg bg-emerald-400/10 px-2 py-1 text-xs text-emerald-200"
                            >
                              {skill}
                            </span>

                          ),
                        )}

                    </div>

                  </div>


                  <div className="mt-5">

                    <div className="text-xs uppercase tracking-wider text-zinc-500">
                      Skill gaps
                    </div>


                    <div className="mt-3 flex flex-wrap gap-2">

                      {(match?.missing_skills || [])
                        .map(
                          (
                            skill,
                            index,
                          ) => (

                            <span
                              key={`${skill}-${index}`}
                              className="rounded-lg bg-amber-400/10 px-2 py-1 text-xs text-amber-200"
                            >
                              {skill}
                            </span>

                          ),
                        )}

                    </div>

                  </div>


                  <div className="mt-6 space-y-2">

                    <button
                      onClick={() =>
                        void openWorkspace(
                          selected,
                        )
                      }
                      disabled={
                        workspaceLoading
                      }
                      className="w-full rounded-xl border border-cyan-300/20 bg-cyan-300/10 px-4 py-3 text-sm font-semibold text-cyan-200"
                    >
                      {workspaceLoading
                        ? "Loading Workspace..."
                        : "Open Opportunity Workspace"}
                    </button>


                    <button
                      onClick={() =>
                        void openPreparation()
                      }
                      disabled={
                        analysisLoading
                      }
                      className="neon-button w-full rounded-xl px-4 py-3 text-sm font-semibold"
                    >
                      Build Preparation Plan
                    </button>


                    <button
                      onClick={() =>
                        void openFuturePath()
                      }
                      disabled={
                        analysisLoading
                      }
                      className="w-full rounded-xl border border-violet-400/30 bg-violet-500/10 px-4 py-3 text-sm text-violet-200"
                    >
                      Show Future Path
                    </button>

                  </div>


                  {(whyNot?.blockers || []).length > 0 && (

                    <div className="mt-6 border-t border-white/8 pt-5">

                      <div className="text-xs uppercase tracking-wider text-zinc-500">
                        What is holding you back
                      </div>


                      <div className="mt-3 space-y-2">

                        {(whyNot?.blockers || [])
                          .slice(0, 4)
                          .map(
                            (
                              blocker,
                              index,
                            ) => (

                              <div
                                key={`${blocker}-${index}`}
                                className="text-sm text-zinc-400"
                              >
                                • {blocker}
                              </div>

                            ),
                          )}

                      </div>

                    </div>

                  )}

                </>

              ) : (

                <p className="mt-6 text-sm text-zinc-500">
                  Select an opportunity to analyse your fit.
                </p>

              )}

            </div>


            {/* HIDDEN SIGNALS */}

            {safeHidden.length > 0 && (

              <div className="glass rounded-2xl p-5">

                <div className="text-xs uppercase tracking-[0.18em] text-zinc-500">
                  Opportunity Signals
                </div>


                <div className="mt-4 space-y-3">

                  {safeHidden
                    .slice(0, 3)
                    .map(
                      (
                        item,
                        index,
                      ) => (

                        <div
                          key={`${item.type}-${index}`}
                          className="rounded-xl bg-white/[0.03] p-3"
                        >

                          <div className="text-xs text-cyan-200">
                            {item.type}
                          </div>

                          <div className="mt-1 text-xs leading-5 text-zinc-500">
                            {item.reason}
                          </div>

                        </div>

                      ),
                    )}

                </div>

              </div>

            )}

          </aside>

        </div>

      </section>


      {/* WORKSPACE */}

      {workspaceOpen && (

        <section className="mx-auto max-w-7xl px-5 pb-16 lg:px-8">

          <OpportunityWorkspace
            data={workspace}
            loading={workspaceLoading}
            onClose={() => {
              setWorkspaceOpen(false);
              setWorkspace(null);
            }}
          />

        </section>

      )}


      {/* PROFILE INTELLIGENCE */}

      <section className="mx-auto max-w-7xl px-5 pb-16 lg:px-8">

        <div className="grid gap-5 lg:grid-cols-3">

          <div className="glass rounded-2xl p-5 lg:col-span-2">

            <div className="flex items-center justify-between gap-4">

              <div>

                <p className="text-xs uppercase tracking-[0.18em] text-zinc-500">
                  Profile Intelligence
                </p>

                <h2 className="mt-2 text-xl font-semibold">
                  What your opportunity history is telling you
                </h2>

              </div>


              {profileIntel?.best_skill_investment && (

                <div className="rounded-xl bg-cyan-300/10 px-3 py-2 text-right">

                  <div className="text-[10px] uppercase tracking-wider text-zinc-500">
                    Best skill investment
                  </div>

                  <div className="text-sm font-semibold text-cyan-200">
                    {profileIntel.best_skill_investment.skill}
                  </div>

                </div>

              )}

            </div>


            <div className="mt-5 grid gap-4 sm:grid-cols-2">

              <div className="rounded-xl bg-white/[0.03] p-4">

                <div className="text-xs text-zinc-500">
                  Recurring profile weaknesses
                </div>


                <div className="mt-3 space-y-2">

                  {(profileIntel?.profile_weaknesses ||
                    [
                      "Run the engine to generate profile intelligence.",
                    ])
                    .slice(0, 4)
                    .map(
                      (
                        item,
                        index,
                      ) => (

                        <div
                          key={`${item}-${index}`}
                          className="text-sm text-zinc-300"
                        >
                          • {item}
                        </div>

                      ),
                    )}

                </div>

              </div>


              <div className="rounded-xl bg-white/[0.03] p-4">

                <div className="text-xs text-zinc-500">
                  Skill proof score
                </div>


                <div className="mt-3 space-y-2">

                  {(profileIntel?.skill_proof || [])
                    .slice(0, 4)
                    .map(
                      (item) => (

                        <div
                          key={item.skill}
                          className="flex items-center justify-between text-sm"
                        >

                          <span className="text-zinc-300">
                            {item.skill}
                          </span>

                          <span className="text-cyan-300">
                            {item.proof_score}%
                          </span>

                        </div>

                      ),
                    )}

                </div>

              </div>

            </div>


            {profileIntel?.direction_drift?.detected && (

              <div className="mt-4 rounded-xl border border-amber-400/20 bg-amber-400/[0.04] p-4">

                <div className="text-xs uppercase tracking-wider text-amber-200">
                  Career Direction Drift Detected
                </div>

                <p className="mt-2 text-sm text-zinc-300">
                  {profileIntel.direction_drift.message}
                </p>

                <p className="mt-2 text-xs text-zinc-500">
                  {profileIntel.direction_drift.action}
                </p>

              </div>

            )}

          </div>


          <div className="glass rounded-2xl p-5">

            <p className="text-xs uppercase tracking-[0.18em] text-zinc-500">
              Opportunity Timeline
            </p>

            <h2 className="mt-2 text-xl font-semibold">
              What to do next
            </h2>


            <div className="mt-5 space-y-3">

              {[
                [
                  "Apply now",
                  profileIntel?.timeline?.apply_now?.length || 0,
                ],
                [
                  "Prepare this week",
                  profileIntel?.timeline?.prepare_this_week?.length || 0,
                ],
                [
                  "Prepare this month",
                  profileIntel?.timeline?.prepare_this_month?.length || 0,
                ],
                [
                  "Future targets",
                  profileIntel?.timeline?.future_targets?.length || 0,
                ],
              ].map(
                ([label, value]) => (

                  <div
                    key={String(label)}
                    className="flex items-center justify-between rounded-xl bg-white/[0.03] p-3"
                  >

                    <span className="text-sm text-zinc-300">
                      {String(label)}
                    </span>

                    <span className="text-cyan-300">
                      {String(value)}
                    </span>

                  </div>

                ),
              )}

            </div>

          </div>

        </div>

      </section>


      {/* RESUME */}

      <section className="mx-auto max-w-7xl px-5 pb-10 lg:px-8">

        <div className="glass rounded-2xl p-5">

          <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">

            <div>

              <p className="text-xs uppercase tracking-[0.18em] text-zinc-500">
                Resume-to-Opportunity Matching
              </p>

              <h2 className="mt-2 text-xl font-semibold">
                Turn your resume into evidence
              </h2>

              <p className="mt-1 text-sm text-zinc-500">
                Upload a text-readable resume and the existing backend parser will extract skills, projects and experience signals.
              </p>

            </div>


            <label className="cursor-pointer rounded-xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-3 text-sm text-cyan-200">

              {resumeLoading
                ? "Analysing..."
                : "Upload Resume"}

              <input
                type="file"
                accept=".txt,.md"
                className="hidden"
                disabled={resumeLoading}
                onChange={(event) => {

                  const file =
                    event.target.files?.[0];

                  if (file) {
                    void handleResumeUpload(
                      file,
                    );
                  }

                }}
              />

            </label>

          </div>


          {resumeResult !== null && (

            <pre className="mt-4 max-h-48 overflow-auto rounded-xl bg-black/30 p-4 text-xs text-zinc-300">
              {JSON.stringify(
                resumeResult,
                null,
                2,
              )}
            </pre>

          )}

        </div>

      </section>


      {/* SIMULATOR + STRATEGY */}

      {selected && (

        <section className="mx-auto max-w-7xl px-5 pb-16 lg:px-8">

          <div className="grid gap-5 lg:grid-cols-2">

            {/* SIMULATOR */}

            <div className="glass rounded-2xl p-5">

              <p className="text-xs uppercase tracking-[0.18em] text-zinc-500">
                Opportunity Readiness Simulator
              </p>

              <h2 className="mt-2 text-xl font-semibold">
                What if you improve your profile?
              </h2>

              <p className="mt-2 text-sm text-zinc-500">
                Test skills before committing time to a preparation plan.
              </p>


              <input
                value={simulationSkills}
                onChange={(event) =>
                  setSimulationSkills(
                    event.target.value,
                  )
                }
                placeholder="Add skills, e.g. SQL, Docker"
                className="mt-4 w-full rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white outline-none"
              />


              <div className="mt-3 flex gap-3">

                <input
                  type="number"
                  min="0"
                  max="5"
                  value={simulationProjects}
                  onChange={(event) =>
                    setSimulationProjects(
                      Number(
                        event.target.value,
                      ) || 0,
                    )
                  }
                  className="w-28 rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white outline-none"
                />


                <button
                  onClick={() =>
                    void runSimulation()
                  }
                  disabled={analysisLoading}
                  className="neon-button flex-1 rounded-xl px-4 py-3 text-sm font-semibold"
                >
                  Simulate Improvement
                </button>

              </div>


              {simulation && (

                <div className="mt-5 grid grid-cols-2 gap-3">

                  <div className="rounded-xl bg-white/[0.03] p-4">

                    <div className="text-xs text-zinc-500">
                      Readiness
                    </div>

                    <div className="mt-1 text-2xl text-cyan-300">
                      {simulation.current_readiness}%
                      {" → "}
                      {simulation.simulated_readiness}%
                    </div>

                  </div>


                  <div className="rounded-xl bg-white/[0.03] p-4">

                    <div className="text-xs text-zinc-500">
                      New opportunities
                    </div>

                    <div className="mt-1 text-2xl text-violet-200">
                      +{simulation.unlocked_opportunities.length}
                    </div>

                  </div>

                </div>

              )}

            </div>


            {/* STRATEGY */}

            <div className="glass rounded-2xl p-5">

              <p className="text-xs uppercase tracking-[0.18em] text-zinc-500">
                Personal Application Strategy
              </p>

              <h2 className="mt-2 text-xl font-semibold">
                Prepare to apply intelligently
              </h2>


              <button
                onClick={() =>
                  void openApplicationStrategy()
                }
                disabled={strategyLoading}
                className="mt-4 w-full rounded-xl border border-violet-400/30 bg-violet-500/10 px-4 py-3 text-sm text-violet-200"
              >
                {strategyLoading
                  ? "Generating..."
                  : "Generate My Strategy"}
              </button>


              {strategy && (

                <div className="mt-5 space-y-4">

                  <div>

                    <div className="text-xs text-zinc-500">
                      Strongest selling points
                    </div>


                    <div className="mt-2 flex flex-wrap gap-2">

                      {strategy.strongest_selling_points.map(
                        (
                          item,
                          index,
                        ) => (

                          <span
                            key={`${item}-${index}`}
                            className="rounded-full bg-emerald-400/10 px-3 py-1 text-xs text-emerald-200"
                          >
                            {item}
                          </span>

                        ),
                      )}

                    </div>

                  </div>


                  <div>

                    <div className="text-xs text-zinc-500">
                      Improve before applying
                    </div>


                    <div className="mt-2 space-y-2">

                      {strategy.improvements_before_applying.map(
                        (
                          item,
                          index,
                        ) => (

                          <div
                            key={`${item}-${index}`}
                            className="text-sm text-zinc-300"
                          >
                            • {item}
                          </div>

                        ),
                      )}

                    </div>

                  </div>

                </div>

              )}

            </div>

          </div>

        </section>

      )}


      {/* PROFILE MODAL */}

      <ProfileModal
        open={profileOpen}
        profile={profile}
        saving={false}
        onClose={() =>
          setProfileOpen(false)
        }
        onSave={async (
          updatedProfile,
        ) => {

          try {

            const saved =
              await saveStudentProfile(
                updatedProfile,
              );


            setProfile(
              saved,
            );


            setProfileOpen(
              false,
            );


            setStatus(
              "Profile updated successfully.",
            );

          } catch (error) {

            console.error(
              error,
            );

            setStatus(
              "Could not save the updated profile.",
            );

          }

        }}
      />

    </main>
  );
}


export default App;