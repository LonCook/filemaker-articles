# FileMaker Web Viewer Series Article Contracts

These contracts keep the demo files cumulative without letting later convenience leak backward into earlier teaching files.

## Series Teaching Goal

The visualizations are teaching surfaces, not the subject of the series. Each demo should make a reusable method inspectable: modular code libraries, explicit FileMaker-to-Web-Viewer data contracts, narrow actions returning to FileMaker, FileMaker-owned application state, layered debugging, and constrained AI-assisted development.

Use concrete fields, scripts, modules, payloads, and screenshots as evidence. Explain a visualization's particular mechanics only as far as the reader needs to follow the method being taught. Exact schema references, module indexes, full script steps, and complete code belong in the build instructions and source exports when they do not advance the published argument.

## Series Identity And Publication Roadmap

Use `Beyond the Web Viewer Blob:` as the fixed public title prefix. The titles should read as parts of one cumulative argument, not as unrelated posts that happen to know the same FileMaker scripts.

1. **Beyond the Web Viewer Blob: A Modular Framework for FileMaker Web Viewer Visualizations**
   - Break apart the calculated HTML blob.
   - Establish named modules, explicit assembly, and one-way context push.

2. **Beyond the Web Viewer Blob: The Blob Talks Back**
   - Add action envelopes and the JavaScript-to-FileMaker return path.
   - Use `Context in. Actions out. FileMaker owns the result.` as the recurring body formulation, not as a second competing title.

3. **Beyond the Web Viewer Blob: Let the Record Show**
   - Subtitle: *Native FileMaker Records In, Ranked Views Out*
   - Use a ranked-list surface to teach FileMaker-owned native data shaping, modular rendering, and a visible record-selection round trip.

4. **Beyond the Web Viewer Blob: The Prompt Thickens**
   - Subtitle: *Working With an AI Co-Developer*
   - Use the actual prompt, supplied context, review, native FileMaker testing, and revision loop to build the visual payoff: a richer Web Viewer visualization coordinated bidirectionally with a native FileMaker portal list on a stable host layout.

5. **Beyond the Web Viewer Blob: Cache Me If You Can**
   - Subtitle: *State, Loading, and the FileMaker Web Viewer Production Pattern*
   - Cover dirty/version tokens, cache rebuilding, loaded-state tracking, smarter loading, and deployment discipline.

Article numbers remain useful in planning documents and downloadable demo filenames. In published prose, use conversational continuity language such as `last round`, `this pass`, and `next time` rather than repeatedly announcing article numbers.

## Individual Article Outlines

These outlines are the editorial spine for the series. A handoff may add implementation detail, screenshots, or source-backed code inserts, but it should not quietly change an article's job. If the scope changes, update this document first; otherwise the roadmap becomes a collection of confident historical artifacts.

### 1. Beyond the Web Viewer Blob: A Modular Framework for FileMaker Web Viewer Visualizations

**Editorial job**

Replace the calculated HTML blob with a small, named module system. Prove that FileMaker can assemble the Web Viewer package, load it, build explicit context, and push that context into a read-only renderer.

**Body outline**

1. Open with the familiar lifecycle of a useful HTML calculation becoming a maintenance problem.
2. Explain why the blob is a delivery and review problem, not evidence that HTML, CSS, or JavaScript are inherently unruly.
3. Introduce the framework split: shell, CSS, runtime, context bridge, boot module, page module, and renderer.
4. Show the thin demo file and identify what was deliberately removed from the production Flicks file.
5. Explain module records, dependency order, payload visibility, and the module-header contract.
6. Show the explicit cache-rebuild contract: commit, rebuild, clear loaded state, and reload.
7. Walk through the visible teaching path:
   - choose FileMaker inputs
   - build context JSON
   - load the Web Viewer
   - push context
   - run the complete sequence
   - edit one module and rebuild
8. Separate FileMaker ownership from JavaScript rendering responsibility.
9. Introduce the value of a modular landing zone for AI-assisted code without turning the article into an AI workflow tutorial.
10. Close with the one-way boundary and the reason the next pass adds a controlled return path.

