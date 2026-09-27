# Beyond the Web Viewer Blob: The Prompt Thickens

## Working With an AI Co-Developer

<aside class="article-resources" aria-label="Article files">
  <a class="article-resources__repository" href="https://github.com/LonCook/filemaker-articles/tree/main/filemaker-web-viewer-series/articles/part-04-the-prompt-thickens">
    <img src="https://raw.githubusercontent.com/LonCook/filemaker-articles/main/assets/icons/mark-github-16.svg" alt="" width="18" height="18">
    <span>View this article's files on GitHub</span>
  </a>
  <a class="article-resources__download" href="https://github.com/LonCook/filemaker-articles/raw/refs/heads/main/filemaker-web-viewer-series/articles/part-04-the-prompt-thickens/demo/Flicks_WebViewer_Framework_04_HybridInterface.fmp12" download>
    <img src="https://raw.githubusercontent.com/LonCook/filemaker-articles/main/assets/icons/file-arrow-down-16.svg" alt="" width="18" height="18">
    <span>Download the demo file: Flicks_WebViewer_Framework_04_HybridInterface.fmp12</span>
  </a>
</aside>

Last round, FileMaker shaped native movie records into a documented context, JavaScript rendered them, and a click returned through `WV.sendAction`. FileMaker validated the stable movie id, performed the native work, and sent its authoritative selection back.

This pass adds the promised visual payoff: a rating landscape, an interactive rating distribution, a nearby-in-rank comparison, and a native FileMaker portal behaving as one interface.

The new subject is not chart construction. It is how the change was developed with an AI co-developer without handing the application over to it.

AI can produce a great deal of plausible code quickly. Plausible is useful. It is not the same as correct, integrated, or accepted. The work still needs a human-owned purpose, current source, explicit contracts, a review boundary, evidence from the right environment, and a definition of done that does not become more accommodating merely because the output has arrived.

The method used here has six parts:

1. Define the job before prompting.
2. Supply the current source and contracts.
3. Constrain the requested change.
4. Review the output as a proposal.
5. Turn observed failure into the next revision.
6. Require native FileMaker evidence before acceptance.

The hybrid interface is the case study. The method is the article.

## 1. Define The Job Before Prompting

“Build a dashboard” leaves the important decisions conveniently unattended.

Before requesting code, I wrote a human brief describing what the interface had to do. The visible payoff was specific:

- plot every FileMaker-shaped movie by release year and global rating;
- show the FileMaker-owned selected movie across the visualization;
- let the user choose and clear a contiguous rating band;
- show the same movie scope in a native FileMaker list;
- let either surface report movie selection;
- return accepted selection and band state to both surfaces.

The brief also assigned ownership:

> JavaScript may retain hover, drag, animation, and in-flight presentation state. JavaScript may not retain authoritative selected movie, rating band, native found set, or acknowledgement state.

That sentence does more work than a paragraph about colors or transitions. It tells generated code what it is allowed to remember and, more importantly, what it is not allowed to decide.

FileMaker owns:

- the ordered movie scope;
- the selected stable movie id;
- the rating band;
- validation of incoming actions;
- the context returned as acknowledgement.

JavaScript owns:

- the rating landscape, distribution, and rank-neighborhood presentation;
- pointer and keyboard interaction;
- transient hover and drag previews;
- narrow reports of user intent through the existing bridge.

This is the same custody arrangement established earlier in the series. A larger visualization does not require a new constitution.

## 2. Supply Current Source And Contracts

The production Flicks file already had a rating dashboard. That made it a useful source reference, but not a sensible package to import whole.

Fresh exports identified its page, renderer, visualization dependency, FileMaker action script, focus script, and state reducer. Inspection also showed direct FileMaker calls, optimistic browser state, synthetic defaults, movers, layered surfaces, and dependencies on the broader production application.

The context packet therefore included:

- fresh DDR, Summary, and module exports from the cumulative demo;
- fresh exports from the read-only production reference;
- the exact current page, renderer, bridge, context builder, and action handler;
- representative context and action JSON;
- module headers and dependency information;
- native FileMaker screenshots;
- acceptance tests and stop lines.

It distinguished full source from abridged article material. It also recorded deliberate omissions. The production dashboard could inspire the visual direction without importing its router, reducer, direct bridge calls, fallback data, or 3D subsystem.

That distinction matters when working with AI. A screenshot can describe appearance. It cannot establish the current schema, script names, action contract, dependency order, or state ownership. Memory is not better merely because it has been formatted as a prompt.

## 3. Constrain The Requested Change

The initial request was narrow. This abridged excerpt asked for two proposed modules and explicitly stopped before FileMaker integration:

```text
Using the full source and manifest in this evidence packet,
propose modules 43 and 44 for the hybrid interface.
...
Return complete page and renderer module source.
Do not modify FileMaker scripts yet.
```

The prompt named the permitted input and output; this is abridged from the complete preserved prompt:

