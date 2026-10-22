# Changelog

## [3.0.0](https://github.com/togethercomputer/together-py/compare/v2.42.0...v3.0.0) (2026-10-22)


### ⚠ BREAKING CHANGES

* **cli:** drop --remediation-id from remediations create ([#656](https://github.com/togethercomputer/together-py/issues/656))
* **sdk:** Remove RL import shim ([#184](https://github.com/togethercomputer/together-py/issues/184))
* **cli:** Promote `beta models` commands out of beta, superseding prior `models` commands ([#186](https://github.com/togethercomputer/together-py/issues/186))

### Features

* **cli:** Promote `beta models` commands out of beta, superseding prior `models` commands ([#186](https://github.com/togethercomputer/together-py/issues/186)) ([a5adc8b](https://github.com/togethercomputer/together-py/commit/a5adc8bae542dc0d350030a92cd4ab9a52e14f55))


### Bug Fixes

* **cli:** drop --remediation-id from remediations create ([#656](https://github.com/togethercomputer/together-py/issues/656)) ([0c42c12](https://github.com/togethercomputer/together-py/commit/0c42c127ecc9dacf2445601ed298de949848fc3f))
* **devcontainer:** move to Debian trixie base with updated ca-certificates (CVE-2026-111943) ([#657](https://github.com/togethercomputer/together-py/issues/657)) ([21b8d3c](https://github.com/togethercomputer/together-py/commit/21b8d3c68ed673f37b78e0481eb0feb5e7d1f7e1))
* **security:** bump certifi to 2026.10.19 and uv to 0.13.4 (CVE-2026-111943) ([#655](https://github.com/togethercomputer/together-py/issues/655)) ([8847d5e](https://github.com/togethercomputer/together-py/commit/8847d5ed5e6c233fb0b0d7cc3fcdc068c492e94b))


### Chores

* **chat.completions:** Fix named exports sdk generation ([951ac21](https://github.com/togethercomputer/together-py/commit/951ac2104f0357513e986e40636632c5d0adbfe5))
* drop unused remediation_id from create remediation ([0f527d7](https://github.com/togethercomputer/together-py/commit/0f527d76c9217801d1d87b8e109277ed682ce70f))
* Fix CLI ft downloading missing url path updates ([#190](https://github.com/togethercomputer/together-py/issues/190)) ([46e1f15](https://github.com/togethercomputer/together-py/commit/46e1f15aca922ab68b36a50258c89c27185e98dd))
* **internals:** Update various internals from the recent changes ([#187](https://github.com/togethercomputer/together-py/issues/187)) ([1db23e6](https://github.com/togethercomputer/together-py/commit/1db23e639b2e06377d5fa4cbd39cc02e03a816d4))
* Move post_training SDK code location ([#191](https://github.com/togethercomputer/together-py/issues/191)) ([cebbce0](https://github.com/togethercomputer/together-py/commit/cebbce06beb830623ff8bcc7c81c16fc4cb6fe44))
* **sdk:** Remove RL import shim ([#184](https://github.com/togethercomputer/together-py/issues/184)) ([b383e36](https://github.com/togethercomputer/together-py/commit/b383e362e873a7e34b12cd489121b837142d0c6e))
* **stlc:** resolve custom-code integrate conflicts for trunk generate ([#189](https://github.com/togethercomputer/together-py/issues/189)) ([e0d4c23](https://github.com/togethercomputer/together-py/commit/e0d4c239bd1298bd3b0ced6bd92eaa83df95781b))