**Demo milestone**

The reader can inspect the retained modules, rebuild the library explicitly, load `wv_main`, and push a context payload that the renderer displays.

**Scope boundary**

No Web Viewer actions, native record arrays, ranked-list renderer, production record mutation, smart loading as the main path, or production application chrome.

**Handoff**

The viewer can receive context but cannot report user intent. The next pass lets it talk back without giving it ownership of FileMaker state.

### 2. Beyond the Web Viewer Blob: The Blob Talks Back

**Editorial job**

Add the JavaScript-to-FileMaker return path. Teach action envelopes as reports of user intent while FileMaker remains the only application-state owner.

**Body outline**

1. Resume from the read-only context card built last round; state plainly what is changing in this pass.
2. Disclose early that the JavaScript was developed with AI assistance and that the full co-development workflow will receive its own installment.
3. Explain why a button, selectable row, or filter requires a return path to FileMaker.
4. Distinguish intent from state: the viewer may report what the user did, but it does not decide what FileMaker must change.
5. Define the action-envelope contract:
   - `__wv_action` metadata
   - `type`
   - `payload`
6. Introduce module `25`, `wv.platform.actions.js`, and the single public bridge `WV.sendAction(type, payload, options)`.
7. Show how the existing renderer adds `Inspect Context` and `Mark Movie` buttons without learning FileMaker script architecture.
8. Introduce `WV__Demo_Handle_Action` as FileMaker's one receiving door; validate the envelope before accepting either demo action.
9. Explain the asynchronous acknowledgement path: JavaScript reports the action, FileMaker handles it, rebuilds context, and pushes the acknowledged state back.
10. Keep loading order and cache rebuilding visible so a missing action module cannot masquerade as an event-handling mystery.
11. Walk through the complete round trip:
    - build context
    - load the viewer
    - push context
    - inspect context
    - mark the movie
    - compare the incoming context JSON with the outgoing action JSON
12. Debug the two directions separately: context-in failures, action-out failures, handler validation failures, and acknowledgement-push failures.
13. Reassert the ownership boundary and show why the action API gives AI-generated renderer code a constrained landing zone.
14. Close with the recurring formulation:

```text
Context in.
Actions out.
FileMaker owns the result.
```

**Demo milestone**

The reader can click actions inside `wv_main`, inspect the received envelope in native FileMaker fields, and see FileMaker acknowledgement context rendered back into the same viewer.

**Scope boundary**

No ranked-list renderer, native record arrays, durable production mutation, navigation system, general-purpose action router, hidden cache triggers, or smart `ensure loaded` path as the main demonstration.

**Handoff**

The two directions and their ownership contract are settled. The next pass can carry real FileMaker records and repeated rows without inventing a new bridge for every interaction.

### 3. Beyond the Web Viewer Blob: Let the Record Show

*Native FileMaker Records In, Ranked Views Out*

**Editorial job**

Move from scalar demo defaults to native FileMaker record data. Use the ranked list as a concrete test surface for the reusable method: FileMaker shapes a documented contract, named Web Viewer modules render it, JavaScript reports narrow user intent, and FileMaker validates, performs the native record work, and returns authoritative state. Do not turn the article into a tutorial on ranked-list design or this demo's schema.

**Body outline**

