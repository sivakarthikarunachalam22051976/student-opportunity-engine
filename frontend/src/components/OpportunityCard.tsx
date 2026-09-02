import {
  ArrowUpRight,
  Building2,
  Clock3,
  MapPin,
  ShieldCheck,
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
    "Deadline unknown";

  const stipendText =
    opportunity.stipend !== undefined &&
    opportunity.stipend !== null
      ? String(
          opportunity.stipend
        )
      : "";

  const match =
    Math.round(
      opportunity.match_score || 0
    );

  const trust =
    Math.round(
      opportunity.trust_score || 0
    );

  const urgency =
    opportunity
      .deadline_intelligence
      ?.urgency;

  const isFunded =
    /funded/i.test(
      stipendText
    ) ||
    /fully funded/i.test(
      opportunity.description ||
      ""
    );

  const applicationUrl =
    opportunity.application_url ||
    opportunity.source_url;


  return (
    <article
      onClick={() =>
        onSelect(opportunity)
      }
      className={`
        glass
        glass-hover
        group
        flex
        min-h-[330px]
        cursor-pointer
        flex-col
        rounded-2xl
        p-5
        transition
        ${
          selected
            ? "border-cyan-300/45 shadow-[0_0_35px_rgba(0,240,255,0.08)]"
            : ""
        }
      `}
    >

      <div
        className="
          flex
          items-start
          justify-between
          gap-4
        "
      >

        <div
          className="
            flex
            h-11
            w-11
            shrink-0
            items-center
            justify-center
            rounded-xl
            border border-white/10
            bg-white/[0.04]
          "
        >
          <Building2
            size={19}
            className="text-cyan-300"
          />
        </div>


        <div
          className="
            flex
            flex-wrap
            justify-end
            gap-2
          "
        >

          <span
            className="
              rounded-full
              border border-violet-400/20
              bg-violet-500/10
              px-2.5 py-1
              text-[10px]
              text-violet-200
            "
          >
            {deadline}
          </span>

          {isFunded && (
            <span
              className="
                rounded-full
                border border-cyan-300/20
                bg-cyan-400/10
                px-2.5 py-1
                text-[10px]
                text-cyan-200
              "
            >
              Fully Funded
            </span>
          )}

        </div>

      </div>


      <div className="mt-6">

        <p
          className="
            text-xs
            uppercase
            tracking-[0.14em]
            text-zinc-500
          "
        >
          {organization}
        </p>

        <h3
          className="
            mt-2
            line-clamp-2
            text-lg
            font-semibold
            leading-6
            text-white
          "
        >
          {opportunity.title}
        </h3>

        <p
          className="
            mt-3
            line-clamp-2
            text-sm
            leading-6
            text-zinc-400
          "
        >
          {opportunity.description ||
            "Explore eligibility, requirements and application details."}
        </p>

      </div>


      <div
        className="
          mt-5
          flex
          flex-wrap
          gap-2
        "
      >

        {(
          opportunity.skills || []
        )
          .slice(0, 4)
          .map(skill => (
            <span
              key={skill}
              className="
                rounded-lg
                border border-white/7
                bg-white/[0.025]
                px-2.5 py-1
                text-xs
                text-zinc-400
              "
            >
              {skill}
            </span>
          ))}

      </div>


      <div
        className="
          mt-auto
          pt-6
        "
      >

        <div
          className="
            grid
            grid-cols-3
            gap-2
          "
        >

          <MiniMetric
            label="Match"
            value={`${match}%`}
          />

          <MiniMetric
            label="Trust"
            value={
              trust
                ? `${trust}%`
                : "—"
            }
          />

          <MiniMetric
            label="Urgency"
            value={
              urgency || "—"
            }
          />

        </div>


        <div
          className="
            mt-4
            flex
            items-center
            justify-between
            gap-3
          "
        >

          <div
            className="
              space-y-1
              text-xs
              text-zinc-500
            "
          >

            {opportunity.location && (
              <div
                className="
                  flex
                  items-center
                  gap-1.5
                "
              >
                <MapPin size={13} />
                {opportunity.location}
              </div>
            )}

            {stipendText && (
              <div
                className="
                  flex
                  items-center
                  gap-1.5
                "
              >
                <Sparkles size={13} />
                {stipendText}
              </div>
            )}

          </div>


          <button
            disabled={!applicationUrl}
            onClick={event => {
              event.stopPropagation();
              onClaim(
                opportunity
              );
            }}
            className="
              flex
              items-center
              gap-2
              rounded-xl
              border border-cyan-300/20
              bg-cyan-400/10
              px-4 py-2.5
              text-xs
              font-semibold
              text-cyan-100
              transition
              hover:border-cyan-300/45
              hover:bg-cyan-400/15
              disabled:cursor-not-allowed
              disabled:opacity-40
            "
          >
            Claim Spot
            <ArrowUpRight size={15} />
          </button>

        </div>

      </div>

    </article>
  );
}


function MiniMetric({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div
      className="
        rounded-xl
        border border-white/7
        bg-black/20
        px-3 py-2
      "
    >

      <p
        className="
          text-[9px]
          uppercase
          tracking-wider
          text-zinc-700
        "
      >
        {label}
      </p>

      <div
        className="
          mt-1
          flex
          items-center
          gap-1.5
          text-xs
          font-medium
          text-zinc-300
        "
      >

        {label === "Trust" && (
          <ShieldCheck
            size={12}
            className="text-cyan-300"
          />
        )}

        {label === "Urgency" && (
          <Clock3
            size={12}
            className="text-violet-300"
          />
        )}

        {value}

      </div>

    </div>
  );
}