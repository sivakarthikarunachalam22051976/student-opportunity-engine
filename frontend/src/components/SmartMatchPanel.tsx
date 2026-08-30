
import { Sparkles, Target, BrainCircuit, ArrowRight } from "lucide-react";

type SmartMatchPanelProps = {
  match: any;
  loading?: boolean;
  // 🚀 RE-ADDED: Define the preparation handler inside the panel type matrix
  onPrepare: () => void;
};

export default function SmartMatchPanel({
  match,
  loading = false,
  // 🚀 RE-ADDED: Destructure the action parameter here
  onPrepare,
}: SmartMatchPanelProps) {
  if (loading) {
    return (
      <div className="glass-card rounded-3xl p-6">
        <p className="text-gray-400">
          Calculating your smart match...
        </p>
      </div>
    );
  }

  const score =
    match?.match_score ??
    match?.score ??
    match?.percentage ??
    0;

  const matchedSkills =
    match?.matched_skills ??
    match?.matching_skills ??
    [];

  const missingSkills =
    match?.missing_skills ??
    match?.skill_gaps ??
    [];

  return (
    <aside className="glass-card rounded-3xl p-6 lg:sticky lg:top-24 flex flex-col justify-between min-h-[480px]">
      <div>
        <div className="mb-6 flex items-center gap-3">
          <div className="rounded-xl border border-cyan-400/20 bg-cyan-400/10 p-3">
            <BrainCircuit className="text-cyan-400" size={24} />
          </div>

          <div>
            <h2 className="font-semibold text-white">
              Smart Match
            </h2>
            <p className="text-sm text-gray-500">
              Based on your profile
            </p>
          </div>
        </div>

        <div className="mb-6 flex justify-center">
          <div className="relative flex h-36 w-36 items-center justify-center rounded-full border-4 border-cyan-400/30">
            <div className="text-center">
              <div className="text-4xl font-bold text-cyan-400">
                {Math.round(score)}%
              </div>
              <div className="mt-1 text-xs text-gray-500">
                Match Score
              </div>
            </div>
          </div>
        </div>

        <div className="mb-6">
          <div className="mb-3 flex items-center gap-2">
            <Target size={17} className="text-cyan-400" />
            <h3 className="text-sm font-semibold text-white">
              Matching Skills
            </h3>
          </div>

          <div className="flex flex-wrap gap-2">
            {matchedSkills.length > 0 ? (
              matchedSkills.map((skill: string) => (
                <span
                  key={skill}
                  className="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-xs text-cyan-300"
                >
                  {skill}
                </span>
              ))
            ) : (
              <span className="text-sm text-gray-500">
                Add your skills to see matches.
              </span>
            )}
          </div>
        </div>

        <div className="mb-6">
          <div className="mb-3 flex items-center gap-2">
            <Sparkles size={17} className="text-violet-400" />
            <h3 className="text-sm font-semibold text-white">
              Growth Areas
            </h3>
          </div>

          <div className="flex flex-wrap gap-2">
            {missingSkills.length > 0 ? (
              missingSkills.map((skill: string) => (
                <span
                  key={skill}
                  className="rounded-full border border-violet-400/20 bg-violet-400/10 px-3 py-1 text-xs text-violet-300"
                >
                  {skill}
                </span>
              ))
            ) : (
              <span className="text-sm text-gray-500">
                No major skill gaps detected.
              </span>
            )}
          </div>
        </div>
      </div>

      {/* 🚀 RE-ADDED BUTTON: Custom styled Action Panel for generating live roadmap analytics */}
      <button
        onClick={onPrepare}
        className="w-full mt-4 flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-violet-500 py-3 text-xs font-semibold text-white transition hover:opacity-90 active:scale-[0.98]"
      >
        Help Me Prepare
        <ArrowRight size={14} />
      </button>
    </aside>
  );
}