```text
- Use only the supplied ranked_view.rows and returned FileMaker context.
- Send only the three allowed hybrid.* actions through WV.sendAction.
- Do not call FileMaker.PerformScript directly.
- Do not keep authoritative selected movie or rating band state in JavaScript.
- Preserve hover and in-flight drag state only.
...
```

It also named what must not arrive:

```text
Do not import production module 66, movers, layered surfaces,
camera behavior, synthetic defaults, production reducers,
or cache/deployment code.
```

Those are not ornamental prompt details. Each one closes a plausible route by which a useful-looking renderer could violate the existing framework.

The stop instruction matters too. The first output was allowed to propose renderer modules. It was not authorized to redesign FileMaker scripts, add schema, or roam through the cumulative demo improving things it had recently noticed.

## 4. Review The Output As A Proposal

The AI returned modules `43` and `44` with the expected division:

| Index | Module | Job |
| ---: | --- | --- |
| `43` | `wv.page.hybrid.rating.html` | assemble the page and loading surface |
| `44` | `wv.renderer.hybrid.rating.js` | render the visualization and report selection and band intent |

Several important checks passed:

- the dependencies and exports were declared;
- rows came only from `ranked_view.rows`;
- stable `movie_id` values were used for actions;
- empty input remained visibly empty;
- outbound actions used `WV.sendAction`;
- no production router, reducer, or synthetic movies appeared;
- returned context remained authoritative.

That did not make the proposal accepted.

The browser harness exposed a pointer defect. In this abridged excerpt, the initial code captured the pointer on the starting histogram rectangle:

```js
rect.addEventListener("pointerdown", function (event) {
  local.dragStart = index;
  local.dragEnd = index;
  if (rect.setPointerCapture) rect.setPointerCapture(event.pointerId);
});
// ...
rect.addEventListener("pointerenter", function () {
  if (local.dragStart >= 0) local.dragEnd = index;
});
```

Dragging across several bins still emitted the starting bin alone. Pointer capture kept events on the first rectangle while range growth depended on entering its siblings. The code was internally tidy and externally wrong.

Review found two quieter defects as well. `Number(null)` and `Number("")` both produce zero, so incomplete returned state could masquerade as a valid rating. Inclusive overlap at shared bin edges could also highlight an adjacent bin that was not actually inside the acknowledged range.

These findings came from three different review questions:

1. Does the code obey the contract?
2. Does the code behave correctly in the browser?
3. Does its treatment of values match the data contract at edge cases?

“The code runs” answers none of them particularly well.

## 5. Turn Failure Into The Revision

The revision request contained the observed behavior, the failed layer, the relevant source mechanism, the required correction, and the boundaries that must remain unchanged.

This is an abridged excerpt:

```text
Observed browser-harness failure:

- Drag began in the first histogram bin and crossed several visible bars.
- The outbound bounds covered only the starting bin.
- Keyboard range selection worked.
- Pointer capture is set on the starting rect, while range growth
  depends on pointerenter firing on sibling rectangles.
...
Required correction:

1. Track pointer drag at the chart level.
2. Convert the current pointer x-coordinate to a clamped bin index.
3. Keep the starting bin as transient state.
4. Commit one narrow hybrid.set_rating_band action on release.
5. Preserve FileMaker ownership.
...
```

This is a much better revision request than “the drag is broken.” It identifies what the evidence proved without prescribing an unrelated rewrite.

The corrected code moved capture and movement to the chart; this excerpt omits unrelated keyboard and rendering code:

```js
rect.addEventListener("pointerdown", function (event) {
  local.dragStart = index;
  local.dragEnd = index;
  if (chart.setPointerCapture) chart.setPointerCapture(event.pointerId);
  // ...
});
// ...
chart.addEventListener("pointermove", function (event) {
  if (local.dragStart < 0) return;
  local.dragEnd = pointerBin(event);
  updatePreview();
});
// ...
chart.addEventListener("pointerup", function (event) {
  if (local.dragStart < 0) return;
  local.dragEnd = pointerBin(event);
  commitRange(local.dragStart, local.dragEnd);
  // ...
});
```

The numeric helper now rejects null and empty input before conversion, and acknowledged band overlap no longer double-counts shared edges.

The revision preserved everything already accepted. It did not rename actions, change module indexes, import production state, or give JavaScript authority it had not previously possessed. A useful revision narrows the defect. It does not reopen the whole project because the prompt has regained access to a keyboard.

## Human Review Still Owns The Payoff

The corrected histogram satisfied the initial interaction brief. It did not yet provide enough visual payoff for this installment.

That was a product decision, not a code defect. The target expanded into three linked views:

1. A rating landscape showing year against global rating.
2. The accessible rating distribution and contiguous band control.
3. A nearby-in-rank comparison centered on FileMaker’s selected movie.

The revised renderer reused the same row contract and the same three actions. No new schema or action router was required. The visual scope grew; the ownership boundary did not.

![The approved rating-landscape target. This mockup established visual direction; it is not native FileMaker acceptance evidence.](<screenshots/10-hybrid-rating-landscape-mockup.png>)

