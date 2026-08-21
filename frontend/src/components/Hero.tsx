import type { ChangeEvent } from "react";

type HeroProps = {
  searchTerm: string;
  activeFilter: string;
  loading: boolean;
  onSearchChange: (value: string) => void;
  onFilterChange: (value: string) => void;
  onLaunch: () => void;
};

// 🎯 FIXED ONCE AND FOR ALL: This is the actual default export React component your page needs!
export default function Hero({
  searchTerm,
  activeFilter,
  loading,
  onSearchChange,
  onFilterChange,
  onLaunch,
}: HeroProps) {
  
  const filters = ["All", "Internship", "Hackathon", "Job", "Scholarship", "Competition"];

  return (
    <section className="relative overflow-hidden bg-[#0a0a0c] py-20 px-5 text-center border-b border-white/5">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(6,182,212,0.05)_0,transparent_70%)]" />
      
      <div className="relative mx-auto max-w-3xl">
        <span className="inline-flex items-center gap-1.5 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-xs font-medium text-cyan-300">
          ✨ Dual Ingestion Engine Active
        </span>
        
        <h1 className="mt-6 text-4xl font-extrabold tracking-tight text-white sm:text-5xl">
          Scout Your Next <span className="bg-gradient-to-r from-cyan-400 to-violet-400 bg-clip-text text-transparent">Opportunity</span> Live
        </h1>
        
        <p className="mt-4 text-base text-zinc-400 max-w-xl mx-auto">
          Enter custom search terms or update your profile to hunt down live, verified positions across global developer registries instantly.
        </p>

        {/* Input Text Bar Field Container */}
        <div className="mt-10 flex flex-col gap-3 sm:flex-row justify-center max-w-2xl mx-auto">
          <input
            type="text"
            value={searchTerm}
            onChange={(e: ChangeEvent<HTMLInputElement>) => onSearchChange(e.target.value)}
            placeholder="Search keywords (e.g. Frontend, Data Science, Remote...)"
            className="w-full rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white placeholder-zinc-500 outline-none transition focus:border-cyan-400/50 focus:bg-white/[0.06]"
          />
          
          <button
            onClick={onLaunch}
            disabled={loading}
            className="shrink-0 rounded-xl bg-gradient-to-r from-cyan-500 to-violet-500 px-6 py-3 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-50"
          >
            {loading ? "Scanning Web..." : "Launch Live Engine"}
          </button>
        </div>

        {/* Dynamic Category Navigation Option Tabs */}
        <div className="mt-8 flex flex-wrap justify-center gap-2">
          {filters.map((filter) => (
            <button
              key={filter}
              onClick={() => onFilterChange(filter)}
              className={`rounded-lg border px-3.5 py-1.5 text-xs font-medium transition ${
                activeFilter === filter
                  ? "border-cyan-400 bg-cyan-400/10 text-cyan-300"
                  : "border-white/5 bg-white/[0.02] text-zinc-400 hover:border-white/10 hover:bg-white/[0.04]"
              }`}
            >
              {filter}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
