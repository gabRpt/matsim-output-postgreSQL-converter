# How to maintain this documentation

The documentation is written in [Markdown](https://en.wikipedia.org/wiki/Markdown) and is built using [HonKit](https://honkit.netlify.app/). The documentation is hosted on [GitHub Pages](https://pages.github.com/).

* First install HonKit following the [installation guide](https://honkit.netlify.app/setup.html).

* Then, in the `docs` folder at the root of the project, run `npx honkit serve` to build the documentation and serve it locally. The changes will be automatically updated in the browser.

* Do your changes by editing the Markdown files in the `docs` folder.

* To build the documentation, run `npx honkit build` in the `docs` folder. The documentation will be built in the `_book` folder.

* Replace the html and json files in the `docs` folder with the html files in the `_book` folder. Do se same with gitbook folder.

* Commit and push the changes.
