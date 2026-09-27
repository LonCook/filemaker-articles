# Initial Prompt

Using the full source and manifest in this evidence packet, propose modules `43` and `44` for the hybrid interface described in `01-human-brief.md`.

Return complete page and renderer module source. Do not modify FileMaker scripts yet.

Requirements:

- Use only the supplied `ranked_view.rows` and returned FileMaker context.
- Render an accessible SVG rating histogram, selected-movie focus marker, and contiguous rating-band interaction.
- Derive bins honestly from the supplied real rows. An empty array produces an explicit empty state.
- Send only the three allowed `hybrid.*` actions through `WV.sendAction`.
- Do not call `FileMaker.PerformScript` directly.
- Do not keep authoritative selected movie or rating band state in JavaScript; context from FileMaker wins on every render.
- Preserve hover and in-flight drag state only.
- Include loading, empty, error, selected, and filtered treatments.
- Declare exact module dependencies and exports in the headers.
- Do not import production module `66`, movers, layered surfaces, camera behavior, synthetic defaults, production reducers, or cache/deployment code.

Stop after returning the two proposed modules. They will be reviewed before integration.

