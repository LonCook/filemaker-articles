# Shared Web Viewer Library

These platform modules are byte-identical in the final Article 2 and Article 3 exports and the Article 4 development export. They are the canonical shared copies used by the cumulative demos.

Load them in this order:

1. [`wv.platform.base.html`](wv.platform.base.html) establishes the base document shell.
2. [`wv.platform.base.css`](wv.platform.base.css) provides shared tokens and base visualization styles.
3. [`wv.platform.runtime.js`](wv.platform.runtime.js) creates the `WV` runtime and renderer registration surface.
4. [`wv.platform.context.js`](wv.platform.context.js) receives and normalizes FileMaker context.
5. [`wv.platform.boot.js`](wv.platform.boot.js) coordinates startup and loading state.
6. [`wv.platform.actions.js`](wv.platform.actions.js) provides the public `WV.sendAction` bridge introduced in Article 2.

Article 1 uses modules 20 through 24. Articles 2 through 4 use all six. Page and renderer modules remain with the article that introduced them.

