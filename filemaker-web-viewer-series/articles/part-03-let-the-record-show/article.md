# Beyond the Web Viewer Blob: Let the Record Show

## Native FileMaker Records In, Ranked Views Out

<aside class="article-resources" aria-label="Article files">
  <a class="article-resources__repository" href="https://github.com/LonCook/filemaker-articles/tree/main/filemaker-web-viewer-series/articles/part-03-let-the-record-show">
    <img src="https://raw.githubusercontent.com/LonCook/filemaker-articles/main/assets/icons/mark-github-16.svg" alt="" width="18" height="18">
    <span>View this article's files on GitHub</span>
  </a>
  <a class="article-resources__download" href="https://github.com/LonCook/filemaker-articles/raw/refs/heads/main/filemaker-web-viewer-series/articles/part-03-let-the-record-show/demo/Flicks_WebViewer_Framework_03_RankedViews.fmp12" download>
    <img src="https://raw.githubusercontent.com/LonCook/filemaker-articles/main/assets/icons/file-arrow-down-16.svg" alt="" width="18" height="18">
    <span>Download the demo file: Flicks_WebViewer_Framework_03_RankedViews.fmp12</span>
  </a>
</aside>

Last round, the Web Viewer learned to talk back. FileMaker pushed context in, JavaScript reported user intent through `WV.sendAction`, and FileMaker sent the result back to the Web Viewer while remaining in charge of application state.

The return trip worked. It was also deliberately harmless. Clicking `Mark Movie` changed visible demo fields; it did not change the current native record, the found set, or any production data. We proved the bridge before asking it to carry furniture.

This pass gives that bridge a real job.

FileMaker establishes a native found set of ranked movies, shapes those records into a documented JSON contract, and sends the contract to a repeated-row renderer. Click a ranked row inside the Web Viewer and JavaScript reports the stable movie id through the same action bridge. FileMaker validates the request against the current ranked collection, navigates to the corresponding native `MOVIE` record, rebuilds context, and returns the authoritative selection.

The visible difference matters. The selected row in the Web Viewer changes. So do the native movie title, movie id, current-record number, and FileMaker toolbar position. We are no longer proving that a button can set a global field. We are proving that one interface surface can ask FileMaker to navigate real records and then accept FileMaker's answer.

The ranked list is the example, not the curriculum. We are using it to make three methods visible: FileMaker shaping native data into an explicit contract, modular Web Viewer code rendering that contract, and AI-assisted JavaScript working inside boundaries a FileMaker developer can inspect and test.

## What We Are Building

The visible surface is intentionally plain: a ranked list of movies for the selected genre.

Each row shows:

- an explicit rank
- a display-ready movie title and year
- a stable FileMaker movie id
- a rating
- a selected treatment only when FileMaker says the row is selected

Above the rows, the viewer shows the active genre, the number of ranked movies, and the native current-record position. Outside the viewer, the FileMaker layout shows the current `MOVIE::title_year_display`, `MOVIE::ID`, the context JSON, the last action JSON, and the existing action diagnostics.

That last part is not decorative. Rank and found-set position are different facts, so the layout exposes both alongside the stable id that lets the two surfaces agree.

![The completed native FileMaker demo with ranked row four selected, the current MOVIE title and id visible, and FileMaker on record 17 of the 33-record found set.](<screenshots/04-ranked-final-native.png>)

No new tables or layouts were required. The richer result comes from a better payload, two additional library modules, and changed behavior in the existing builder and handler.

## Define The Contract Before Drawing Rows

A ranked list can look obvious enough that the visual design quietly becomes the data contract. The first column is rank, the big text is a title, the gold border means selected; surely JavaScript can work out the rest.

That is how display labels begin moonlighting as identifiers.

The renderer needs several kinds of values, and they are not interchangeable:

| Contract value | Job |
| --- | --- |
| `movie_id` | stable identity used in actions and validation |
| `display_title` | display-ready FileMaker value |
| `year` | explicit source fact available to later presentation changes |
| `rating` | visible score |
| `rank` | native ranking fact when available |
| `order` | explicit array/display order |
| `selected` | FileMaker-owned selected state for this row |

