import { useEffect, useState } from "react";
import { X, Save, UserRound } from "lucide-react";

import type { StudentProfile } from "../types";

type ProfileModalProps = {
  open: boolean;
  profile: StudentProfile;
  saving?: boolean;
  onClose: () => void;
  onSave: (profile: StudentProfile) => Promise<void> | void;
};

export default function ProfileModal({
  open,
  profile,
  saving = false,
  onClose,
  onSave,
}: ProfileModalProps) {
  const [formData, setFormData] =
    useState<StudentProfile>(profile);

  useEffect(() => {
    if (open) {
      setFormData(profile);
    }
  }, [open, profile]);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (
        event.key === "Escape" &&
        open &&
        !saving
      ) {
        onClose();
      }
    }

    window.addEventListener(
      "keydown",
      handleKeyDown
    );

    return () => {
      window.removeEventListener(
        "keydown",
        handleKeyDown
      );
    };
  }, [open, saving, onClose]);

  if (!open) {
    return null;
  }

  function updateField(
    field: keyof StudentProfile,
    value: string
  ) {
    if (
      field === "skills" ||
      field === "interests"
    ) {
      setFormData((current) => ({
        ...current,
        [field]: value
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean),
      }));

      return;
    }

    if (field === "year") {
      setFormData((current) => ({
        ...current,
        year: Math.max(
          1,
          Math.min(
            6,
            Number(value) || 1
          )
        ),
      }));

      return;
    }

    setFormData((current) => ({
      ...current,
      [field]: value,
    }));
  }

  function updateArrayField(
    field: "projects" | "evidence",
    value: string
  ) {
    setFormData((current) => ({
      ...current,
      [field]: value
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
    }));
  }

  async function handleSave() {
    await onSave(formData);
  }

  function handleBackdropClick() {
    if (!saving) {
      onClose();
    }
  }

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/75 p-3 backdrop-blur-md sm:p-5"
      onMouseDown={handleBackdropClick}
    >
      <div
        className="glass flex max-h-[92vh] w-full max-w-2xl flex-col overflow-hidden rounded-3xl border border-white/10 shadow-2xl"
        onMouseDown={(event) =>
          event.stopPropagation()
        }
      >
        {/* HEADER */}
        <div className="flex shrink-0 items-start justify-between gap-4 border-b border-white/10 p-5 sm:p-6">
          <div className="flex items-start gap-3">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-cyan-400/20 bg-cyan-400/10">
              <UserRound
                size={20}
                className="text-cyan-300"
              />
            </div>

            <div>
              <p className="text-[10px] font-medium uppercase tracking-[0.18em] text-zinc-500">
                Student Profile
              </p>

              <h2 className="mt-1 text-xl font-semibold text-white sm:text-2xl">
                Personalize your engine
              </h2>

              <p className="mt-1 text-xs leading-5 text-zinc-500">
                Your profile controls how opportunities
                are matched and ranked.
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            disabled={saving}
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-white/10 text-zinc-400 transition hover:border-white/20 hover:bg-white/[0.05] hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
            aria-label="Close profile editor"
          >
            <X size={18} />
          </button>
        </div>

        {/* SCROLLABLE FORM AREA */}
        <div className="min-h-0 flex-1 overflow-y-auto px-5 py-5 sm:px-6 sm:py-6">
          <div className="grid gap-5 sm:grid-cols-2">
            <label className="text-sm text-zinc-400">
              Name

              <input
                className="mt-2 w-full rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-white outline-none transition placeholder:text-zinc-600 focus:border-cyan-400/40 focus:bg-white/[0.06]"
                value={formData.name}
                onChange={(event) =>
                  updateField(
                    "name",
                    event.target.value
                  )
                }
                placeholder="Your name"
              />
            </label>

            <label className="text-sm text-zinc-400">
              Year

              <input
                type="number"
                min="1"
                max="6"
                className="mt-2 w-full rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-white outline-none transition focus:border-cyan-400/40 focus:bg-white/[0.06]"
                value={formData.year}
                onChange={(event) =>
                  updateField(
                    "year",
                    event.target.value
                  )
                }
              />
            </label>

            <label className="text-sm text-zinc-400">
              Branch

              <input
                className="mt-2 w-full rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-white outline-none transition placeholder:text-zinc-600 focus:border-cyan-400/40 focus:bg-white/[0.06]"
                value={formData.branch}
                onChange={(event) =>
                  updateField(
                    "branch",
                    event.target.value
                  )
                }
                placeholder="Computer Science"
              />
            </label>

            <label className="text-sm text-zinc-400">
              Location

              <input
                className="mt-2 w-full rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-white outline-none transition placeholder:text-zinc-600 focus:border-cyan-400/40 focus:bg-white/[0.06]"
                value={formData.location}
                onChange={(event) =>
                  updateField(
                    "location",
                    event.target.value
                  )
                }
                placeholder="Bengaluru, India"
              />
            </label>

            <label className="text-sm text-zinc-400 sm:col-span-2">
              Opportunity Type

              <select
                className="mt-2 w-full rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-white outline-none transition focus:border-cyan-400/40 focus:bg-white/[0.06]"
                value={
                  formData.opportunity_type
                }
                onChange={(event) =>
                  updateField(
                    "opportunity_type",
                    event.target.value
                  )
                }
              >
                {[
                  "internship",
                  "hackathon",
                  "job",
                  "scholarship",
                  "competition",
                ].map((type) => (
                  <option
                    key={type}
                    value={type}
                    className="bg-[#111114]"
                  >
                    {type[0].toUpperCase() +
                      type.slice(1)}
                  </option>
                ))}
              </select>

              <p className="mt-2 text-xs text-zinc-600">
                Choose the opportunity category you
                want the engine to prioritize.
              </p>
            </label>

            <label className="text-sm text-zinc-400 sm:col-span-2">
              Interests

              <textarea
                className="mt-2 min-h-[88px] w-full resize-y rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-white outline-none transition placeholder:text-zinc-600 focus:border-cyan-400/40 focus:bg-white/[0.06]"
                value={
                  formData.interests.join(", ")
                }
                onChange={(event) =>
                  updateField(
                    "interests",
                    event.target.value
                  )
                }
                placeholder="AI, Machine Learning, Web Development"
              />

              <p className="mt-2 text-xs text-zinc-600">
                Separate interests with commas.
              </p>
            </label>

            <label className="text-sm text-zinc-400 sm:col-span-2">
              Skills

              <textarea
                className="mt-2 min-h-[88px] w-full resize-y rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-white outline-none transition placeholder:text-zinc-600 focus:border-cyan-400/40 focus:bg-white/[0.06]"
                value={
                  formData.skills.join(", ")
                }
                onChange={(event) =>
                  updateField(
                    "skills",
                    event.target.value
                  )
                }
                placeholder="Python, React, SQL, FastAPI"
              />

              <p className="mt-2 text-xs text-zinc-600">
                Separate skills with commas.
              </p>
            </label>

            <label className="text-sm text-zinc-400 sm:col-span-2">
              Projects

              <textarea
                className="mt-2 min-h-[88px] w-full resize-y rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-white outline-none transition placeholder:text-zinc-600 focus:border-cyan-400/40 focus:bg-white/[0.06]"
                value={
                  (
                    formData.projects || []
                  ).join(", ")
                }
                onChange={(event) =>
                  updateArrayField(
                    "projects",
                    event.target.value
                  )
                }
                placeholder="Student Opportunity Engine, AI Resume Analyzer"
              />

              <p className="mt-2 text-xs text-zinc-600">
                Add projects that demonstrate your
                experience.
              </p>
            </label>

            <label className="text-sm text-zinc-400 sm:col-span-2">
              Evidence Links / Proof

              <textarea
                className="mt-2 min-h-[88px] w-full resize-y rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-white outline-none transition placeholder:text-zinc-600 focus:border-cyan-400/40 focus:bg-white/[0.06]"
                value={
                  (
                    formData.evidence || []
                  ).join(", ")
                }
                onChange={(event) =>
                  updateArrayField(
                    "evidence",
                    event.target.value
                  )
                }
                placeholder="GitHub profile, LinkedIn profile, project portfolio"
              />

              <p className="mt-2 text-xs text-zinc-600">
                Add portfolio, GitHub, LinkedIn or
                project links separated by commas.
              </p>
            </label>
          </div>
        </div>

        {/* FIXED FOOTER */}
        <div className="flex shrink-0 flex-col-reverse gap-3 border-t border-white/10 bg-black/20 p-5 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <p className="text-xs text-zinc-600">
            Changes update your opportunity matching.
          </p>

          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={onClose}
              disabled={saving}
              className="rounded-xl px-4 py-3 text-sm font-medium text-zinc-400 transition hover:bg-white/[0.04] hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
            >
              Cancel
            </button>

            <button
              type="button"
              disabled={saving}
              onClick={handleSave}
              className="neon-button flex items-center justify-center gap-2 rounded-xl px-5 py-3 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60"
            >
              <Save size={16} />

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