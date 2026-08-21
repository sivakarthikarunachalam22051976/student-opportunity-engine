import {
  ArrowUpRight,
  Building2,
  MapPin,
  Sparkles,
} from "lucide-react";

import type {
  Opportunity,
} from "../types";


type OpportunityCardProps = {
  opportunity: Opportunity;

  selected: boolean;

  onSelect: (
    opportunity: Opportunity
  ) => void;

  onClaim: (
    opportunity: Opportunity
  ) => void;
};


export default function OpportunityCard({
  opportunity,
  selected,
  onSelect,
  onClaim,
}: OpportunityCardProps) {

  const organization =
    opportunity.organization ||
    opportunity.company ||
    "Organization not specified";


  const deadline =
    opportunity.deadline ||
    "Deadline not specified";


  const stipendText = opportunity.stipend !== undefined && opportunity.stipend !== null 
    ? String(opportunity.stipend) 
    : "";

  const isFunded =
    /funded/i.test(stipendText) ||
    /fully funded/i.test(
      opportunity.description || ""
    );


  return (
    <article
      onClick={() =>
        onSelect(opportunity)
      }

      className={`glass glass-hover flex min-h-[300px] cursor-pointer flex-col rounded-2xl p-5 ${
        selected
          ? "border-cyan-300/45"
          : ""
      }`}
    >

      <div className="flex items-start justify-between gap-4">

        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-white/10 bg-white/[0.04]">

          <Building2
            size={19}
            className="text-[#00f0ff]"
          />

        </div>


        <div className="flex flex-wrap justify-end gap-2">

          <span className="rounded-full border border-violet-400/20 bg-violet-500/10 px-2.5 py-1 text-[10px] font-medium text-violet-200">

            {deadline}

          </span>


          {isFunded && (

            <span className="rounded-full border border-cyan-300/20 bg-cyan-400/10 px-2.5 py-1 text-[10px] font-medium text-cyan-200">

              Fully Funded

            </span>

          )}

        </div>

      </div>


      <div className="mt-6">

        <p className="text-xs uppercase tracking-[0.14em] text-zinc-500">

          {organization}

        </p>


        <h3 className="mt-2 line-clamp-2 text-lg font-semibold leading-6 text-white">

          {opportunity.title}

        </h3>


        <p className="mt-3 line-clamp-2 text-sm leading-6 text-zinc-400">

          {opportunity.description ||
            "Explore eligibility, requirements and application details for this opportunity."
          }

        </p>

      </div>


      <div className="mt-5 flex flex-wrap gap-2">

        {opportunity.skills
          ?.slice(0, 3)
          .map((skill) => (

            <span
              key={skill}

              className="rounded-lg border border-white/7 bg-white/[0.025] px-2.5 py-1 text-xs text-zinc-400"
            >

              {skill}

            </span>

          ))}

      </div>


      <div className="mt-auto flex items-center justify-between gap-3 pt-7">

        <div className="space-y-1 text-xs text-zinc-500">

          {opportunity.location && (

            <div className="flex items-center gap-1.5">

              <MapPin size={13} />

              {opportunity.location}

            </div>

          )}


          {stipendText && (

            <div className="flex items-center gap-1.5">

              <Sparkles size={13} />

              {stipendText}

            </div>

          )}

        </div>


        <button
          onClick={(event) => {

            event.stopPropagation();

            onClaim(opportunity);
          }}

          className="flex items-center gap-2 rounded-xl border border-cyan-300/20 bg-cyan-400/10 px-4 py-2.5 text-xs font-semibold text-cyan-100 transition hover:border-cyan-300/45 hover:bg-cyan-400/15"
        >

          Claim Spot

          <ArrowUpRight size={15} />

        </button>

      </div>

    </article>
  );
}