The rows are only part of what FileMaker sends. The Web Viewer also needs the active genre, the number of matching movies, the selected movie, the native record position, and the message to show when nothing matches. The complete payload is easier to understand in one piece. We will look at the actual JSON next.

## The Payload FileMaker Actually Built

Here is an excerpt from the successful native Sci-Fi run. The values shown are copied from `FOCUS::g_wv_context_json`; most row objects are omitted so the contract does not consume the rest of the article by attrition.

```jsonc
{
  "__wv": {
    "contract_version": 1,
    "page": 41,
    "page_name": "ranked_list",
    "source": "ranked_views_demo",
    "ts": "8/2/2026 12:02:42 AM"
  },
  "actions": {
    "count": 6,
    "last_type": "ranked.select_movie",
    "status": "Selected native movie MOVIE-51D0E623-D55B-4D32-9191-B20C58243640 | record 17 of 33"
  },
  "ranked_view": {
    "count": 33,
    "current_record_id": "MOVIE-51D0E623-D55B-4D32-9191-B20C58243640",
    "current_record_number": 17,
    "empty_message": "No ranked movies match Sci-Fi.",
    "filter": {
      "genre_id": "GENRE-303185A0-4C08-48BC-95D3-932558B1DF5A",
      "label": "Sci-Fi"
    },
    "native_found_count": 33,
    "rows": [
      {
        "display_title": "AL: Twilight Cargo (2015)",
        "movie_id": "MOVIE-7F59D64D-EADC-40BC-B954-E29394F89802",
        "order": 1,
        "rank": 1,
        "rating": 1499.92455530079,
        "selected": false,
        "year": 2015
      },
      // Rows 2–3 omitted.
      {
        "display_title": "AX: Amber Void (2018)",
        "movie_id": "MOVIE-51D0E623-D55B-4D32-9191-B20C58243640",
        "order": 4,
        "rank": 4,
        "rating": 1499.12197114646,
        "selected": true,
        "year": 2018
      }
      // Rows 5–33 omitted.
    ],
    "selected_movie_id": "MOVIE-51D0E623-D55B-4D32-9191-B20C58243640"
  }
}
```

The full native payload remains visible in the demo. That is important because the JSON is not merely transportation; it is the boundary we can inspect when the native data and rendered rows disagree.

Notice what is not in it. There is no full movie record, no relationship graph, no privilege map, no FileMaker calculation dependency list, and no invitation for JavaScript to reconstruct a found set. The payload is a rendering contract, not a moving van.

## FileMaker Shapes The Native Records

`WV__Demo_Build_Context` has been updated for this pass. It now runs from the `MOVIE`-based `WV Framework - Demo` layout, establishes the ranked native found set, and turns those records into the payload the renderer expects. That keeps record selection, genre filtering, and sort order in FileMaker. The updated builder begins by selecting only the native facts the renderer needs:

```filemaker
Set Variable [ $_rows_text ; Value:
  ...
    ExecuteSQL (
      base &
      "INNER JOIN \"MOVIE_GENRE\" mg ON mg.\"id_movie\" = m.\"ID\" " &
      "WHERE mg.\"id_genre\" = ? " & ordered ;
      Char ( 29 ) ; Char ( 30 ) ; $_genre_id
    )
  ...
]
```

This is FileMaker choosing the records, applying the genre condition, and defining the order. JavaScript receives the result after those decisions. It does not receive table names and a cheerful suggestion to query responsibly.

Note: The literal table and field names keep this example readable. In production code, I would abstract them; hard-coded `ExecuteSQL` references are fragile when schema names change. That is a separate lesson, not an oversight. I don't want to receive calls about this.

The script turns each returned row into a JSON object with a stable id, display value, year, rating, rank, and order:

