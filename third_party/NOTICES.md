# Third-party dependency provenance

`conda-packages.json` identifies the 116 packages in the build environment, including package URLs and SHA-256 values. `conda/` preserves the corresponding conda-forge recipes and the license files present in those packages. The package hashes were checked against the downloaded archives; the explicit environment install itself did not independently verify the hashes against a signed manifest.

Four environment packages did not contain an `info/licenses` directory: `libgcc`, `libgfortran`, `libgfortran5`, and `libsqlite`. Consult their retained recipes and upstream terms. SQLite's official copyright statement is at <https://www.sqlite.org/copyright.html>.

The project's source and components carry their own terms, including `source/iio-emu/LICENSE_ADIBSD`. Consult `native/source-lock.json` for exact source revisions and `native/libsigrokdecode-arm64.patch` for local changes.

This inventory is preparation for an audit; it is not a determination that a particular binary release satisfies all redistribution conditions.
