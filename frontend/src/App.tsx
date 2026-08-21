import {
  useEffect,
  useMemo,
  useState,
} from "react";

import Header from "./components/Header";
import Hero from "./components/Hero";
import OpportunityGrid from "./components/OpportunityGrid";
import ProfileModal from "./components/ProfileModal";
import SmartMatchPanel from "./components/SmartMatchPanel";

import {
  getMatch,
  getOpportunities,
  getPreparation,
  getStudentProfile,
  saveStudentProfile,
  searchOpportunities,
} from "./api";

import { demoProfile } from "./data/demoProfile";

import type {
  MatchResponse,
  Opportunity,
  StudentProfile,
} from "./types";


function App() {

  const [
  profile,
  setProfile,
] = useState<StudentProfile>({
  name: "Sivakarthik",
  year: 2,
  branch: "Computer Science Engineering",
  location: "Bangalore, India",
  interests: ["Artificial Intelligence", "Web Development"],
  skills: ["Python", "FastAPI", "React", "SQL"],
  opportunity_type: "internship"
});


  const [
    opportunities,
    setOpportunities,
  ] = useState<Opportunity[]>([]);


  const [
    selectedOpportunity,
    setSelectedOpportunity,
  ] = useState<Opportunity>();


  const [
    matchData,
    setMatchData,
  ] = useState<MatchResponse>();


  const [
    searchTerm,
    setSearchTerm,
  ] = useState("");


  const [
    activeFilter,
    setActiveFilter,
  ] = useState("All");


  const [
    loading,
    setLoading,
  ] = useState(false);


  const [
    matchLoading,
    setMatchLoading,
  ] = useState(false);


  const [
    profileOpen,
    setProfileOpen,
  ] = useState(false);


  const [
    savingProfile,
    setSavingProfile,
  ] = useState(false);


  const [
    statusMessage,
    setStatusMessage,
  ] = useState(
    "Engine ready. Launch a live search."
  );


  useEffect(() => {

    async function initialize() {

      try {

        const savedProfile =
          await getStudentProfile();

        if (savedProfile?.name) {
          setProfile(savedProfile);
        }

      } catch {
        setProfile(demoProfile);
      }


      try {

        const existingOpportunities =
          await getOpportunities();

        setOpportunities(
          existingOpportunities
        );

      } catch {
        // Live search can still populate results.
      }

    }

    initialize();

  }, []);


  const filteredOpportunities =
    useMemo(() => {

      const query =
        searchTerm
          .trim()
          .toLowerCase();


      return opportunities.filter(
        (opportunity) => {

          const searchableText = [

            opportunity.title,

            opportunity.organization,

            opportunity.company,

            opportunity.description,

            opportunity.type,

            ...(opportunity.skills || []),

            ...(opportunity.tags || []),

          ]
            .filter(Boolean)
            .join(" ")
            .toLowerCase();


          const matchesSearch =
            !query ||
            searchableText.includes(query);


          if (
            activeFilter === "All"
          ) {
            return matchesSearch;
          }


          const filter =
            activeFilter.toLowerCase();


          const matchesFilter =
            searchableText.includes(
              filter
            );


          return (
            matchesSearch &&
            matchesFilter
          );
        }
      );

    }, [
      opportunities,
      searchTerm,
      activeFilter,
    ]);


  async function launchEngine() {

    setLoading(true);

    setStatusMessage(
      "Scanning live opportunities..."
    );


    try {

      const response =
        await searchOpportunities(
          profile
        );


      setOpportunities(
        response.opportunities
      );


      setSelectedOpportunity(
        response.opportunities[0]
      );


      setStatusMessage(
        `${response.count} opportunities discovered for ${profile.name}.`
      );


      if (
        response.opportunities.length > 0
      ) {

        await selectOpportunity(
          response.opportunities[0]
        );

      }

    } catch (error) {

      console.error(error);

      setStatusMessage(
        "Live search failed. Check that the FastAPI backend is running."
      );

    } finally {

      setLoading(false);

    }

  }


  async function selectOpportunity(
    opportunity: Opportunity
  ) {

    setSelectedOpportunity(
      opportunity
    );

    setMatchData(undefined);

    setMatchLoading(true);


    try {

      const data =
        await getMatch(
          opportunity.id
        );

      setMatchData(data);

    } catch (error) {

      console.error(error);

    } finally {

      setMatchLoading(false);

    }

  }


  function claimOpportunity(
    opportunity: Opportunity
  ) {

    const link =
      opportunity.application_url ||
      opportunity.link ||
      opportunity.url;


    if (link) {

      window.open(
        link,
        "_blank",
        "noopener,noreferrer"
      );

    } else {

      setStatusMessage(
        "No verified application link was returned for this opportunity."
      );

    }

  }


  async function handleSaveProfile(
    updatedProfile: StudentProfile
  ) {

    setSavingProfile(true);


    try {

      const saved =
        await saveStudentProfile(
          updatedProfile
        );

      setProfile(saved);

      setProfileOpen(false);

      setStatusMessage(
        "Student profile updated."
      );

    } catch (error) {

      console.error(error);

      setStatusMessage(
        "Profile could not be saved."
      );

    } finally {

      setSavingProfile(false);

    }

  }


  async function buildPreparationPlan() {

    if (!selectedOpportunity) {
      return;
    }


    try {

      await getPreparation(
        selectedOpportunity.id
      );

      setStatusMessage(
        "Preparation analysis generated by the backend."
      );

    } catch (error) {

      console.error(error);

      setStatusMessage(
        "Preparation analysis could not be generated."
      );

    }

  }


  return (

    <main className="min-h-screen bg-[#0a0a0c] text-white">

      <Header
        onEditProfile={() =>
          setProfileOpen(true)
        }
      />


      <Hero
        searchTerm={searchTerm}

        activeFilter={activeFilter}

        loading={loading}

        onSearchChange={setSearchTerm}

        onFilterChange={setActiveFilter}

        onLaunch={launchEngine}
      />


      <section
        id="opportunities"
        className="mx-auto max-w-7xl px-5 py-12 lg:px-8"
      >

        <div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">

          <div>

            <p className="text-xs uppercase tracking-[0.18em] text-zinc-500">
              Live Opportunity Feed
            </p>

            <h2 className="mt-2 text-2xl font-semibold text-white">
              Opportunities worth your attention
            </h2>

          </div>


          <div className="text-sm text-zinc-500">

            {filteredOpportunities.length} visible

          </div>

        </div>


        <div className="mb-6 rounded-xl border border-white/7 bg-white/[0.02] px-4 py-3 text-sm text-zinc-400">

          {statusMessage}

        </div>


        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">

          <OpportunityGrid
            opportunities={
              filteredOpportunities
            }

            selectedOpportunity={
              selectedOpportunity
            }

            loading={loading}

            onSelect={
              selectOpportunity
            }

            onClaim={
              claimOpportunity
            }
            onPrepare={
              buildPreparationPlan
            }
          />


          <SmartMatchPanel
            match={
              matchData
            }

            loading={matchLoading}
            onPrepare={
              buildPreparationPlan
            }
          />

        </div>

      </section>


      <footer className="border-t border-white/6 px-5 py-8">

        <div className="mx-auto flex max-w-7xl flex-col justify-between gap-3 text-xs text-zinc-600 sm:flex-row">

          <span>
            Student Opportunity Engine
          </span>

          <span>
            Discover → Match → Diagnose → Prepare → Apply
          </span>

        </div>

      </footer>


      <ProfileModal
        open={profileOpen}

        profile={profile}

        saving={savingProfile}

        onClose={() =>
          setProfileOpen(false)
        }

        onSave={
          handleSaveProfile
        }
      />

    </main>
  );
}


export default App;