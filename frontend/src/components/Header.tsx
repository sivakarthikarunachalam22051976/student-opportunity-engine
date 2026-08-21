import {
  Activity,
  Settings2,
  UserRound,
} from "lucide-react";


type HeaderProps = {
  onEditProfile: () => void;
};


export default function Header({
  onEditProfile,
}: HeaderProps) {

  return (
    <header className="sticky top-0 z-40 border-b border-white/8 bg-[#0a0a0c]/80 backdrop-blur-xl">

      <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 lg:px-8">

        <div className="flex items-center gap-3">

          <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-300/25 bg-cyan-400/10">

            <Activity
              size={21}
              className="text-[#00f0ff]"
            />

          </div>

          <div>
            <p className="text-sm font-semibold tracking-wide text-white">
              Student Opportunity
            </p>

            <p className="text-xs tracking-[0.22em] text-zinc-500">
              ENGINE
            </p>
          </div>

        </div>


        <div className="hidden items-center gap-6 text-sm text-zinc-400 md:flex">

          <span>Discover</span>
          <span>Match</span>
          <span>Prepare</span>

        </div>


        <button
          onClick={onEditProfile}
          className="glass flex items-center gap-2 rounded-xl px-4 py-2 text-sm text-zinc-200 transition hover:border-cyan-300/30 hover:text-white"
        >

          <UserRound size={16} />

          <span className="hidden sm:inline">
            Profile
          </span>

          <Settings2
            size={15}
            className="text-zinc-500"
          />

        </button>

      </div>

    </header>
  );
}