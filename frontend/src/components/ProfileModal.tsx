import {
  useEffect,
  useState,
} from "react";

import type {
  StudentProfile,
} from "../types";

interface ProfileModalProps {
  open: boolean;
  profile: StudentProfile;
  saving: boolean;
  onClose: () => void;
  onSave: (
    profile: StudentProfile
  ) => void | Promise<void>;
}

function ProfileModal({
  open,
  profile,
  saving,
  onClose,
  onSave,
}: ProfileModalProps) {

  const [
    formData,
    setFormData,
  ] = useState<StudentProfile>(profile);


  useEffect(() => {
    setFormData(profile);
  }, [profile]);


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

      setFormData({
        ...formData,
        [field]: value
          .split(",")
          .map(
            (item) =>
              item.trim()
          )
          .filter(Boolean),
      });

      return;
    }


    setFormData({
      ...formData,
      [field]: value,
    });
  }


  async function handleSubmit(
    event: React.FormEvent<HTMLFormElement>
  ) {

    event.preventDefault();

    await onSave(formData);
  }


  return (

    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4 backdrop-blur-sm">

      <div className="glass w-full max-w-2xl rounded-2xl p-6 shadow-2xl">

        <div className="mb-6 flex items-start justify-between gap-4">

          <div>

            <p className="text-xs uppercase tracking-[0.2em] text-cyan-400">
              Student Profile
            </p>

            <h2 className="mt-2 text-2xl font-semibold text-white">
              Tune your opportunity engine
            </h2>

          </div>


          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-white/10 px-3 py-1.5 text-sm text-zinc-400 transition hover:border-white/20 hover:text-white"
          >
            Close
          </button>

        </div>


        <form
          onSubmit={handleSubmit}
          className="grid gap-4 sm:grid-cols-2"
        >

          <label className="grid gap-2">

            <span className="text-sm text-zinc-400">
              Name
            </span>

            <input
              value={formData.name}
              onChange={(event) =>
                updateField(
                  "name",
                  event.target.value
                )
              }
              className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-white outline-none transition focus:border-cyan-400/60"
            />

          </label>


          <label className="grid gap-2">

            <span className="text-sm text-zinc-400">
              Year
            </span>

            <input
              value={formData.year}
              onChange={(event) =>
                updateField(
                  "year",
                  event.target.value
                )
              }
              className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-white outline-none transition focus:border-cyan-400/60"
            />

          </label>


          <label className="grid gap-2">

            <span className="text-sm text-zinc-400">
              Branch
            </span>

            <input
              value={formData.branch}
              onChange={(event) =>
                updateField(
                  "branch",
                  event.target.value
                )
              }
              className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-white outline-none transition focus:border-cyan-400/60"
            />

          </label>


          <label className="grid gap-2">

            <span className="text-sm text-zinc-400">
              Location
            </span>

            <input
              value={formData.location}
              onChange={(event) =>
                updateField(
                  "location",
                  event.target.value
                )
              }
              className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-white outline-none transition focus:border-cyan-400/60"
            />

          </label>


          <label className="grid gap-2 sm:col-span-2">

            <span className="text-sm text-zinc-400">
              Skills
            </span>

            <input
              value={formData.skills.join(", ")}
              onChange={(event) =>
                updateField(
                  "skills",
                  event.target.value
                )
              }
              placeholder="Python, React, Java"
              className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-white outline-none transition focus:border-cyan-400/60"
            />

          </label>


          <label className="grid gap-2 sm:col-span-2">

            <span className="text-sm text-zinc-400">
              Interests
            </span>

            <input
              value={formData.interests.join(", ")}
              onChange={(event) =>
                updateField(
                  "interests",
                  event.target.value
                )
              }
              placeholder="AI, Software Development"
              className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-white outline-none transition focus:border-cyan-400/60"
            />

          </label>


          <div className="mt-4 flex justify-end gap-3 sm:col-span-2">

            <button
              type="button"
              onClick={onClose}
              className="rounded-xl border border-white/10 px-5 py-3 text-sm text-zinc-300"
            >
              Cancel
            </button>


            <button
              type="submit"
              disabled={saving}
              className="neon-button rounded-xl px-5 py-3 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60"
            >
              {saving
                ? "Saving..."
                : "Save Profile"}
            </button>

          </div>

        </form>

      </div>

    </div>
  );
}

export default ProfileModal;