1. Resume from the completed round trip: the transport is established; now the payload earns something more substantial to carry.
2. Define the ranked-view job before writing renderer code: what the reader should see, select, and inspect.
3. Establish the native-data contract, including stable record ids, display values, rank/order values, selected state, and any filter metadata the renderer actually needs.
4. Show FileMaker establishing an inspectable native found set and shaping those records into JSON. Keep find, relationship, calculation, and privilege decisions on the FileMaker side; abridge implementation excerpts when the full calculation does not advance that ownership lesson.
5. Explain why the payload should contain display-ready facts without becoming a serialized copy of the entire schema.
6. Introduce the ranked-list page and renderer as named, independently reviewable modules. Use their dependency declaration to demonstrate the modular-library method, not as an inventory exercise.
7. Render empty, loading, populated, and selected states from the same documented contract.
8. Reuse `WV.sendAction` for row selection. Move quickly past bridge mechanics already taught last round and concentrate on the new method: FileMaker validates the stable id against current state, performs native record navigation, and returns the resulting selection.
9. Introduce `ensure loaded` only where the richer renderer makes unconditional reloads visibly wasteful. Keep cache state and fallback behavior inspectable.
10. Walk through the native-data path:
   - establish and visibly inspect the FileMaker found set
   - build the ranked-view payload
   - load or ensure the correct viewer package
   - push context
   - select a Web Viewer row
   - observe FileMaker navigate to the corresponding native record
   - inspect the action and acknowledged selection
11. Debug the layers separately: FileMaker found set, native current record, JSON shape, repeated-row rendering, selected-state context, and action payload ids.
12. Show how the explicit input, output, authority, and module boundaries make AI-assisted renderer work inspectable, while reserving the prompt/review/test transcript for the next installment.
13. Close by restating that the ranked list is evidence for the method, not the curriculum, and separate the teaching loader from a production-ready loading and deployment pattern.

**Demo milestone**

The reader can establish and inspect a native FileMaker found set, shape its records into a ranked-view payload, render repeated rows, and send stable-id selection intent back through the existing action bridge. FileMaker navigates to the corresponding native movie record, exposes the current record and found-set position on the layout, and returns that authoritative selection through context.

**Scope boundary**

No JavaScript queries against FileMaker data, no authoritative browser-side selection, no broad production record mutation, no full native FileMaker list, no navigation drawer or full Flicks application chrome, and no claim that the demo loading pattern is the final deployment contract. The published body does not need to reproduce every exact script, dependency, or schema reference preserved in the source-backed build materials.

**Handoff**

The series now contains a realistic data and interaction contract worth extending. The next pass exposes the AI co-development loop while using it to build the visual payoff: a richer Web Viewer visualization coordinated bidirectionally with a native FileMaker list.

### 4. Beyond the Web Viewer Blob: The Prompt Thickens

*Working With an AI Co-Developer*

**Editorial job**

Make the AI-assisted development process visible and reviewable while delivering the series' visual payoff. Build a complete hybrid interface in which a richer Web Viewer visualization and a native FileMaker portal list share FileMaker-owned selection and filter state through the established context and action contracts. Keep the Web Viewer on a stable `SOLUTION__all` host; let FileMaker change the portal relationship list and selected-id globals without navigating the host record. Show how a FileMaker developer frames that work, supplies the relevant contracts, evaluates the proposed change, tests it in the native file, and sends evidence back into the next revision.

**Body outline**

1. Open with the distinction established earlier: AI can produce a useful paste quickly; the framework determines whether that paste has a maintainable place to live.
2. Define the payoff before prompting: a native FileMaker portal list and a richer Web Viewer visualization should behave as one interface without pretending they have two owners.
3. Choose a source-backed visualization whose interaction materially exceeds what the native list readily provides. The work should exercise the existing module, payload, and action contracts rather than requiring a new subsystem for the sake of spectacle.
4. Define the human-owned brief:
   - desired user-visible behavior
   - native FileMaker portal-list behavior
   - Web Viewer visualization behavior
   - modules and FileMaker scripts allowed to change
   - input payload shape
   - action types and handler boundary
   - state JavaScript is not allowed to own
   - acceptance tests
5. Show the context supplied to the AI: current module headers and code, representative JSON, FileMaker script contracts, native list behavior, screenshots, and relevant failure evidence.
6. Present the initial prompt and explain why each constraint is present.
7. Review the first output as a proposed change, not as proof of completion:
   - contract compliance
   - dependency discipline
   - invented APIs or fields
   - error and empty-state behavior
   - unnecessary scope growth
