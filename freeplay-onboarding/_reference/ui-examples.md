# UI Examples for Onboarding Flow

Full UI mockup examples for the onboarding orchestration skill.

## Fresh Start UI

```
FREEPLAY ONBOARDING
═══════════════════════════════════════════════════════════════

Welcome! This will guide you through setting up Freeplay for
your project. The process has 3 phases:

  [1] Analyze Codebase       ○ Not started
      Scan for prompts, detect framework, create migration plan

  [2] Migrate Prompts        ○ Not started
      Move prompts to Freeplay with version control

  [3] Integrate Logging      ○ Not started
      Set up tracing to capture LLM calls in Freeplay

Each phase saves progress, so you can stop and resume anytime.

Ready to begin? [y/n]
═══════════════════════════════════════════════════════════════
```

## Resume UI

```
FREEPLAY ONBOARDING - RESUMING
═══════════════════════════════════════════════════════════════

Found existing onboarding state. Here's your progress:

  [1] Analyze Codebase       ✓ Complete
      Found 5 prompts, detected LangGraph framework

  [2] Migrate Prompts        ✓ Complete
      4 prompts migrated to project "my-project"

  [3] Integrate Logging      ○ Not started
      Ready to set up tracing

Options:
  1. Continue from where you left off (Phase 3)
  2. Re-run a specific phase
  3. Start over (clear existing state)

What would you like to do? [1/2/3]
═══════════════════════════════════════════════════════════════
```

## Phase Complete UI

```
Phase 1 complete!

  ✓ Found 5 prompts (4 ready for migration, 1 needs manual work)
  ✓ Detected LangGraph framework
  ✓ Analysis saved to .freeplay/analysis.json

Continue to Phase 2 (Migrate Prompts)? [y/n]
```

## Interruption UI

```
Onboarding paused.

Your progress has been saved:
  ✓ Phase 1: Complete
  ✓ Phase 2: Complete
  ○ Phase 3: Not started

To resume later, run /freeplay-onboarding again.
Your state is saved in .freeplay/
```

## Skip Warning UI

```
You've asked to skip Phase 2 (Migrate Prompts).

⚠️  Warning: Skipping prompt migration means:
  - Prompts remain in your code (not managed by Freeplay)
  - No version history or A/B testing for prompts
  - Logging will still work, but without prompt template linkage

Are you sure you want to skip? [y/n]
```

## Final Summary UI

```
ONBOARDING COMPLETE
═══════════════════════════════════════════════════════════════

Congratulations! Your project is now set up with Freeplay.

SUMMARY:
  ✓ Analyzed codebase - found 5 prompts, LangGraph framework
  ✓ Migrated 4 prompts to Freeplay
  ✓ Integrated logging with callback handler

QUICK LINKS:
  Dashboard: https://app.freeplay.ai/projects/xxx
  Prompts:   https://app.freeplay.ai/projects/xxx/prompts
  Traces:    https://app.freeplay.ai/projects/xxx/traces

FILES CREATED:
  .freeplay/analysis.json        - Codebase analysis
  .freeplay/migration-manifest.json - Migration record
  .freeplay/integration-report.json - Integration details
  lib/freeplay_handler.py        - Logging handler

FILES MODIFIED:
  agents/main.py                 - Added Freeplay integration

NEXT STEPS:
  1. Run your agent and verify traces appear in Freeplay
  2. Try editing a prompt in Freeplay and see the new version
  3. Create a dataset and run your first evaluation
  4. Deploy prompts to production when ready

DOCUMENTATION:
  Freeplay Docs: https://docs.freeplay.ai
  SDK Reference: https://docs.freeplay.ai/sdk

Need help? Contact support@freeplay.ai

═══════════════════════════════════════════════════════════════
```

## Notes

These UI examples show the full display format for reference. The actual skill should present information clearly but doesn't need to match these examples exactly - adapt based on the actual onboarding state and context.