```filemaker
Set Variable [ $_rows_json ; Value:
  ...
        json = JSONSetElement ( json
          ; [ "[" & i & "].movie_id" ; movie_id ; JSONString ]
          ; [ "[" & i & "].display_title" ; Case ( IsEmpty ( display_title ) ; movie_id ; display_title ) ; JSONString ]
          ; [ "[" & i & "].year" ; year ; JSONNumber ]
          ; [ "[" & i & "].rating" ; rating ; JSONNumber ]
          ; [ "[" & i & "].rank" ; rank ; JSONNumber ]
          ; [ "[" & i & "].order" ; i + 1 ; JSONNumber ]
        ) ;
  ...
]
```

That array alone would be enough to draw rows. It would not be enough to prove a native round trip.

`$_rows_json` is the handoff between the two calculations. Once the first step has built the row array, the builder uses its movie ids to establish the native `MOVIE` found set, resolves and navigates to the selected record, and adds the resulting `selected` value to each row. The final calculation then inserts that completed array into `ranked_view.rows` and adds the native found-set values beside it:

```filemaker
; [ "ranked_view.selected_movie_id" ; $_movie_id ; JSONString ]
; [ "ranked_view.native_found_count" ; Get ( FoundCount ) ; JSONNumber ]
; [ "ranked_view.current_record_number" ; Get ( RecordNumber ) ; JSONNumber ]
; [ "ranked_view.current_record_id" ; GetAsText ( MOVIE::ID ) ; JSONString ]
; [ "ranked_view.rows" ; $_rows_json ; JSONArray ]
```

This is the part that makes the current pass different from the last one. FileMaker is not merely acknowledging an action in a global status field. It is establishing and navigating a real found set, and the layout exposes that native state beside the renderer.