8. Integrate the accepted visualization into the module records and rebuild the library through the established FileMaker path.
9. Build the native FileMaker portal list from an ordered FileMaker-owned stable-id relationship list. Keep its SOLUTION-hosted Web Viewer record fixed while selection and rating-band membership change.
10. Prove both directions of the interface:
   - selecting a native FileMaker portal row updates the FileMaker-owned selected id, patches or rebuilds context, and updates the visualization
   - selecting, filtering, or brushing the visualization sends stable-id intent through `WV.sendAction`
   - FileMaker validates the intent, updates authoritative selection or the portal relationship list, refreshes only the native objects that require it, and returns acknowledgement context
   - the visualization and portal list settle on the same FileMaker-owned state without navigating or reloading the Web Viewer's host record
11. Test in two environments where useful:
   - browser harness for fast renderer inspection
   - native FileMaker for the actual list, bridge, layout, context, action, and acknowledgement path
12. Capture failures as evidence and use them to constrain the next prompt. Do not substitute “try again” for diagnosis.
13. Show the revision loop and the final diff or module excerpt that satisfies the acceptance tests.
14. Identify the human decisions that remain non-delegable: visualization purpose, application ownership, data contract, authorization, record effects, and acceptance of production risk.
15. Provide a reusable prompt/context/review checklist for later Web Viewer work.
16. Close with what AI changed about the speed of iteration—and what it did not change about responsibility.

**Demo milestone**

The reader can follow a complete hybrid-interface change from human brief through AI proposal, review, native FileMaker integration, failed test evidence, revision, and verified result. Selection or filtering in the native FileMaker portal list updates the Web Viewer visualization; interaction in the visualization returns stable-id intent to FileMaker, and both surfaces display the acknowledged FileMaker-owned state while the SOLUTION-hosted Web Viewer remains resident.

**Scope boundary**

No generic “prompt engineering” survey, model comparison, autonomous production changes, unreviewed code dump, browser-owned authoritative state, decorative chart with no interaction contract, or implication that a browser preview proves the FileMaker integration works.

**Handoff**

The visual payoff and the development workflow are both visible. The final pass can now tighten state, loading, cache, and deployment behavior for the complete portal-list/Web-Viewer interface without hiding either the machinery or who is responsible for it.

### 5. Beyond the Web Viewer Blob: Cache Me If You Can

*State, Loading, and the FileMaker Web Viewer Production Pattern*

**Editorial job**

Turn the cumulative teaching framework into an explicit production pattern. Automate the state and loading work the reader has already seen without turning it back into hidden magic with a better variable name.

**Body outline**

1. Resume from the working native-list/Web-Viewer interface and ask the production question: how does FileMaker know which code is cached, which viewer is loaded, and when either must change?
2. Define the production state model:
   - committed module records
   - library cache version or dirty token
   - loaded-viewer map
   - current context
   - action-contract version
3. Explain the commit trigger and dirty/version-token contract. Editing a module and changing the active library are separate events; treating them as identical is how stale code acquires tenure.
4. Show cache rebuild behavior, error reporting, version advancement, and loaded-map reset.
5. Introduce the production `ensure loaded` pattern:
   - attempt context push first
   - reload only when forced or when the viewer runtime is absent/stale
   - retry the context push once
   - return structured status
6. Extend the pattern to multiple viewers or batch loading only if the cumulative demo has a concrete need for it.
7. Revisit action handling for production: payload versions, allowed action types, privilege checks, current-record validation, and narrowly routed FileMaker scripts.
8. Define deployment discipline for module changes, demo-to-production promotion, cache versioning, and rollback evidence.
9. Add observability that earns its keep: structured script results, visible version information, targeted logging, and a failure matrix for cache, load, push, render, and action paths.
10. Walk through two production scenarios:
    - unchanged modules and an already-loaded viewer take the fast push path
    - a committed module change marks the cache dirty, rebuilds it, resets loaded state, reloads the viewer, and restores context
11. Walk through representative failures without collapsing them into “reload everything”:
    - cache rebuild failure
    - missing runtime
    - failed retry
    - invalid action version
    - stale or unauthorized record intent