This is another part of working with an AI co-developer: generated code can satisfy its prompt and still fail the larger human purpose. Contract compliance is necessary. It is not a substitute for taste, priorities, or judgment about whether the result was worth building.

## 6. Require Evidence From The Right Environment

The browser harness was useful for:

- SVG geometry and responsive layout;
- pointer and keyboard behavior;
- empty, selected, and acknowledged states;
- outbound action-envelope capture;
- checking that the renderer contained no direct FileMaker bridge call.

It could not prove:

- native layout context;
- FileMaker portal behavior;
- script validation;
- authoritative selection and rating-band state;
- acknowledgement through the real Web Viewer;
- whether the loaded viewer remained present while native state changed.

Those claims required the FileMaker target.

The final `WV Framework - Hybrid` layout uses a stable one-record `SOLUTION__all` host. `wv_main` remains on that record while a native `MOVIE_GLOBAL_RATING` portal displays the FileMaker-owned movie scope. An ordered list of stable ids drives portal membership. `FOCUS::g_wv_demo_movie_id` owns selection, and the rating globals own the acknowledged band.

A portal-row click and a Web Viewer selection both update that FileMaker state, patch the context, and push acknowledgement. The two surfaces do not synchronize directly with one another. They synchronize with FileMaker.

```text
Native portal intent ─┐
                      ├─> FileMaker-owned state
Web Viewer intent ────┘            │
                                   ├─> native portal treatment
                                   └─> acknowledged Web Viewer context
```

That is all the implementation detail the article needs. The complete scripts, relationship, object bindings, module source, and FMXML belong in the build materials.

The fresh DDR and Save as XML export verify the installed layout context, portal, object names, script histories, merge calculations, and interaction-path structure. Static source reconciliation is supporting evidence, not native behavioral acceptance.

Before publication, the current target still needs final native captures showing:

- a clean Run with the complete hybrid interface;
- portal-row selection acknowledged in the visualization;
- Web Viewer dot selection acknowledged in the portal;
- a rating-band change reflected in both surfaces.

<!-- SCREENSHOT NEEDED: complete current native hybrid interface. -->

<!-- SCREENSHOT NEEDED: portal selection and Web Viewer acknowledgement. -->

<!-- SCREENSHOT NEEDED: acknowledged rating band and filtered portal. -->

The placeholders stay explicit because a screenshot from the browser harness would prove only that the browser harness can take screenshots. It has already demonstrated that talent.

## What Remains Human-Owned

AI helped produce and revise the modules. It helped compare outputs with source exports, assemble pasteable FileMaker XML, and narrow defects from recorded evidence.

It did not own:

- the purpose of the visualization;
- the division of responsibility between FileMaker and JavaScript;
- the allowed data and action contracts;
- authorization to change schema or scripts;
- the decision that the first visual payoff was insufficient;
- the definition of native acceptance;
- the decision to keep generated code in the maintained system.

These are not the chores left over after AI development. They are the development decisions that make AI assistance useful.

## A Reusable AI Co-Development Checklist

For a FileMaker Web Viewer change, I would use the same sequence again.

### Before the prompt

- Define the visible job and why it belongs in a Web Viewer.
- Assign authoritative state explicitly.
- Export and inspect current FileMaker and module source.
- Identify the exact allowed change boundary.
- Write acceptance tests and stop lines.

### In the prompt

- Name the supplied inputs and expected outputs.
- Provide representative context and action messages.
- Require the established public bridge.
- Name forbidden dependencies and authority.
- Ask for a proposal at the smallest useful integration boundary.

### During review

- Compare dependencies, fields, scripts, and APIs with current source.
- Check ownership, not merely syntax.
- Exercise empty, loading, selected, filtered, and error states.
- Preserve the untouched initial output and record accepted and rejected findings.

### During revision

- Report observed behavior and expected behavior.
- Identify the failed layer.
- Supply the relevant source and evidence.
- Preserve everything already accepted.
- Stop broad rewrites from entering through a narrow defect.

### Before acceptance

- Use browser evidence only for browser claims.
- Test layout, bridge, records, validation, and acknowledgement in FileMaker.
- Reconcile final source exports with the article and build materials.
- Do not call a passing component test a completed interface.

## Takeaway

AI accelerated the implementation. The framework made the output inspectable. The contract made it reviewable. Evidence made revision specific. FileMaker testing decided whether the integrated result was real.

That is the lesson:

> AI accelerates implementation only when purpose, authority, review, and acceptance remain explicit. Otherwise, it accelerates plausible rework.

The hybrid rating interface is the payoff, but it is also evidence for a more reusable practice. Give AI a bounded job, current source, and a place to land. Review what arrives as a proposal. Feed failures back as evidence. Keep application authority where it belongs.

Next time, the series can turn to cache versions, dirty state, loaded-viewer tracking, bounded recovery, deployment, and rollback. Those mechanisms deserve automation. The decisions behind them do not.