![The native Script Workspace showing the ranked builder's found-set navigation, selected-id reconciliation, row JSON, and final context construction.](<screenshots/05-builder-native.png>)

## Named Modules, Repeated Rows

The cumulative library keeps the eight modules from the two-way demo and adds two:

| Index | Module | Job |
| ---: | --- | --- |
| `41` | `wv.page.ranked.list.html` | assemble the ranked page and show the initial loading state |
| `42` | `wv.renderer.ranked.list.js` | render repeated rows, empty state, selected state, and selection actions |

The exact indexes belong to this demo. The reusable idea is simpler: page `41` declares its platform, action-bridge, and renderer dependencies; the library assembles them; and the renderer remains a named module that can be reviewed or replaced without reopening the whole Web Viewer package.

![The native module inventory with cumulative platform modules 20–25, ranked page 41, ranked renderer 42, and the earlier context page 62/63.](<screenshots/07-module-inventory-native.png>)

Once FileMaker supplies the ordered array, repeated-row rendering is a browser job. The renderer iterates the `ranked_view.rows` array and uses only the contract it received:

```js
rows.forEach(function (record) {
  record = record || {};

  var movieId = value(record.movie_id);
  var row = el(
    "button",
    "wv-ranked-row" + (record.selected === true ? " is-selected" : "")
  );

  row.type = "button";
  row.setAttribute("data-movie-id", movieId);
  ...
  list.appendChild(row);
});
```

JavaScript handles presentation; FileMaker makes the application decisions: which movies belong in the array, their order, and which movie is selected. That division is not a slight against JavaScript. It is a refusal to duplicate FileMaker rules in the one place least able to enforce them.

The page begins with a literal loading state. When context arrives, the renderer replaces it with either the ranked rows or an explicit empty state. The same contract drives loading, empty, populated, and selected presentation; the renderer applies the selected treatment only when FileMaker returns `selected: true` for that record.

![The native FileMaker Web Viewer after the ranked page loads and before context is pushed.](<screenshots/01-ranked-loading-native.png>)

An empty array produces a different, deliberate result:

![The ranked renderer's deliberate empty state in the native FileMaker target.](<screenshots/02-ranked-empty-native.png>)

## The New Work Happens In FileMaker

The row handler does not call `FileMaker.PerformScript` directly. It reuses the `WV.sendAction` door established last round:

```js
row.addEventListener("click", function () {
  ...
  WV.sendAction("ranked.select_movie", { movie_id: movieId }, {
    source: "wv.renderer.ranked.list"
  });
  ...
});
```

The action is `ranked.select_movie`; its payload contains the stable `movie_id`. The envelope machinery is unchanged. The important part is what FileMaker does after receiving it.

The inherited `WV__Demo_Handle_Action` script still checks incoming messages and handles the two demo actions from last round. This pass adds only `ranked.select_movie` and the checks required for it.

FileMaker does not act on the message merely because it is valid JSON. The handler checks that the message came from the expected viewer code, contains the expected action and movie id, and refers to a movie in the ranked collection FileMaker already supplied. Only then does FileMaker navigate.

The page number, module name, and JSON paths are details of this demo. The reusable method is the point: JavaScript reports a narrow user intention, FileMaker validates it against current application state, does the record work, and returns the result.

After validation, FileMaker goes to the first record in the ranked found set, walks forward until `MOVIE::ID` matches the requested id, and writes that native id to `FOCUS::g_wv_demo_movie_id`:

```text
If [ $_ranked_action ]
  Go to Layout [ “WV Framework - Demo” (MOVIE) ]
  Set Variable [ $_nav_index; Value:1 ]
  Go to Record/Request/Page [ First ]
  Loop [ Flush: Always ]
    Exit Loop If [ GetAsText ( MOVIE::ID ) = $_payload_movie_id or
                  $_nav_index >= Get ( FoundCount ) ]
    Go to Record/Request/Page [ Next; Exit after last: Off ]
    Set Variable [ $_nav_index; Value:$_nav_index + 1 ]
  End Loop
  Set Field By Name [ "FOCUS::g_wv_demo_movie_id"; GetAsText ( MOVIE::ID ) ]
End If
```

The resulting status uses the native movie id, record number, and found count. FileMaker then rebuilds context and pushes it back to the viewer. Native navigation can reinitialize the Web Viewer on this teaching layout, so the handler reloads the page when necessary before pushing that context; the exact pause and reload steps remain in the build instructions.

The important sequence is stable even when the loading implementation changes: FileMaker validates, performs the native work, rebuilds its context, and only then returns the selected state.

![The native handler branch showing FileMaker found-set navigation, selected-id update, context rebuild, viewer reload, and acknowledgement push.](<screenshots/06-handler-native.png>)

## Loading Gets Only As Smart As This Surface Justifies

The separate `Build Context`, `Load Web Viewer`, and `Push Context` buttons remain because they let us inspect each boundary independently.

The `Run` path adds one convenience: it tries to push the new context into the existing viewer first and reloads only when the viewer is not ready. The loader reports whether it reloaded, and the layout exposes that result instead of asking the reader to trust invisible recovery.

This is enough intelligence for this pass. The final dirty-token, cache-version, loaded-map, retry, and deployment contract still belongs in `Cache Me If You Can`, after the complete interface exists and there is something worth productionizing.

## Walk Through The Native Round Trip

Open `WV Framework - Demo` in `Flicks_WebViewer_Framework_03_RankedViews.fmp12`.

The Web Viewer object remains `wv_main`. The module index is `41`. The genre field drives the FileMaker query, while the movie id field reflects FileMaker's authoritative selection.

1. Choose `Sci-Fi` and click `Build Context`. FileMaker should establish a 33-record native found set, and `FOCUS::g_wv_context_json` should contain 33 ranked rows. Confirm that `ranked_view.native_found_count` matches the found count and `ranked_view.current_record_id` matches the visible `MOVIE::ID`.
2. Click `Load Web Viewer`. The viewer should show `Loading ranked records…`, while the debug HUD reports that page `41` is loaded and renderer `42` is registered.
3. Click `Push Context`. The loading surface should become the ranked list; its genre, row count, and selected id should match the native payload.
4. Click row `#4`, `AX: Amber Void (2018)`. Inspect `FOCUS::g_wv_action_json` and confirm that `ranked.select_movie` carries the stable id `MOVIE-51D0E623-D55B-4D32-9191-B20C58243640`.

Now watch FileMaker, not just the gold border.

The native layout changes to `AX: Amber Void (2018)`. The visible native id changes to the requested stable id. FileMaker's toolbar moves to record `17 of 33`. The action status says the native movie was selected. After acknowledgement returns, row `#4` receives the selected treatment and the viewer summary reports `native record 17 of 33`.

That is the payoff for this pass. The Web Viewer asked; FileMaker navigated; both surfaces settled on FileMaker's state.

## Debug The Layers Separately

Once native records, JSON, rendering, actions, and acknowledgement are involved, “the Web Viewer is wrong” covers a great deal of territory while locating none of it.

Ask how far the evidence traveled. The same boundaries that make the system modular also tell us where to look when it fails:

| Symptom | Inspect next |
| --- | --- |
| Native found set is wrong | active FileMaker filter, `$_rows_text`, and the count after `Perform Find` |
| Found set is right but JSON is wrong | row and field separators, `$_rows_json`, counts, ids, order, and selected values |
| JSON is right but rows do not appear | rebuilt library, page/renderer registration, and whether `ranked_view.rows` arrived as an array rather than quoted JSON |
| Click does not reach FileMaker | `FOCUS::g_wv_action_json`, then the Web Viewer permission to perform FileMaker scripts |
| FileMaker rejects the id | `payload.movie_id`, the ids in the current `ranked_view.rows`, and the page/source metadata |
| FileMaker navigates but the viewer does not settle | native record position, selected id, rebuilt context, returned `selected` flag, and load/push results |

If the FileMaker found set is wrong, JavaScript is merely displaying the consequences with better typography. If `FOCUS::g_wv_action_json` contains the click, the viewer already delivered it; continue on the FileMaker side. And if that field never changes, check the Web Viewer permission checkbox. It is small. Its capacity for wasting an afternoon remains disproportionately large.

The handler deliberately rejects an id absent from the current ranked collection. A movie can exist in the database and still be invalid for the active view.

## FileMaker Still Owns The Application

FileMaker now owns more visible state than it did last round:

- which records qualify and how they are ordered
- the native found set, current record, and selected movie
- validation of incoming actions
- the context returned to the viewer

JavaScript owns:

- loading, empty, populated, and selected presentation
- repeated-row construction and local click handling
- packaging intent into the documented action call
- rendering the context FileMaker returns

The renderer does not query FileMaker. It does not optimistically keep the clicked row selected as authoritative state. It does not infer that rank `4` means native record `4`. It receives facts, renders them, reports intent, and waits for the next facts.

That arrangement is slightly less magical and considerably more maintainable.

## Where The AI Co-Developer Fits

The ranked renderer is the most substantial AI-assisted JavaScript in the series so far. The useful part is not that an AI can write `rows.forEach`; it is that the request described a narrow, inspectable job:

- input: the documented ranked-row contract
- output: one documented selection action
- authority: none over FileMaker queries or selected state
- presentation: repeated rows with explicit loading, empty, and selected states
- change boundary: the ranked page and renderer modules

Those constraints let us review the result against a contract rather than treating the entire Web Viewer as one opaque deliverable. Next round, we will show that collaboration instead of summarizing it: the prompt, supplied context, first output, review, native FileMaker evidence, and revision loop. The ranked list here is the contract-teaching surface. It is not the visual ceiling.

## Takeaway

Last round proved two-way communication. This pass turns that bridge into a reusable method: FileMaker shapes native records into a contract, named modules render it, JavaScript reports a narrow user intention, and FileMaker validates the request, performs the native work, and returns authoritative state.

The selected Web Viewer row, native movie fields, FileMaker record position, action JSON, and returned context all tell the same story. Because those boundaries are explicit, AI-assisted renderer code has a constrained place to land and evidence against which it can be reviewed. That agreement is the method earning its keep.

Next pass, we use the same custody arrangement to build the full interface: native FileMaker list on one side, richer Web Viewer visualization on the other, and two-way interaction that is worth having a Web Viewer for.
