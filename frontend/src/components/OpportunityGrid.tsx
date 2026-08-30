import type {
  Opportunity,
} from "../types";

import OpportunityCard from "./OpportunityCard";

type OpportunityGridProps = {
  opportunities: Opportunity[];

  selectedOpportunity?: Opportunity;

  loading: boolean;

  onSelect: (
    opportunity: Opportunity
  ) => void;

  onClaim: (
    opportunity: Opportunity
  ) => void;
};

export default function OpportunityGrid({
  opportunities,
  selectedOpportunity,
  loading,
  onSelect,
  onClaim,
}: OpportunityGridProps) {
  if (loading) {
    return (
      <div className="grid gap-5 sm:grid-cols-2">
        {[1, 2, 3, 4].map((item) => (
          <div
            key={item}
            className="glass h-[300px] animate-pulse rounded-2xl"
          />
        ))}
      </div>
    );
  }

  if (!opportunities.length) {
    return (
      <div className="glass flex min-h-[300px] flex-col items-center justify-center rounded-2xl px-6 text-center">
        <p className="text-lg font-semibold text-white">
          No opportunities found
        </p>

        <p className="mt-2 max-w-md text-sm text-zinc-500">
          Launch the engine to search for opportunities
          matched to the current student profile.
        </p>
      </div>
    );
  }

  return (
    <div className="grid gap-5 sm:grid-cols-2">
      {opportunities.map((opportunity) => (
        <OpportunityCard
          key={String(opportunity.id)}
          opportunity={opportunity}
          selected={
            selectedOpportunity?.id ===
            opportunity.id
          }
          onSelect={onSelect}
          onClaim={onClaim}
        />
      ))}
    </div>
  );
}