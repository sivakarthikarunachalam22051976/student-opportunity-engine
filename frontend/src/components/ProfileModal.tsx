import {
  useEffect,
  useState,
} from "react";

import {
  Check,
  X,
} from "lucide-react";

import type {
  OpportunityType,
  StudentProfile,
} from "../types";


type ProfileModalProps = {
  open: boolean;
  profile: StudentProfile;
  saving?: boolean;
  onClose: () => void;
  onSave: (
    profile: StudentProfile
  ) => Promise<void> | void;
};


const opportunityTypes: OpportunityType[] = [
  "internship",
  "hackathon",
  "job",
  "scholarship",
  "competition",
];


export default function ProfileModal({
  open,
  profile,
  saving = false,
  onClose,
  onSave,
}: ProfileModalProps) {

  const [
    formData,
    setFormData,
  ] = useState<StudentProfile>(profile);


  useEffect(() => {
    if (open) {
      setFormData({
        ...profile,
        interests: [
          ...(profile.interests || []),
        ],
        skills: [
          ...(profile.skills || []),
        ],
        projects: [
          ...(profile.projects || []),
        ],
        evidence: [
          ...(profile.evidence || []),
        ],
      });
    }
  }, [open, profile]);


  if (!open) {
    return null;
  }


  function updateList(
    field:
      | "skills"
      | "interests"
      | "projects"
      | "evidence",
    value: string,
  ) {

    setFormData(
      current => ({
        ...current,
        [field]:
          value
            .split(",")
            .map(
              item =>
                item.trim()
            )
            .filter(Boolean),
      })
    );
  }


  return (
    <div
      className="
        fixed inset-0 z-[100]
        flex items-center justify-center
        bg-black/75 p-4
        backdrop-blur-md
      "
      onMouseDown={(event) => {
        if (
          event.target ===
          event.currentTarget
        ) {
          onClose();
        }
      }}
    >

      <div
        className="
          glass w-full max-w-3xl
          max-h-[92vh]
          overflow-hidden
          rounded-3xl
          shadow-2xl
        "
      >

        {/* HEADER */}

        <div
          className="
            flex items-center justify-between
            border-b border-white/8
            px-6 py-5
          "
        >

          <div>

            <p
              className="
                text-[10px]
                uppercase
                tracking-[0.2em]
                text-cyan-300
              "
            >
              Profile Intelligence
            </p>

            <h2
              className="
                mt-1
                text-xl
                font-semibold
                text-white
              "
            >
              Edit Student Profile
            </h2>

            <p
              className="
                mt-1
                text-xs
                text-zinc-500
              "
            >
              Your profile controls discovery,
              matching and preparation analysis.
            </p>

          </div>


          <button
            type="button"
            onClick={onClose}
            disabled={saving}
            className="
              rounded-xl
              border border-white/10
              p-2
              text-zinc-500
              transition
              hover:border-white/20
              hover:text-white
            "
          >
            <X size={18} />
          </button>

        </div>


        {/* SCROLLABLE BODY */}

        <div
          className="
            max-h-[calc(92vh-145px)]
            overflow-y-auto
            px-6 py-6
          "
        >

          <div
            className="
              grid gap-5
              sm:grid-cols-2
            "
          >

            <Field
              label="Name"
              value={formData.name}
              onChange={(value) =>
                setFormData(
                  current => ({
                    ...current,
                    name: value,
                  })
                )
              }
            />


            <div>

              <label
                className="
                  text-sm
                  text-zinc-400
                "
              >
                Year
              </label>

              <select
                value={formData.year}
                onChange={(event) =>
                  setFormData(
                    current => ({
                      ...current,
                      year: Number(
                        event.target.value
                      ),
                    })
                  )
                }
                className="
                  mt-2
                  w-full
                  rounded-xl
                  border border-white/10
                  bg-[#101015]
                  px-4 py-3
                  text-white
                  outline-none
                  focus:border-cyan-300/50
                "
              >

                {[1, 2, 3, 4, 5, 6].map(
                  year => (
                    <option
                      key={year}
                      value={year}
                    >
                      Year {year}
                    </option>
                  )
                )}

              </select>

            </div>


            <Field
              label="Branch"
              value={formData.branch}
              onChange={(value) =>
                setFormData(
                  current => ({
                    ...current,
                    branch: value,
                  })
                )
              }
            />


            <Field
              label="Location"
              value={formData.location}
              onChange={(value) =>
                setFormData(
                  current => ({
                    ...current,
                    location: value,
                  })
                )
              }
            />


            <div
              className="
                sm:col-span-2
              "
            >

              <label
                className="
                  text-sm
                  text-zinc-400
                "
              >
                Opportunity Type
              </label>

              <select
                value={
                  formData.opportunity_type
                }
                onChange={(event) =>
                  setFormData((current: StudentProfile): StudentProfile => ({
                    ...current,
                    opportunity_type: event.target.value as OpportunityType,
                    }))
                    }
                className="
                  mt-2
                  w-full
                  rounded-xl
                  border border-white/10
                  bg-[#101015]
                  px-4 py-3
                  text-white
                  outline-none
                  focus:border-cyan-300/50
                "
              >

                {opportunityTypes.map(
                  type => (
                    <option
                      key={type}
                      value={type}
                    >
                      {type
                        .charAt(0)
                        .toUpperCase()
                        +
                        type.slice(1)}
                    </option>
                  )
                )}

              </select>

            </div>


            <ListField
              label="Skills"
              value={
                formData.skills.join(", ")
              }
              placeholder="Python, React, SQL, FastAPI"
              onChange={(value) =>
                updateList(
                  "skills",
                  value
                )
              }
            />


            <ListField
              label="Interests"
              value={
                formData.interests.join(", ")
              }
              placeholder="AI, Web Development, Data Science"
              onChange={(value) =>
                updateList(
                  "interests",
                  value
                )
              }
            />


            <ListField
              label="Projects"
              value={
                (
                  formData.projects || []
                ).join(", ")
              }
              placeholder="Project 1, Project 2"
              onChange={(value) =>
                updateList(
                  "projects",
                  value
                )
              }
            />


            <ListField
              label="Evidence / Proof"
              value={
                (
                  formData.evidence || []
                ).join(", ")
              }
              placeholder="GitHub, portfolio, certifications"
              onChange={(value) =>
                updateList(
                  "evidence",
                  value
                )
              }
            />

          </div>


          <div
            className="
              mt-6
              rounded-2xl
              border border-cyan-300/10
              bg-cyan-300/[0.03]
              p-4
            "
          >

            <p
              className="
                text-xs
                font-medium
                text-cyan-200
              "
            >
              How this improves your results
            </p>

            <p
              className="
                mt-2
                text-xs
                leading-5
                text-zinc-500
              "
            >
              Skills influence matching,
              interests influence relevance,
              projects strengthen portfolio analysis,
              and evidence helps determine how ready
              you are to apply.
            </p>

          </div>

        </div>


        {/* FOOTER */}

        <div
          className="
            flex items-center
            justify-between
            border-t border-white/8
            px-6 py-4
          "
        >

          <p
            className="
              hidden
              text-xs
              text-zinc-600
              sm:block
            "
          >
            Changes are applied after saving.
          </p>

          <div
            className="
              flex
              gap-3
            "
          >

            <button
              type="button"
              onClick={onClose}
              disabled={saving}
              className="
                rounded-xl
                border border-white/10
                px-5 py-3
                text-sm
                text-zinc-400
                hover:text-white
              "
            >
              Cancel
            </button>


            <button
              type="button"
              disabled={saving}
              onClick={() =>
                onSave(formData)
              }
              className="
                neon-button
                flex items-center
                gap-2
                rounded-xl
                px-5 py-3
                text-sm
                font-semibold
                disabled:cursor-not-allowed
                disabled:opacity-60
              "
            >

              <Check size={16} />

              {saving
                ? "Saving..."
                : "Save Profile"}

            </button>

          </div>

        </div>

      </div>

    </div>
  );
}


function Field({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (
    value: string
  ) => void;
}) {
  return (
    <label
      className="
        block
        text-sm
        text-zinc-400
      "
    >

      {label}

      <input
        value={value}
        onChange={(event) =>
          onChange(
            event.target.value
          )
        }
        className="
          mt-2
          w-full
          rounded-xl
          border border-white/10
          bg-white/[0.03]
          px-4 py-3
          text-white
          outline-none
          focus:border-cyan-300/50
        "
      />

    </label>
  );
}


function ListField({
  label,
  value,
  placeholder,
  onChange,
}: {
  label: string;
  value: string;
  placeholder: string;
  onChange: (
    value: string
  ) => void;
}) {
  return (
    <label
      className="
        block
        text-sm
        text-zinc-400
        sm:col-span-2
      "
    >

      {label}

      <textarea
        value={value}
        placeholder={placeholder}
        onChange={(event) =>
          onChange(
            event.target.value
          )
        }
        className="
          mt-2
          min-h-24
          w-full
          resize-y
          rounded-xl
          border border-white/10
          bg-white/[0.03]
          px-4 py-3
          text-sm
          leading-6
          text-white
          outline-none
          placeholder:text-zinc-700
          focus:border-cyan-300/50
        "
      />

      <p
        className="
          mt-1
          text-[10px]
          text-zinc-700
        "
      >
        Separate multiple entries with commas.
      </p>

    </label>
  );
}