12. Show how the same contracts improve later AI-assisted maintenance: smaller diffs, explicit acceptance tests, and fewer opportunities to invent state.
13. Close by restating the full architecture and the custody arrangement between FileMaker, the Web Viewer runtime, and generated code.

**Demo milestone**

The reader can edit and commit a module, observe the cache/version transition, run the smart loading path, confirm that unchanged viewers avoid needless reloads, and follow structured evidence when any stage fails.

**Scope boundary**

No universal framework claim, no invisible recovery loop without a retry limit, no client-owned application state, and no automation the reader has not already seen in its explicit form earlier in the series.

**Series close**

The blob has become a set of named modules, explicit data and action contracts, a reviewable AI workflow, and a production loading pattern. FileMaker still owns the application. That continuity is the point.

## FileMaker Script Header History Contract

When a later demo modifies an existing FileMaker script, preserve every existing modification-history entry in that script's header. Add the new entry at the top of the list; do not replace the prior entry merely because the current article is interested in the latest change.

Use newest-first order:

```text
# Modified: {{current timestamp}} — {{author}} — {{email}} : {{current change}}
# Modified: {{earlier timestamp}} — {{author}} — {{email}} : {{earlier change}}
# Modified: {{original timestamp}} — {{author}} — {{email}} : created
```

Preserve earlier entries verbatim, including their dates, authorship, and change notes. The header is a modification history, not a parking space reserved for whichever edit arrived most recently.

## Library Cache Contract

Article One keeps cache invalidation explicit. The reader edits `LIBRARY_CODE`, commits the record, clicks `Rebuild Library`, then reloads the Web Viewer. This is intentionally visible; the first article is about showing the machinery, not hiding it behind clever triggers. Clever triggers have had plenty of attention. They can wait.

Use this Article One utility script:

- `WV__Demo_Rebuild_Library`

It must:

- commit the current record
- call `library_json . ensure cache ( -force_rebuild ) : json` with `force_rebuild = 1`
- clear `$$wv_loaded_map`
- return a small JSON status object

Place the button on `WV Framework - Modules`, not on the main demo layout. The main demo layout should stay focused on load, build context, and push context.

## Viewer Load Contract

Article One should use the plain, visible sequence:

- `WV__Demo_Build_Context`
- `WV__Demo_Load_Viewer`
- `WV__Demo_Push_Context`

`WV__Demo_Load_Viewer` calls `. webviewer . load ( index ; -object_name )` directly. That is intentional. Article One is teaching the assembly line: build the package, load the Web Viewer, build the payload, push the payload. No smart loader yet; no "trust me, I handled it" layer wearing a little framework hat.

Retain `. webviewer . ensure loaded ...` and `. webviewer . ensure loaded . batch ...` only as framework carry-forward scripts if the demo file still needs them for later migration. They are not part of the Article One visible demo path.

Introduce the smarter "only reload when needed" path later, when there is enough complexity to justify it:

- Article Two may mention the pattern as a future convenience, but should still keep load/push behavior explicit.
- Article Three may introduce `ensure loaded` when native data and richer rendering make repeated reloads annoying enough to discuss honestly.
- Article Five should frame `ensure loaded` as part of the production pattern: push first, reload only on `force_reload` or missing Web Viewer runtime, then retry push once.

## Cross-Article Progression

Article Two may introduce a controlled dirty-marker after module edits, but the rebuild action should remain visible. The lesson is still teachable state management; do not turn the framework into a box of hidden springs yet.

Article Three may make viewer loading smart enough to rebuild when the module cache is dirty. At that point the demo is dealing with native data and a richer renderer, so reducing manual cache steps is reasonable.

Article Four pauses the framework progression long enough to show the AI co-development workflow already operating behind the JavaScript: prompt framing, supplied contracts, code review, native testing, and constrained revision.

Article Five should explain the production pattern explicitly:

- commit trigger
- dirty/version token
- cache rebuild
- loaded-map reset
- reload only when needed

The production pattern belongs after the reader has seen the parts separately. Otherwise the article teaches magic; FileMaker already has enough places to hide magic without our help.
