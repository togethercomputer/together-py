# Changelog

## 2.0.0-alpha.18 (2026-01-31)

Full Changelog: [v2.0.0-alpha.17...v2.0.0-alpha.18](https://github.com/togethercomputer/together-py/compare/v2.0.0-alpha.17...v2.0.0-alpha.18)

### Features

* Add chat completion support for reasoning.enabled ([7fba349](https://github.com/togethercomputer/together-py/commit/7fba349c1bde34ace5ca38c0728479f054518e04))
* **api:** Add API for listing deployments ([298d447](https://github.com/togethercomputer/together-py/commit/298d4475208fb24e1373fa7449c0716768d5501d))
* **api:** Add beta sdks for jig features ([c3ac883](https://github.com/togethercomputer/together-py/commit/c3ac883f8ffe62d2c1b660e3a62fc82891e63dac))
* **api:** Move jobs apis to nest under model uploads per their use case ([368c003](https://github.com/togethercomputer/together-py/commit/368c003ec61e8cea2ec995ba9889d3cf7ac21328))
* **api:** Move queue out of jig namespace ([ebc1498](https://github.com/togethercomputer/together-py/commit/ebc1498125e7b95f2726cfb37a4324aadcf40f8d))
* **api:** Update Jig types and add retrieve_logs api to jig ([76a3c1a](https://github.com/togethercomputer/together-py/commit/76a3c1abccf8bb1efaebd192a68fe31785b568cf))
* **cli:** enhance hardware command to display availability status ([#223](https://github.com/togethercomputer/together-py/issues/223)) ([e7cf8a3](https://github.com/togethercomputer/together-py/commit/e7cf8a30c6a1d46f10ea5049f51e969be6f8418f))
* **client:** add custom JSON encoder for extended type support ([036a0ea](https://github.com/togethercomputer/together-py/commit/036a0eaba07c3cca56e9dbec965e1cce2f8b848a))
* internal: Update to new cluster api routing ([54af0bd](https://github.com/togethercomputer/together-py/commit/54af0bdf4076e5ff02f0475547a4b1d2f7393c46))
* move byoc features under /deployments route ([d70e2e9](https://github.com/togethercomputer/together-py/commit/d70e2e9c3c12997935a34cb4a63a26e315e0c799))


### Bug Fixes

* Avoid crashing when uploading a model which weights already exist ([#226](https://github.com/togethercomputer/together-py/issues/226)) ([5a9095c](https://github.com/togethercomputer/together-py/commit/5a9095c91da5de8333e366e88f6960b428177d07))


### Chores

* **api:** Improve type names for jig volumes and logs ([b256c61](https://github.com/togethercomputer/together-py/commit/b256c61f601d67a0abee1dbc44e9851d52014d0d))
* **api:** Move Queue SDK methods into Jig namespace ([43179e1](https://github.com/togethercomputer/together-py/commit/43179e1ee8451cc3bcb8430c2bc35148309b82db))
* **api:** Rename jig queue apis ([4b466d6](https://github.com/togethercomputer/together-py/commit/4b466d6079071fd840880337b20c4d34a3a5cf45))
* **ci:** upgrade `actions/github-script` ([c8668a1](https://github.com/togethercomputer/together-py/commit/c8668a1424fbfcd37d893d414d4dcd0307f5aac4))


### Documentation

* **axle-queue:** added axle-queue endpoints ([4e60b09](https://github.com/togethercomputer/together-py/commit/4e60b096128cbfef4769195a9b00cf0236e5052c))

## 2.0.0-alpha.17 (2026-01-21)

Full Changelog: [v2.0.0-alpha.16...v2.0.0-alpha.17](https://github.com/togethercomputer/together-py/compare/v2.0.0-alpha.16...v2.0.0-alpha.17)

### Features

* **cli:** add b200 and h200 GPU options for endpoint creation ([#218](https://github.com/togethercomputer/together-py/issues/218)) ([b514912](https://github.com/togethercomputer/together-py/commit/b514912a281922fefbf8a9f62b936ed1de243718))
* Improve usage of models list cli command ([#216](https://github.com/togethercomputer/together-py/issues/216)) ([430e6c1](https://github.com/togethercomputer/together-py/commit/430e6c1e030749be474f020b677d91014ba4482c))


### Chores

* Deprecate CLI usage for endpoints create flag --no-promopt-cache ([#219](https://github.com/togethercomputer/together-py/issues/219)) ([55e9700](https://github.com/togethercomputer/together-py/commit/55e9700187b42f8baff6f567a3a657b46577ed88))
* Mark disable_prompt_cache as deprecated for endpoint creation ([6a629b2](https://github.com/togethercomputer/together-py/commit/6a629b29e53b4374503d30ca75456184ef313b67))

## 2.0.0-alpha.16 (2026-01-18)

Full Changelog: [v2.0.0-alpha.15...v2.0.0-alpha.16](https://github.com/togethercomputer/together-py/compare/v2.0.0-alpha.15...v2.0.0-alpha.16)

### Features

* Add backwards compatible support for google colab api keys ([#211](https://github.com/togethercomputer/together-py/issues/211)) ([80dacca](https://github.com/togethercomputer/together-py/commit/80daccafb4ef69438be1d98773fe3a31ac09cace))
* Add together clusters get-credentials CLI command ([#208](https://github.com/togethercomputer/together-py/issues/208)) ([fa54aa9](https://github.com/togethercomputer/together-py/commit/fa54aa9646e9dab2822491473856f64d5cf4688f))
* **client:** add support for binary request streaming ([8464e12](https://github.com/togethercomputer/together-py/commit/8464e12187b42ff3a58c82ca55ec284ffa98aeea))


### Chores

* Add code samples and descriptions to instant cluster apis ([e1ad614](https://github.com/togethercomputer/together-py/commit/e1ad614f8c3189ddc991fab96013cf5f7aace1d8))
* Improve example script ([#213](https://github.com/togethercomputer/together-py/issues/213)) ([7839058](https://github.com/togethercomputer/together-py/commit/783905873500e3228837e2cf87ebc097d9026539))
* **internal:** update `actions/checkout` version ([dc0819c](https://github.com/togethercomputer/together-py/commit/dc0819c95429f69bf0d7ef442b7b1ea811ec40b5))
* Port tokenize_data example ([#209](https://github.com/togethercomputer/together-py/issues/209)) ([f2714a8](https://github.com/togethercomputer/together-py/commit/f2714a84f2802989a8f519c21e5c62e9fc787038))
* Update cluster apis to reflect their new response shape ([6be132b](https://github.com/togethercomputer/together-py/commit/6be132b210973e9c26beedd0080039e28e522096))

## 2.0.0-alpha.15 (2026-01-09)

Full Changelog: [v2.0.0-alpha.14...v2.0.0-alpha.15](https://github.com/togethercomputer/together-py/compare/v2.0.0-alpha.14...v2.0.0-alpha.15)

### Features

* Add started_at timestamp to fix time estimation ([92ce60d](https://github.com/togethercomputer/together-py/commit/92ce60dd081700c1ef804dc7ad581a4fcf5d81a0))


### Chores

* **api:** Remove APIs that were accidentally added in the wrong namespace ([0425f14](https://github.com/togethercomputer/together-py/commit/0425f14f7598fe3065d6f26c0ae3b577149798b0))
* Minimize breaking changes on common import paths and alias names ([#206](https://github.com/togethercomputer/together-py/issues/206)) ([e677e60](https://github.com/togethercomputer/together-py/commit/e677e6038ee662d79f9a5f0bbf5452843ea37782))
* Update README for clusters CLI commands ([aeaf53a](https://github.com/togethercomputer/together-py/commit/aeaf53a4825376d4aad59c9a70efd0b26a3e1aab))

## 2.0.0-alpha.14 (2026-01-06)

Full Changelog: [v2.0.0-alpha.13...v2.0.0-alpha.14](https://github.com/togethercomputer/together-py/compare/v2.0.0-alpha.13...v2.0.0-alpha.14)

### Chores

* Add Instant Clusters to OpenAPI spec ([2583943](https://github.com/togethercomputer/together-py/commit/25839431e9d7636e3cb2e1b14b8eaeeac179dda5))

## 2.0.0-alpha.13 (2026-01-06)

Full Changelog: [v2.0.0-alpha.12...v2.0.0-alpha.13](https://github.com/togethercomputer/together-py/compare/v2.0.0-alpha.12...v2.0.0-alpha.13)

### Features

* Add compliance and chat_template_kwargs to chat completions spec ([e6fed17](https://github.com/togethercomputer/together-py/commit/e6fed17708d9c58b30f7c46279fae8be3e143e8d))

## 2.0.0-alpha.12 (2026-01-05)

Full Changelog: [v2.0.0-alpha.11...v2.0.0-alpha.12](https://github.com/togethercomputer/together-py/compare/v2.0.0-alpha.11...v2.0.0-alpha.12)

### Features

* Support VLM finetuning ([e4428b3](https://github.com/togethercomputer/together-py/commit/e4428b3c86080286643b0e287ff02ac6b8cd3864))
* VLM Support update ([97c74a3](https://github.com/togethercomputer/together-py/commit/97c74a38da1ea0a7717b0172f5cd65bb85bcaee4))


### Bug Fixes

* use async_to_httpx_files in patch method ([dc293e6](https://github.com/togethercomputer/together-py/commit/dc293e68b49cce5b0c8437e94152e369bb09b625))


### Chores

* **internal:** add `--fix` argument to lint script ([c29463d](https://github.com/togethercomputer/together-py/commit/c29463dbe8a18fa02bf436ae4cbdd6b59644e641))
* **internal:** codegen related update ([f7499fc](https://github.com/togethercomputer/together-py/commit/f7499fcd931834fcd16210cd25e14dc5b328fb0e))


### Documentation

* add more examples ([a048344](https://github.com/togethercomputer/together-py/commit/a048344c0daeeab4d7fefd41d3554bde860dd9d5))

## 2.0.0-alpha.11 (2025-12-16)

Full Changelog: [v2.0.0-alpha.10...v2.0.0-alpha.11](https://github.com/togethercomputer/together-py/compare/v2.0.0-alpha.10...v2.0.0-alpha.11)

### Features

* **api:** api update ([17ad3ec](https://github.com/togethercomputer/together-py/commit/17ad3ec91a06a7e886252d4b688c3a9e217a3799))
* **api:** api update ([ebc3414](https://github.com/togethercomputer/together-py/commit/ebc3414e28db0309fef5aeed456e242048b5d13c))
* **files:** add support for string alternative to file upload type ([db59ed6](https://github.com/togethercomputer/together-py/commit/db59ed6235f2e18db100a72084c2fefc22354d15))


### Chores

* **internal:** add missing files argument to base client ([6977285](https://github.com/togethercomputer/together-py/commit/69772856908b8378c74eed382735523e91011d90))

## 2.0.0-alpha.10 (2025-12-15)

Full Changelog: [v2.0.0-alpha.9...v2.0.0-alpha.10](https://github.com/togethercomputer/together-py/compare/v2.0.0-alpha.9...v2.0.0-alpha.10)

### Features

* **api:** Add fine_tuning.estimate_price api ([1582cc4](https://github.com/togethercomputer/together-py/commit/1582cc498e17562a3a23ae5120dfff2d39ae1e41))
* **api:** api update ([5341347](https://github.com/togethercomputer/together-py/commit/53413475daeeec382968407d47688cf7926f643c))
* **api:** api update ([96fc9b3](https://github.com/togethercomputer/together-py/commit/96fc9b3b1218bcf0c8dd13a28b8eab5c9690c6fd))
* **api:** api update ([e5cfa45](https://github.com/togethercomputer/together-py/commit/e5cfa45f476c77965a9249e9ae41b55b029abfaa))


### Bug Fixes

* **types:** allow pyright to infer TypedDict types within SequenceNotStr ([048f2b7](https://github.com/togethercomputer/together-py/commit/048f2b7d347aa2ab09a4b49c2770cbf15a70c3e4))


### Chores

* add missing docstrings ([a1c8329](https://github.com/togethercomputer/together-py/commit/a1c8329a0c2562bcdbd22c262eb7a995bfbd0deb))
* **internal:** avoid using unstable Python versions in tests ([6268112](https://github.com/togethercomputer/together-py/commit/62681124a807a4f718e1711039242d2b9037e33b))
* Update model list CLI to use api parameter for dedicated filtering ([#195](https://github.com/togethercomputer/together-py/issues/195)) ([95cc672](https://github.com/togethercomputer/together-py/commit/95cc672583e2a908f54dd557cd0f22465da26a4b))

## 2.0.0-alpha.9 (2025-12-03)

Full Changelog: [v2.0.0-alpha.8...v2.0.0-alpha.9](https://github.com/togethercomputer/together-py/compare/v2.0.0-alpha.8...v2.0.0-alpha.9)

### Features

* **api:** api update ([fa5e6f3](https://github.com/togethercomputer/together-py/commit/fa5e6f3eb27475ac2e377bbea9150d45bf4e141e))
* **api:** api update ([236996f](https://github.com/togethercomputer/together-py/commit/236996f0eba5c0a33d2da59b438a830684e89192))


### Bug Fixes

* ensure streams are always closed ([db990c7](https://github.com/togethercomputer/together-py/commit/db990c744ebfffcfe48f52dc44b1ca7b47f1f79a))


### Chores

* bump required `uv` version ([1dfec56](https://github.com/togethercomputer/together-py/commit/1dfec5659c5a8e6c8abc7a1035d602a3e47ff67a))
* **deps:** mypy 1.18.1 has a regression, pin to 1.17 ([2235b95](https://github.com/togethercomputer/together-py/commit/2235b95d3e8dc11c9edc308e2b4b69b1463d21cb))
* **docs:** use environment variables for authentication in code snippets ([051c1b4](https://github.com/togethercomputer/together-py/commit/051c1b489cb80ded1ad60f6b8722512dd2efae3f))
* fix internal type issues ([4a2b0f1](https://github.com/togethercomputer/together-py/commit/4a2b0f1cfebc013102e21d54318269a0fe037b7a))
* update lockfile ([e93c953](https://github.com/togethercomputer/together-py/commit/e93c95338756fb37f279aec946d0c5f74cf22877))

## 2.0.0-alpha.8 (2025-11-26)

Full Changelog: [v2.0.0-alpha.7...v2.0.0-alpha.8](https://github.com/togethercomputer/together-py/compare/v2.0.0-alpha.7...v2.0.0-alpha.8)

### Features

* **api:** api update ([49bb5d4](https://github.com/togethercomputer/together-py/commit/49bb5d4ba69ca118ecc34be2d69c4253665e2e81))
* **api:** Fix internal references for VideoJob spec ([fb5e7bb](https://github.com/togethercomputer/together-py/commit/fb5e7bb3dbaa9427d291de7440c201529b6cf528))


### Bug Fixes

* Address incorrect logic for `endpoint [command] --wait false` logic ([31236a9](https://github.com/togethercomputer/together-py/commit/31236a9df29c22fe7444c2dbb0d4bfc518bc79aa))


### Chores

* Remove incorrect file upload docs ([5bb847e](https://github.com/togethercomputer/together-py/commit/5bb847e33b55e5d0978c742e86cf931a2c08f919))
* Remove incorrect file upload docs ([bb97093](https://github.com/togethercomputer/together-py/commit/bb970938650b6f9580538528979221d142f74b6a))

## 2.0.0-alpha.7 (2025-11-26)

Full Changelog: [v2.0.0-alpha.6...v2.0.0-alpha.7](https://github.com/togethercomputer/together-py/compare/v2.0.0-alpha.6...v2.0.0-alpha.7)

### Bug Fixes

* include rich in package dependencies ([9c9c5fc](https://github.com/togethercomputer/together-py/commit/9c9c5fcc29183e1598418684391b480d4052c9b9))

## 2.0.0-alpha.6 (2025-11-25)

Full Changelog: [v2.0.0-alpha.5...v2.0.0-alpha.6](https://github.com/togethercomputer/together-py/compare/v2.0.0-alpha.5...v2.0.0-alpha.6)

### Chores

* **api:** Cleanup some exported types ([bf57f0d](https://github.com/togethercomputer/together-py/commit/bf57f0d49619651e96565d99a9291aa55873e4f0))
* fix lint and type checks ([#186](https://github.com/togethercomputer/together-py/issues/186)) ([7184b72](https://github.com/togethercomputer/together-py/commit/7184b72f79aa2b255a0921f5fc4680e75f0d8847))

## 2.0.0-alpha.5 (2025-11-25)

Full Changelog: [v2.0.0-alpha.4...v2.0.0-alpha.5](https://github.com/togethercomputer/together-py/compare/v2.0.0-alpha.4...v2.0.0-alpha.5)

### Features

* **api:** manual updates ([f1b27a5](https://github.com/togethercomputer/together-py/commit/f1b27a53efeb925b6b89d3f7636c4809814347d8))


### Bug Fixes

* uv v0.8.11 only has python 3.14rc, which causes issues with pydantic 2 ([981828a](https://github.com/togethercomputer/together-py/commit/981828a2f70db44845e6a1ae93d1906269d7ba5f))


### Chores

* **internal:** working around mypy ([7d080fc](https://github.com/togethercomputer/together-py/commit/7d080fc748da2cf3293ddfa5b74b23e47213c77f))

## 2.0.0-alpha.4 (2025-11-24)

Full Changelog: [v2.0.0-alpha.3...v2.0.0-alpha.4](https://github.com/togethercomputer/together-py/compare/v2.0.0-alpha.3...v2.0.0-alpha.4)

### Chores

* Run bootstrap on codebase ([399a559](https://github.com/togethercomputer/together-py/commit/399a55971beaf5f42f6bacd426996f8049f36441))

## 2.0.0-alpha.3 (2025-11-24)

Full Changelog: [v2.0.0-alpha.2...v2.0.0-alpha.3](https://github.com/togethercomputer/together-py/compare/v2.0.0-alpha.2...v2.0.0-alpha.3)

### Features

* **api:** update via SDK Studio ([79346e8](https://github.com/togethercomputer/together-py/commit/79346e8254761d5f8059d0451c0cd3af7fa96aac))


### Chores

* **internal:** codegen related update ([ae73675](https://github.com/togethercomputer/together-py/commit/ae73675ce207c9c5304f1b77d74800fae673d53f))

## 2.0.0-alpha.2 (2025-11-21)

Full Changelog: [v2.0.0-alpha.1...v2.0.0-alpha.2](https://github.com/togethercomputer/together-py/compare/v2.0.0-alpha.1...v2.0.0-alpha.2)

### ⚠ BREAKING CHANGES

* **api:** Change call signature for `audio.create` to `audio.speech.create` to match spec with python library and add space for future APIs

### Features

* **api:** api update ([9d5e1a2](https://github.com/togethercomputer/together-py/commit/9d5e1a2a8fe09f01ac9ed984361139064d42a2d8))
* **api:** Change TTS call signature ([251c911](https://github.com/togethercomputer/together-py/commit/251c911e4b6562fb1751ae2a880e7ff6bb2e7bd2))

## 2.0.0-alpha.1 (2025-11-21)

Full Changelog: [v0.1.0-alpha.28...v2.0.0-alpha.1](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.28...v2.0.0-alpha.1)

### ⚠ BREAKING CHANGES

* **api:** Update method signature for reranking to `rerank.create()`
* **api:** Change Fine Tuning method name from `download()` to `content()` to align with other namespaces
* **api:** For the TS SDK the `images.create` is now `images.generate`

### Features

* **api:** api update ([921fa59](https://github.com/togethercomputer/together-py/commit/921fa591a5a9c70f96d457a7b59749dfdfb6d4d6))
* **api:** Change fine tuning download method to `.create` ([aa27907](https://github.com/togethercomputer/together-py/commit/aa279076c524956e204cb68b7424048a4f93a17d))
* **api:** Change image creation signature to `images.generate` ([a6e3ad7](https://github.com/togethercomputer/together-py/commit/a6e3ad792393be978b123c87707afe779ef8df34))
* **api:** Change rerank method signature ([338c415](https://github.com/togethercomputer/together-py/commit/338c415d1cee04520413717ee821f47a64316211))
* **api:** Port finetuning create code from together-python ([#176](https://github.com/togethercomputer/together-py/issues/176)) ([ef3bd52](https://github.com/togethercomputer/together-py/commit/ef3bd5245ee254269653ff8e6db1651cfcf89c6d))


### Chores

* **api:** Remove auto-generated fine_tuning.create method from Python SDK ([c533f29](https://github.com/togethercomputer/together-py/commit/c533f29e2b94d5d9ca97ed50c181dae0fc2dcd7b))
* Fix examples ([35422cb](https://github.com/togethercomputer/together-py/commit/35422cb1eef730a04117d83c8df08442461f5ec1))

## 0.1.0-alpha.28 (2025-11-18)

Full Changelog: [v0.1.0-alpha.27...v0.1.0-alpha.28](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.27...v0.1.0-alpha.28)

### Features

* **api:** api update ([c854d7d](https://github.com/togethercomputer/together-py/commit/c854d7d032e64c4d7068ceffa3af38824b4a9e25))
* **api:** file upload method signature and functionality match previ… ([#174](https://github.com/togethercomputer/together-py/issues/174)) ([e2a19ca](https://github.com/togethercomputer/together-py/commit/e2a19ca87c3e6698155cfa9874f588c1906f3744))


### Chores

* **api:** Remove auto-generated files upload API to support custom coded version ([d6c9c59](https://github.com/togethercomputer/together-py/commit/d6c9c59b9549fa29401ea2016c6b97869d0ec21b))

## 0.1.0-alpha.27 (2025-11-14)

Full Changelog: [v0.1.0-alpha.26...v0.1.0-alpha.27](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.26...v0.1.0-alpha.27)

### Features

* **api:** Add batches.cancel API ([c0e615b](https://github.com/togethercomputer/together-py/commit/c0e615bada270d973e662a263cd23a35eb19b171))

## 0.1.0-alpha.26 (2025-11-14)

Full Changelog: [v0.1.0-alpha.25...v0.1.0-alpha.26](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.25...v0.1.0-alpha.26)

### ⚠ BREAKING CHANGES

* **api:** Access to the api for listing checkpoints has changed its name to `list_checkpoints`
* **api:** Access to fine tuning APIs namespace has changed from `fine_tune` to `fine_tuning`

### Features

* **api:** Add audio.voices.list sdk ([f81ec92](https://github.com/togethercomputer/together-py/commit/f81ec926febfd802d31c98e32b98cdb2ec87926c))


### Styles

* **api:** Change fine tuning method `retrieve_checkpoints` to `list_checkpoints` ([131ebfe](https://github.com/togethercomputer/together-py/commit/131ebfe73729265f057a183e5fa2e3b86890e01f))
* **api:** Change fine tuning namespace to `fine_tuning` ([52288c9](https://github.com/togethercomputer/together-py/commit/52288c97f8a5aedcf07e7f5afa96fb775ed5d1fc))

## 0.1.0-alpha.25 (2025-11-13)

Full Changelog: [v0.1.0-alpha.24...v0.1.0-alpha.25](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.24...v0.1.0-alpha.25)

### Bug Fixes

* Add CLI support for endpoings list --mine and --usage-type ([54b81f1](https://github.com/togethercomputer/together-py/commit/54b81f11597b7f94e4c9db613ab6f08b016ebfbf))
* Remove unnecessary logic require endpoints cli to have both min/max replicas provided together ([12a5fc1](https://github.com/togethercomputer/together-py/commit/12a5fc1f6cb5e692a2da9d5f4c01b2162d641191))

## 0.1.0-alpha.24 (2025-11-12)

Full Changelog: [v0.1.0-alpha.23...v0.1.0-alpha.24](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.23...v0.1.0-alpha.24)

### Features

* **api:** api update ([0bd2950](https://github.com/togethercomputer/together-py/commit/0bd2950b229ea5801bec74e568053eea46dc4d58))

## 0.1.0-alpha.23 (2025-11-12)

Full Changelog: [v0.1.0-alpha.22...v0.1.0-alpha.23](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.22...v0.1.0-alpha.23)

### Features

* **api:** Add endpoints.list_avzones ([9492e97](https://github.com/togethercomputer/together-py/commit/9492e9766862834c7e905d545e205f730a5feb14))

## 0.1.0-alpha.22 (2025-11-12)

Full Changelog: [v0.1.0-alpha.21...v0.1.0-alpha.22](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.21...v0.1.0-alpha.22)

### Features

* **api:** api update ([360eb81](https://github.com/togethercomputer/together-py/commit/360eb813c52d05ed12aa2778a07232707036c69d))

## 0.1.0-alpha.21 (2025-11-11)

Full Changelog: [v0.1.0-alpha.20...v0.1.0-alpha.21](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.20...v0.1.0-alpha.21)

### Features

* **api:** api update ([c80ecd4](https://github.com/togethercomputer/together-py/commit/c80ecd47aa3324017c3674f9e3fd34ab11685047))
* **api:** api update ([e61ccab](https://github.com/togethercomputer/together-py/commit/e61ccab3e3e81c33149c2ce72d8ea85b364ce9b3))
* **api:** api update ([2468e28](https://github.com/togethercomputer/together-py/commit/2468e287f223e58aa0d851817895785ca1cef13b))
* **api:** Update Eval APIs ([c222457](https://github.com/togethercomputer/together-py/commit/c222457e71f6a9db507c407f08d828ff24e352b1))


### Bug Fixes

* **compat:** update signatures of `model_dump` and `model_dump_json` for Pydantic v1 ([f3a2627](https://github.com/togethercomputer/together-py/commit/f3a2627c19b2249d88daa2f9a37eb3b5492c3b52))

## 0.1.0-alpha.20 (2025-11-10)

Full Changelog: [v0.1.0-alpha.19...v0.1.0-alpha.20](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.19...v0.1.0-alpha.20)

### Features

* **api:** manual updates ([8654003](https://github.com/togethercomputer/together-py/commit/8654003b2288c8f91efb7cd5e3ae7c7d5d3b2ed1))

## 0.1.0-alpha.19 (2025-11-10)

Full Changelog: [v0.1.0-alpha.18...v0.1.0-alpha.19](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.18...v0.1.0-alpha.19)

### ⚠ BREAKING CHANGES

* **api:** The default max retries for api calls has changed from 5 to 2. This may result in more frequent non-200 responses.

### Features

* **api:** Add fine_tune.delete API ([bc935ae](https://github.com/togethercomputer/together-py/commit/bc935ae8fb20e008a8581fe9532c2f2dba052cc5))
* **api:** Add Video APIs ([0e4b013](https://github.com/togethercomputer/together-py/commit/0e4b013607b6c8837772b94e7abe04ff5cf0a945))
* **api:** api update ([bede2e9](https://github.com/togethercomputer/together-py/commit/bede2e9c93d11fc015326a480791a2a477fe3f5f))
* **api:** api update ([fc55c21](https://github.com/togethercomputer/together-py/commit/fc55c21ebe3a874c7df3247c949d93f47eee15a1))
* **api:** api update ([27a68fe](https://github.com/togethercomputer/together-py/commit/27a68feb1d4abb65b1bbc8268c0e2cc6639843ea))
* **api:** api update ([4c03db5](https://github.com/togethercomputer/together-py/commit/4c03db5279ec649d74509de37826fe15f70c4ccb))
* **api:** api update ([828c879](https://github.com/togethercomputer/together-py/commit/828c8790ba68175880fc8899e6f4d3343fb77efc))
* **api:** api update ([5225475](https://github.com/togethercomputer/together-py/commit/5225475f361176f3b5a8cc0375490cb6bab8578f))
* **api:** api update ([23cc181](https://github.com/togethercomputer/together-py/commit/23cc181522f5921905b8fe5cbf244dff7fd9a848))
* **api:** api update ([8777e19](https://github.com/togethercomputer/together-py/commit/8777e197d81964b6d0eae39f5ff390c5862aece4))
* **api:** Change the default max retries from 5 to 2 ([f4948c0](https://github.com/togethercomputer/together-py/commit/f4948c0f88558047ad39cf039c545ee73cd2bf59))
* **api:** manual updates ([ab62050](https://github.com/togethercomputer/together-py/commit/ab620506058c338e19e564dfab3e8344d673813e))
* **api:** manual updates ([a129515](https://github.com/togethercomputer/together-py/commit/a1295156330d815c0749cf14d1dd84339292c2c6))
* **api:** manual updates ([f51d284](https://github.com/togethercomputer/together-py/commit/f51d284e2aa3592574ec4416d526bf581574ebe6))
* **api:** manual updates ([cd3c514](https://github.com/togethercomputer/together-py/commit/cd3c514e7572d5ad0b889fb5dff97c4901854715))
* **api:** Rename evaluation sdks to evals ([9163ca7](https://github.com/togethercomputer/together-py/commit/9163ca78c42c421c5de732bb54cd30578aeb3e77))


### Bug Fixes

* **client:** close streams without requiring full consumption ([298c565](https://github.com/togethercomputer/together-py/commit/298c565cec79e666da10c7b64af7eb3964f62668))
* compat with Python 3.14 ([274f25d](https://github.com/togethercomputer/together-py/commit/274f25de691bfb4ec0bc2b4a7626c647e87996b8))


### Chores

* bump `httpx-aiohttp` version to 0.1.9 ([18e2050](https://github.com/togethercomputer/together-py/commit/18e2050b0de8bc897c9b818553b84d0685a03ba5))
* do not install brew dependencies in ./scripts/bootstrap by default ([af4299a](https://github.com/togethercomputer/together-py/commit/af4299aa1f5cc9eba0183267d51e9ff5e49e1e98))
* improve example values ([0855619](https://github.com/togethercomputer/together-py/commit/08556197407d5323431ed040dd58c46b657ff993))
* **internal/tests:** avoid race condition with implicit client cleanup ([cc6a071](https://github.com/togethercomputer/together-py/commit/cc6a0712fc81aeefae07a4149ffc493e18811b01))
* **internal:** detect missing future annotations with ruff ([d33b041](https://github.com/togethercomputer/together-py/commit/d33b0419d5db8a5ba094821bcbcc94785e7ff829))
* **internal:** grammar fix (it's -&gt; its) ([57b735a](https://github.com/togethercomputer/together-py/commit/57b735a920469e0fb6b1f10e2477327e81bf17d7))
* **internal:** update pydantic dependency ([9a64a83](https://github.com/togethercomputer/together-py/commit/9a64a8387f90ef99c31276640b7af1f6e0a50bf7))
* **package:** drop Python 3.8 support ([94fabac](https://github.com/togethercomputer/together-py/commit/94fabacaf4c872ab77dc530990b80aba8214f4f6))
* **types:** change optional parameter type from NotGiven to Omit ([8384a79](https://github.com/togethercomputer/together-py/commit/8384a7900df0798a5c29bf827576735ca258d06b))

## 0.1.0-alpha.18 (2025-09-05)

Full Changelog: [v0.1.0-alpha.17...v0.1.0-alpha.18](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.17...v0.1.0-alpha.18)

### Features

* **api:** api update ([4001cfe](https://github.com/togethercomputer/together-py/commit/4001cfedc1059220c6add12bdec35a39e3f21978))
* improve future compat with pydantic v3 ([384e6b6](https://github.com/togethercomputer/together-py/commit/384e6b6a09e54cbfa19663fb2364833bff7efade))
* **types:** replace List[str] with SequenceNotStr in params ([b5453b3](https://github.com/togethercomputer/together-py/commit/b5453b3733b752b791f4112afc3738c309dd4779))


### Chores

* **internal:** add Sequence related utils ([458cd63](https://github.com/togethercomputer/together-py/commit/458cd63de37a1c9a18a260b73a4db9bd488ed3d3))
* **internal:** move mypy configurations to `pyproject.toml` file ([7faa161](https://github.com/togethercomputer/together-py/commit/7faa16182cafa4cde1c2e173dccd9570f3272405))
* **tests:** simplify `get_platform` test ([44ee2e2](https://github.com/togethercomputer/together-py/commit/44ee2e2c21b7989e4db354238505ecdf676d60b4))

## 0.1.0-alpha.17 (2025-08-29)

Full Changelog: [v0.1.0-alpha.16...v0.1.0-alpha.17](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.16...v0.1.0-alpha.17)

### Features

* **api:** add evals api to config ([a4c2938](https://github.com/togethercomputer/together-py/commit/a4c2938a7d9cd9e61c1510210cd62367c1f46bea))


### Bug Fixes

* avoid newer type syntax ([8723398](https://github.com/togethercomputer/together-py/commit/8723398a6f3e7143e999abe2a7d3aec5dae9d6c1))


### Chores

* **internal:** change ci workflow machines ([7e0823d](https://github.com/togethercomputer/together-py/commit/7e0823d056c11ab3b348376f684c40fd1083be92))

## 0.1.0-alpha.16 (2025-08-21)

Full Changelog: [v0.1.0-alpha.15...v0.1.0-alpha.16](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.15...v0.1.0-alpha.16)

### Features

* **api:** api update ([f0a8308](https://github.com/togethercomputer/together-py/commit/f0a8308e39499125e8cf899c784b4efa352ecee4))
* **api:** api update ([376b1bc](https://github.com/togethercomputer/together-py/commit/376b1bc080925812a9f0163718bbb37abe79e4ae))
* **api:** api update ([e90437f](https://github.com/togethercomputer/together-py/commit/e90437ffb404b6e68699d1e21871050939e868c4))
* **api:** api update ([9363a0d](https://github.com/togethercomputer/together-py/commit/9363a0d7150866ff20e8a548af1fe25a581a590d))
* **api:** api update ([64454cc](https://github.com/togethercomputer/together-py/commit/64454cc2ef08acb96ac25027ca4ed716f5d9aaf4))
* **api:** api update ([891126e](https://github.com/togethercomputer/together-py/commit/891126ee0a7907eb0e38fd20ab269fe8f1fa9473))
* **api:** manual updates ([5bddf93](https://github.com/togethercomputer/together-py/commit/5bddf93637359ac62ace63271060936ab7714aa0))
* **api:** manual updates ([127ba9f](https://github.com/togethercomputer/together-py/commit/127ba9fe10bd8ebe8237faac28a4b6c567bcb9a7))
* clean up environment call outs ([a8ae4ca](https://github.com/togethercomputer/together-py/commit/a8ae4ca28d68f51b03049df4fc46638ec1f2a1b0))
* **client:** support file upload requests ([6e89024](https://github.com/togethercomputer/together-py/commit/6e8902404f65b5c3a4f74d796733e1afa8a4a60a))


### Bug Fixes

* **client:** don't send Content-Type header on GET requests ([0cad846](https://github.com/togethercomputer/together-py/commit/0cad846a3d5b702bb975914e640b7ab3ea5cfbb5))
* **parsing:** ignore empty metadata ([4629c6d](https://github.com/togethercomputer/together-py/commit/4629c6d6364fddceffbb633285ded2d6655bd473))
* **parsing:** parse extra field types ([81734d8](https://github.com/togethercomputer/together-py/commit/81734d82bf4259d644ee787b2aff8c86a6e0edb2))


### Chores

* **internal:** fix ruff target version ([5d6d8cb](https://github.com/togethercomputer/together-py/commit/5d6d8cb97f1c4e381ba69dc41183197788d8b93c))
* **internal:** update comment in script ([4a51bbe](https://github.com/togethercomputer/together-py/commit/4a51bbe766b5dc7139ee86d3c5da4ecc42aeb7b0))
* **internal:** update test skipping reason ([13f9c03](https://github.com/togethercomputer/together-py/commit/13f9c03e1b239df6181d5c8d51dec8c8c35a2ade))
* **project:** add settings file for vscode ([d257e48](https://github.com/togethercomputer/together-py/commit/d257e48ca2cfa4e8e7696566f85d62879dee8af5))
* update @stainless-api/prism-cli to v5.15.0 ([29dca11](https://github.com/togethercomputer/together-py/commit/29dca1155b33339041b63e83c803f8b5b0a99b62))
* update github action ([44e1d3a](https://github.com/togethercomputer/together-py/commit/44e1d3afe46be6a1f8de963fe64690ab051b057a))

## 0.1.0-alpha.15 (2025-07-10)

Full Changelog: [v0.1.0-alpha.14...v0.1.0-alpha.15](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.14...v0.1.0-alpha.15)

### Features

* **api:** adding audio APIs ([7d85bd7](https://github.com/togethercomputer/together-py/commit/7d85bd7b497dcca60e0ef2198dcdbe68239afba8))
* **api:** api update ([fb4b686](https://github.com/togethercomputer/together-py/commit/fb4b6860a6418f69a841bcb466b3a6a83e38ce60))
* **api:** api update ([74be086](https://github.com/togethercomputer/together-py/commit/74be0862b48ee083ea7e6bd9dff2713a24e98799))
* **api:** api update ([5077f31](https://github.com/togethercomputer/together-py/commit/5077f31cbd79add55d1a3fba8cb20211d045dff6))
* **api:** api update ([94a2b5e](https://github.com/togethercomputer/together-py/commit/94a2b5e82c7890fe835792876a936321c87e95c6))
* **api:** api update ([2d73c2e](https://github.com/togethercomputer/together-py/commit/2d73c2e7014e57b29fb910cc22d5df4ec7daa6b2))
* **api:** removed streaming from translation/transcription endpoints ([02af14a](https://github.com/togethercomputer/together-py/commit/02af14a746534eb8b136be72209134f9e8d12d75))


### Bug Fixes

* **ci:** correct conditional ([7ede6e3](https://github.com/togethercomputer/together-py/commit/7ede6e388052ea970aa97ddda230d42933f5f285))
* **ci:** release-doctor — report correct token name ([3d04b80](https://github.com/togethercomputer/together-py/commit/3d04b80d5380864cb450c4fbd10d2ddcf154d132))
* **parsing:** correctly handle nested discriminated unions ([d930701](https://github.com/togethercomputer/together-py/commit/d9307012a76a110e1d12284631f084e365d15d77))


### Chores

* **ci:** change upload type ([16f1b33](https://github.com/togethercomputer/together-py/commit/16f1b33fc4593056fcc9a3e9242e1cac75e29f80))
* **ci:** only run for pushes and fork pull requests ([a8a34c0](https://github.com/togethercomputer/together-py/commit/a8a34c04a4b181eb17c49182e8dd6a59295d0f03))
* **internal:** bump pinned h11 dep ([dbb7251](https://github.com/togethercomputer/together-py/commit/dbb725183f21b56bc41f347b43d58e7ea3afdddb))
* **internal:** codegen related update ([74e55b0](https://github.com/togethercomputer/together-py/commit/74e55b0751c6a938e5a44ec3d4fd59099b01f5cd))
* **package:** mark python 3.13 as supported ([b184004](https://github.com/togethercomputer/together-py/commit/b18400445b27608a0792a9a446af418f52c32b59))
* **readme:** fix version rendering on pypi ([6f29b83](https://github.com/togethercomputer/together-py/commit/6f29b833185ad8013bc7aaacad18026a48d2c3ec))

## 0.1.0-alpha.14 (2025-06-23)

Full Changelog: [v0.1.0-alpha.13...v0.1.0-alpha.14](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.13...v0.1.0-alpha.14)

### Chores

* **api:** re-enable audio unit tests ([02c8f9a](https://github.com/togethercomputer/together-py/commit/02c8f9ad850aed5aae7110ab37d33377aead1c47))
* **tests:** skip some failing tests on the latest python versions ([49a71b3](https://github.com/togethercomputer/together-py/commit/49a71b3b35ffaef63bc8100faba69d87d517cedb))

## 0.1.0-alpha.13 (2025-06-20)

Full Changelog: [v0.1.0-alpha.12...v0.1.0-alpha.13](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.12...v0.1.0-alpha.13)

### Features

* **api:** add batch api to config ([07299cc](https://github.com/togethercomputer/together-py/commit/07299cc337cb356076643df7fc070b2fd8e85c54))
* **api:** api update ([249669c](https://github.com/togethercomputer/together-py/commit/249669c03db384d71c04fe69f78a579b5235c54c))
* **client:** add support for aiohttp ([8e4cedf](https://github.com/togethercomputer/together-py/commit/8e4cedf646520031811a97f65460f41b61894dd9))


### Bug Fixes

* **client:** correctly parse binary response | stream ([7b9486c](https://github.com/togethercomputer/together-py/commit/7b9486c29ef0eeb862460d1ee82417db9a8f801f))
* **tests:** fix: tests which call HTTP endpoints directly with the example parameters ([82b2dcb](https://github.com/togethercomputer/together-py/commit/82b2dcb43af96a7339b2305d02486d3084850303))


### Chores

* change publish docs url ([8fac9f3](https://github.com/togethercomputer/together-py/commit/8fac9f3e12630ed88b68c6cb7d798ebcc6a88833))
* **ci:** enable for pull requests ([6e4d972](https://github.com/togethercomputer/together-py/commit/6e4d972a3a3094fb2d8d468d1e3e89b173ce6ffd))
* **internal:** update conftest.py ([2b13ac4](https://github.com/togethercomputer/together-py/commit/2b13ac4298cc44c0515a3aa348cfdb4bc63d9cb2))
* **readme:** update badges ([acfabb5](https://github.com/togethercomputer/together-py/commit/acfabb57a60aab2853283f62d72897a8bb95a778))
* **tests:** add tests for httpx client instantiation & proxies ([30ba23e](https://github.com/togethercomputer/together-py/commit/30ba23e549ed87a82a7e49164b1809388486754b))
* **tests:** run tests in parallel ([7efb923](https://github.com/togethercomputer/together-py/commit/7efb923a6802382cdfe676c1124e6b9dafd8e233))


### Documentation

* **client:** fix httpx.Timeout documentation reference ([bed4e88](https://github.com/togethercomputer/together-py/commit/bed4e88653ff35029c1921bd2d940abade5b00c0))

## 0.1.0-alpha.12 (2025-06-10)

Full Changelog: [v0.1.0-alpha.11...v0.1.0-alpha.12](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.11...v0.1.0-alpha.12)

### Features

* **api:** address diagnostic issues in audio api, correct openapi issue in images api, disambiguate a response in finetune api, enable automated testing on finetune and images ([9d72038](https://github.com/togethercomputer/together-py/commit/9d7203895723e9be3600fa970430d33b51049094))

## 0.1.0-alpha.11 (2025-06-03)

Full Changelog: [v0.1.0-alpha.10...v0.1.0-alpha.11](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.10...v0.1.0-alpha.11)

### Features

* **api:** api update ([3cff5ae](https://github.com/togethercomputer/together-py/commit/3cff5ae5aeda8413075dd164d30cd3afbf66413f))
* **api:** update spec / config to remove remaining codegen warnings ([48986d2](https://github.com/togethercomputer/together-py/commit/48986d2c15b07b6761bc50c93a72a116ec73aed5))

## 0.1.0-alpha.10 (2025-06-03)

Full Changelog: [v0.1.0-alpha.9...v0.1.0-alpha.10](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.9...v0.1.0-alpha.10)

### Features

* **api:** add files/upload apu support and switch upload_file method over to use it. ([2269981](https://github.com/togethercomputer/together-py/commit/2269981dba119b0dc984ae10131817d15cec889a))
* **api:** api update ([436f32a](https://github.com/togethercomputer/together-py/commit/436f32ad54460fe029975bccee1570ff49fe80dd))
* **client:** add follow_redirects request option ([b515197](https://github.com/togethercomputer/together-py/commit/b515197012ea3e342dfbe4a3f7d418fdc90828df))


### Chores

* **docs:** remove reference to rye shell ([1931f17](https://github.com/togethercomputer/together-py/commit/1931f174b6ef8c778a20d1292b27ccbdb67491fb))
* **docs:** remove unnecessary param examples ([6ed818e](https://github.com/togethercomputer/together-py/commit/6ed818ea9e78be560dce5f166d4ba492e4fd1ab3))

## 0.1.0-alpha.9 (2025-05-31)

Full Changelog: [v0.1.0-alpha.8...v0.1.0-alpha.9](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.8...v0.1.0-alpha.9)

### Features

* **api:** get file upload working ([cb8b8b8](https://github.com/togethercomputer/together-py/commit/cb8b8b86974721c2b2366e8481b88b3cb4851f0c))
* **api:** move upload to be a method of existing files resource ([b7c43be](https://github.com/togethercomputer/together-py/commit/b7c43be446e48390528994ee5a070699c490cec4))


### Bug Fixes

* **api:** correct file reroute handling, error message ([b8bc101](https://github.com/togethercomputer/together-py/commit/b8bc1010e047ba0b1bd75a311cb1220f13366f04))

## 0.1.0-alpha.8 (2025-05-29)

Full Changelog: [v0.1.0-alpha.7...v0.1.0-alpha.8](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.7...v0.1.0-alpha.8)

### Features

* **api:** move upload to be a method of existing files resource ([80d5ae0](https://github.com/togethercomputer/together-py/commit/80d5ae03f2fee590266fe5504f738b6d49f5311c))

## 0.1.0-alpha.7 (2025-05-24)

Full Changelog: [v0.1.0-alpha.6...v0.1.0-alpha.7](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.6...v0.1.0-alpha.7)

### Features

* **api:** update via SDK Studio ([8be984a](https://github.com/togethercomputer/together-py/commit/8be984afa71c2926525cbd2c0cac3ec1806bfda9))
* **api:** update via SDK Studio ([7c0522d](https://github.com/togethercomputer/together-py/commit/7c0522dd99b90fbcabd21f1725d79f72e3a7c020))
* **api:** update via SDK Studio ([e4a88e4](https://github.com/togethercomputer/together-py/commit/e4a88e45e7092e44cfdd8ab2c3c9d6c89fdd612b))
* **api:** update via SDK Studio ([065228b](https://github.com/togethercomputer/together-py/commit/065228b816ddfb77587de79c52e0b1a93ee2c714))


### Chores

* **tests:** improve ci test names ([03a7211](https://github.com/togethercomputer/together-py/commit/03a721149086b2eaf3bf4a41334e44fd40b3c13c))

## 0.1.0-alpha.6 (2025-05-22)

Full Changelog: [v0.1.0-alpha.5...v0.1.0-alpha.6](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.5...v0.1.0-alpha.6)

### Features

* **api:** update ([075b568](https://github.com/togethercomputer/together-py/commit/075b568c1f6b70c4c46d023de90bfeb1e9dab9cc))


### Bug Fixes

* **tests:** make test pydantic v1 compatible ([ffd8631](https://github.com/togethercomputer/together-py/commit/ffd863143a209d51ba1e3c0abd7f0d2220ac3c5e))

## 0.1.0-alpha.5 (2025-05-21)

Full Changelog: [v0.1.0-alpha.4...v0.1.0-alpha.5](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.4...v0.1.0-alpha.5)

### Features

* **api:** api update ([ccdc937](https://github.com/togethercomputer/together-py/commit/ccdc93755af77a38f53967a7e4051bf8c8c38526))
* **api:** api update ([33f506b](https://github.com/togethercomputer/together-py/commit/33f506b8ad4aa62c9b0c1c8c25213c4d7fd668f8))
* **api:** api update ([e5803db](https://github.com/togethercomputer/together-py/commit/e5803db6544207bc92f193baa739a2cd1b230d5c))
* **api:** api update ([3d7c605](https://github.com/togethercomputer/together-py/commit/3d7c605429a02698d4f651fed09ef99ee1098791))
* **api:** api update ([ccef35f](https://github.com/togethercomputer/together-py/commit/ccef35fda09b9f39c5d6f33ec3fed8a73793a490))
* **api:** Formatting fixes, some lint fixes ([e002ae7](https://github.com/togethercomputer/together-py/commit/e002ae790103c0e48a3116041d344785a249b61f))
* **api:** get test_code_interpreter passing ([dc5babc](https://github.com/togethercomputer/together-py/commit/dc5babcf915591e1dc680a6f1aa440d9c5f48aa0))
* **api:** Update spec and config to get all tests except code-interpolation an fine_tune unit tests working. ([2c21a07](https://github.com/togethercomputer/together-py/commit/2c21a07e6c56a736d51974287e3520fa52cea724))


### Chores

* **ci:** fix installation instructions ([164cbd1](https://github.com/togethercomputer/together-py/commit/164cbd14b5f399315d69318e0cb4aca0838a9ad3))
* **ci:** upload sdks to package manager ([c9aae0a](https://github.com/togethercomputer/together-py/commit/c9aae0aeaae0a5014fa9e7383db6b24fa2c09fe2))
* **ci:** use --pre flag for prerelease installation instructions ([9775c6b](https://github.com/togethercomputer/together-py/commit/9775c6b14a4bb7c7571b6cd7e9166fe86df51731))
* **ci:** use --pre flag for prerelease installation instructions ([a460c1e](https://github.com/togethercomputer/together-py/commit/a460c1e8981138d2f928fab0fc8e3e40abea035b))
* **docs:** grammar improvements ([387b072](https://github.com/togethercomputer/together-py/commit/387b07273ae75d5216aeb996e37b540572f2ac40))

## 0.1.0-alpha.4 (2025-05-13)

Full Changelog: [v0.1.0-alpha.3...v0.1.0-alpha.4](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.3...v0.1.0-alpha.4)

### Features

* **api:** add tci resources ([023b3a0](https://github.com/togethercomputer/together-py/commit/023b3a00991729a0a06845ee7f64f760cf6f4325))
* **api:** adds unspecified endpoints ([678f58a](https://github.com/togethercomputer/together-py/commit/678f58af8b2be9e65b667cb0b104a9be4b6667f4))
* **api:** api update ([6d9609e](https://github.com/togethercomputer/together-py/commit/6d9609e279d228ba1aad926914d089904b858c01))
* **api:** api update ([bb40eb9](https://github.com/togethercomputer/together-py/commit/bb40eb96cbf911f0f9772c98e261988ab1432383))
* **api:** api update ([271887f](https://github.com/togethercomputer/together-py/commit/271887fe30d8f4b8f0405d16366e1f82868a1d0d))
* **api:** api update ([2a7de06](https://github.com/togethercomputer/together-py/commit/2a7de06a3a1b5425a1dd553c32390df21b252e21))
* **api:** api update ([#117](https://github.com/togethercomputer/together-py/issues/117)) ([dd8e841](https://github.com/togethercomputer/together-py/commit/dd8e841d1eaf40a9f143f63f7f4ced0f701b0fbd))
* **api:** api update ([#120](https://github.com/togethercomputer/together-py/issues/120)) ([adf0e5b](https://github.com/togethercomputer/together-py/commit/adf0e5ba1cd266278cf4503b04cfcd847a97b0e4))
* **api:** api update ([#121](https://github.com/togethercomputer/together-py/issues/121)) ([0ab0bc9](https://github.com/togethercomputer/together-py/commit/0ab0bc97ca4db4d2d64f3c2f9eeada9ffa37fc97))
* **api:** api update ([#130](https://github.com/togethercomputer/together-py/issues/130)) ([4f1a7ea](https://github.com/togethercomputer/together-py/commit/4f1a7ea708c55466f4fa3f1698b505ffbfe2aea6))
* **api:** api update ([#132](https://github.com/togethercomputer/together-py/issues/132)) ([7c8a194](https://github.com/togethercomputer/together-py/commit/7c8a194c4e1f484f8455adce6f56c840411f4946))
* **api:** api update ([#135](https://github.com/togethercomputer/together-py/issues/135)) ([22a93e9](https://github.com/togethercomputer/together-py/commit/22a93e9c5c7a33c502f5a4c380c576c2a752d6a5))


### Bug Fixes

* **ci:** ensure pip is always available ([#127](https://github.com/togethercomputer/together-py/issues/127)) ([4da2bc0](https://github.com/togethercomputer/together-py/commit/4da2bc0bb7cc4516cf0d93032544fbb71025c118))
* **ci:** remove publishing patch ([#128](https://github.com/togethercomputer/together-py/issues/128)) ([6bd4d6f](https://github.com/togethercomputer/together-py/commit/6bd4d6f8d8f8842f56cdbb56df0a4d5e5227dde4))
* **client:** correct type to enum ([#129](https://github.com/togethercomputer/together-py/issues/129)) ([8a5fa0e](https://github.com/togethercomputer/together-py/commit/8a5fa0e2858e851756f022943ada948374bb017c))
* **package:** support direct resource imports ([f59e7c3](https://github.com/togethercomputer/together-py/commit/f59e7c3b3bcc7c076bd8c71b2ab42f8a117e5519))
* **perf:** optimize some hot paths ([f79734d](https://github.com/togethercomputer/together-py/commit/f79734d809a4a7c18eb8903190e6b4d90d299e45))
* **perf:** skip traversing types for NotGiven values ([1103dd0](https://github.com/togethercomputer/together-py/commit/1103dd03e7f021deadd0b000b3bff9c5494442b6))
* **pydantic v1:** more robust ModelField.annotation check ([d380238](https://github.com/togethercomputer/together-py/commit/d3802383e80ad8d3606a1e753c72a20864531332))
* skip invalid fine-tune test ([#133](https://github.com/togethercomputer/together-py/issues/133)) ([2f41046](https://github.com/togethercomputer/together-py/commit/2f4104625264947305cee0bd26fc38ff290f16ea))
* **tests:** correctly skip create fine tune tests ([#138](https://github.com/togethercomputer/together-py/issues/138)) ([47c9cae](https://github.com/togethercomputer/together-py/commit/47c9cae7da9caee8de3ba7480b784fc5d168e1b0))
* **types:** handle more discriminated union shapes ([#126](https://github.com/togethercomputer/together-py/issues/126)) ([2483c76](https://github.com/togethercomputer/together-py/commit/2483c76ee0cf06ee7a1819446cfa4fa349958da4))


### Chores

* broadly detect json family of content-type headers ([6e2421e](https://github.com/togethercomputer/together-py/commit/6e2421e126e74b4bcc7bc2aaef07a078bdd1e0ea))
* **ci:** add timeout thresholds for CI jobs ([2425c53](https://github.com/togethercomputer/together-py/commit/2425c53723d34959380d44131d607ded5a665004))
* **ci:** only use depot for staging repos ([2dfe569](https://github.com/togethercomputer/together-py/commit/2dfe569cf72f74a97fbe1e282c9d079c371d32aa))
* **ci:** run on more branches and use depot runners ([3c61f56](https://github.com/togethercomputer/together-py/commit/3c61f565633c395dba16fda924c241910145c13c))
* **client:** minor internal fixes ([f6f5174](https://github.com/togethercomputer/together-py/commit/f6f5174c6ec0b9a3a4decfc25737efbbb52bffe5))
* fix typos ([#131](https://github.com/togethercomputer/together-py/issues/131)) ([dedf3ad](https://github.com/togethercomputer/together-py/commit/dedf3adb709255ba9303e29354b013db8a8520b9))
* **internal:** avoid errors for isinstance checks on proxies ([8b81509](https://github.com/togethercomputer/together-py/commit/8b81509faac153ee4a33b3460c17759e2465dfcd))
* **internal:** base client updates ([890efc3](https://github.com/togethercomputer/together-py/commit/890efc36f00553025237601bad51f3f0a906376b))
* **internal:** bump pyright version ([01e104a](https://github.com/togethercomputer/together-py/commit/01e104a2bba92c77ef610cf48720d8a2785ff39b))
* **internal:** bump rye to 0.44.0 ([#124](https://github.com/togethercomputer/together-py/issues/124)) ([e8c3dc3](https://github.com/togethercomputer/together-py/commit/e8c3dc3be0e56d7c4e7a48d8f824a88878e0c981))
* **internal:** codegen related update ([#125](https://github.com/togethercomputer/together-py/issues/125)) ([5e83e04](https://github.com/togethercomputer/together-py/commit/5e83e043b3f62c38fa13c72d54278e845c2df46a))
* **internal:** expand CI branch coverage ([#139](https://github.com/togethercomputer/together-py/issues/139)) ([2db8ca2](https://github.com/togethercomputer/together-py/commit/2db8ca2b6d063b136e9cb50c3991a11f6f47e4fb))
* **internal:** fix list file params ([8a8dcd3](https://github.com/togethercomputer/together-py/commit/8a8dcd384e480c52358460ba662a48311a415cfb))
* **internal:** import reformatting ([49f361b](https://github.com/togethercomputer/together-py/commit/49f361bf9d548ca45a01e31972b5db797752e481))
* **internal:** minor formatting changes ([33e3a75](https://github.com/togethercomputer/together-py/commit/33e3a751bd9f3382e5e462bbcf92a212e14d26ff))
* **internal:** reduce CI branch coverage ([6f6ac97](https://github.com/togethercomputer/together-py/commit/6f6ac973e36bdeb28883ff6281228c67f76c55a1))
* **internal:** refactor retries to not use recursion ([ffb0eb4](https://github.com/togethercomputer/together-py/commit/ffb0eb46712544a86f01eaa842ac13f085e37fee))
* **internal:** remove extra empty newlines ([#122](https://github.com/togethercomputer/together-py/issues/122)) ([b0cbbaa](https://github.com/togethercomputer/together-py/commit/b0cbbaa10e003e84cf2c8c23ef05baa6bc9d4e82))
* **internal:** remove trailing character ([#134](https://github.com/togethercomputer/together-py/issues/134)) ([f09c6cb](https://github.com/togethercomputer/together-py/commit/f09c6cb1620997e72b99bc918d77ae9a2be9e8b3))
* **internal:** slight transform perf improvement ([#136](https://github.com/togethercomputer/together-py/issues/136)) ([d31383c](https://github.com/togethercomputer/together-py/commit/d31383c0f8fb1749381fad871aa60bd0eaad3e03))
* **internal:** update models test ([b64d4cc](https://github.com/togethercomputer/together-py/commit/b64d4cc9a1424fa7f46088e51306b877afba3fae))
* **internal:** update pyright settings ([05720d5](https://github.com/togethercomputer/together-py/commit/05720d5b0b7387fbe3b04975dfa6b764898a7a02))
* **tests:** improve enum examples ([#137](https://github.com/togethercomputer/together-py/issues/137)) ([4c3e75d](https://github.com/togethercomputer/together-py/commit/4c3e75d5aa75421d4aca257c0df89d24e2db264e))


### Documentation

* revise readme docs about nested params ([#118](https://github.com/togethercomputer/together-py/issues/118)) ([0eefffd](https://github.com/togethercomputer/together-py/commit/0eefffd623bc692f2e03fd299b9b05c3bb88bf53))

## 0.1.0-alpha.3 (2025-03-05)

Full Changelog: [v0.1.0-alpha.2...v0.1.0-alpha.3](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.2...v0.1.0-alpha.3)

### Features

* **api:** add audio create method ([#92](https://github.com/togethercomputer/together-py/issues/92)) ([bcf3aa1](https://github.com/togethercomputer/together-py/commit/bcf3aa18688ad9ea36fea2bcfe067db01289120a))
* **api:** add models for chat completion structured message types ([#75](https://github.com/togethercomputer/together-py/issues/75)) ([f2ae323](https://github.com/togethercomputer/together-py/commit/f2ae3239bb6bf699fc065d071a1c5ba87db5f88a))
* **api:** api update ([#101](https://github.com/togethercomputer/together-py/issues/101)) ([2bd8e65](https://github.com/togethercomputer/together-py/commit/2bd8e65544d59c69a80bafe169eb04897d71245a))
* **api:** api update ([#105](https://github.com/togethercomputer/together-py/issues/105)) ([4eef0b2](https://github.com/togethercomputer/together-py/commit/4eef0b218aba9fc9256399b42e176701b5ff60d5))
* **api:** api update ([#108](https://github.com/togethercomputer/together-py/issues/108)) ([b601cca](https://github.com/togethercomputer/together-py/commit/b601cca20a962ed13d81edd421fc828614e2a10d))
* **api:** api update ([#114](https://github.com/togethercomputer/together-py/issues/114)) ([6f01742](https://github.com/togethercomputer/together-py/commit/6f0174242cabac214cce8dd09002825bcb02d1dd))
* **api:** api update ([#45](https://github.com/togethercomputer/together-py/issues/45)) ([d387d6a](https://github.com/togethercomputer/together-py/commit/d387d6abb8c674927598309d57802d97c7c00b89))
* **api:** api update ([#46](https://github.com/togethercomputer/together-py/issues/46)) ([def7699](https://github.com/togethercomputer/together-py/commit/def76990bafc2d34d37c1e4e25895593945d0822))
* **api:** api update ([#47](https://github.com/togethercomputer/together-py/issues/47)) ([d02eebd](https://github.com/togethercomputer/together-py/commit/d02eebd261e87bfc4e1de13aa865290935976fd8))
* **api:** api update ([#48](https://github.com/togethercomputer/together-py/issues/48)) ([3653de7](https://github.com/togethercomputer/together-py/commit/3653de7c2cee68ba4028ae4dd321cfae7627865c))
* **api:** api update ([#49](https://github.com/togethercomputer/together-py/issues/49)) ([7a7f47e](https://github.com/togethercomputer/together-py/commit/7a7f47e3cf9e72a4889bb08ff754aaf98c8759f0))
* **api:** api update ([#50](https://github.com/togethercomputer/together-py/issues/50)) ([15d98b6](https://github.com/togethercomputer/together-py/commit/15d98b6a3f41077e6416acf27a7c533efdc7d70e))
* **api:** api update ([#51](https://github.com/togethercomputer/together-py/issues/51)) ([206d67c](https://github.com/togethercomputer/together-py/commit/206d67c4776b0edeead915d0c1194deef05553b4))
* **api:** api update ([#57](https://github.com/togethercomputer/together-py/issues/57)) ([5fa99e8](https://github.com/togethercomputer/together-py/commit/5fa99e8d5d17833b48a2483c1ef8b5adeefb7527))
* **api:** api update ([#60](https://github.com/togethercomputer/together-py/issues/60)) ([1ee28e1](https://github.com/togethercomputer/together-py/commit/1ee28e1e767b72b073196cee1231c2a582a7009a))
* **api:** api update ([#61](https://github.com/togethercomputer/together-py/issues/61)) ([b330e50](https://github.com/togethercomputer/together-py/commit/b330e50d40f30e1ffb3293b3bb602664085a97ed))
* **api:** api update ([#65](https://github.com/togethercomputer/together-py/issues/65)) ([db5d526](https://github.com/togethercomputer/together-py/commit/db5d526fff7953cb40947ec820b68a44463c5662))
* **api:** api update ([#66](https://github.com/togethercomputer/together-py/issues/66)) ([a7f9670](https://github.com/togethercomputer/together-py/commit/a7f967053aa1c9095b6d8e019797d0e8ea167471))
* **api:** api update ([#67](https://github.com/togethercomputer/together-py/issues/67)) ([cb2be54](https://github.com/togethercomputer/together-py/commit/cb2be54bb0060f6139dabb9a10a72e76ac042263))
* **api:** api update ([#95](https://github.com/togethercomputer/together-py/issues/95)) ([f98a54f](https://github.com/togethercomputer/together-py/commit/f98a54ff0ed5e74333c07fa06ae3276e5278fbb9))
* **api:** api update ([#97](https://github.com/togethercomputer/together-py/issues/97)) ([41f9f89](https://github.com/togethercomputer/together-py/commit/41f9f8968a4f8bba01881d05b88b894328df90af))
* **api:** OpenAPI spec update via Stainless API ([#26](https://github.com/togethercomputer/together-py/issues/26)) ([cbbd44c](https://github.com/togethercomputer/together-py/commit/cbbd44ce8dae1d12129ce5703f01884ff56e46a1))
* **api:** OpenAPI spec update via Stainless API ([#31](https://github.com/togethercomputer/together-py/issues/31)) ([87136bb](https://github.com/togethercomputer/together-py/commit/87136bb2d9a11485e587aa6265b11cd407a2b213))
* **api:** OpenAPI spec update via Stainless API ([#32](https://github.com/togethercomputer/together-py/issues/32)) ([8cb6e69](https://github.com/togethercomputer/together-py/commit/8cb6e69d8f294695c4ad8847b24443c59c327bb2))
* **api:** OpenAPI spec update via Stainless API ([#33](https://github.com/togethercomputer/together-py/issues/33)) ([c4e5afb](https://github.com/togethercomputer/together-py/commit/c4e5afbe89e938a0ead46fd1b309e078bb879c33))
* **api:** OpenAPI spec update via Stainless API ([#35](https://github.com/togethercomputer/together-py/issues/35)) ([3d1993e](https://github.com/togethercomputer/together-py/commit/3d1993ed5e0f9b540d0e4007a505948eab863a77))
* **api:** OpenAPI spec update via Stainless API ([#39](https://github.com/togethercomputer/together-py/issues/39)) ([6dd6113](https://github.com/togethercomputer/together-py/commit/6dd6113e0a6e6047a459a9ced7dfebeea9c00a10))
* **client:** allow passing `NotGiven` for body ([#107](https://github.com/togethercomputer/together-py/issues/107)) ([8a33c2e](https://github.com/togethercomputer/together-py/commit/8a33c2eb83b37e1da3b77d1c996d856ed2501366))
* **client:** send `X-Stainless-Read-Timeout` header ([#100](https://github.com/togethercomputer/together-py/issues/100)) ([f32ec38](https://github.com/togethercomputer/together-py/commit/f32ec387fe4aba3583d2ab56643d1db8b1becb28))


### Bug Fixes

* asyncify on non-asyncio runtimes ([#106](https://github.com/togethercomputer/together-py/issues/106)) ([573af88](https://github.com/togethercomputer/together-py/commit/573af88a8eb6e0b7b2e86e06db5edef8d5286e4a))
* **client:** avoid OverflowError with very large retry counts ([#42](https://github.com/togethercomputer/together-py/issues/42)) ([580649d](https://github.com/togethercomputer/together-py/commit/580649d2168ed69328c33c1d5d03bb3f85ad8840))
* **client:** compat with new httpx 0.28.0 release ([#69](https://github.com/togethercomputer/together-py/issues/69)) ([6b181ec](https://github.com/togethercomputer/together-py/commit/6b181ecf4876483e553080cb701f6f814d180a89))
* **client:** mark some request bodies as optional ([8a33c2e](https://github.com/togethercomputer/together-py/commit/8a33c2eb83b37e1da3b77d1c996d856ed2501366))
* **client:** only call .close() when needed ([#85](https://github.com/togethercomputer/together-py/issues/85)) ([79ef703](https://github.com/togethercomputer/together-py/commit/79ef70387b107a6ff7af73d6e773a7efcff6ff25))
* **cli:** handle nullable choice property ([8af8258](https://github.com/togethercomputer/together-py/commit/8af825830bb45afc592089b34ff9bcf8485bbc57))
* correctly handle deserialising `cls` fields ([#88](https://github.com/togethercomputer/together-py/issues/88)) ([dfe1abb](https://github.com/togethercomputer/together-py/commit/dfe1abb2d5bbecea63587279aa04356bb5951054))
* **tests:** skip invalid test ([#96](https://github.com/togethercomputer/together-py/issues/96)) ([e66f177](https://github.com/togethercomputer/together-py/commit/e66f177a3f6dbd02710aae2ae9ea27e9d25bd2c7))


### Chores

* add docstrings to raw response properties ([#37](https://github.com/togethercomputer/together-py/issues/37)) ([8d8e94b](https://github.com/togethercomputer/together-py/commit/8d8e94b4f6998b1f01e9afda84f90ff19c07802f))
* add missing isclass check ([#83](https://github.com/togethercomputer/together-py/issues/83)) ([e99d895](https://github.com/togethercomputer/together-py/commit/e99d895ffe68dedab5023ba95c715d5b68cebd47))
* add repr to PageInfo class ([#43](https://github.com/togethercomputer/together-py/issues/43)) ([7879084](https://github.com/togethercomputer/together-py/commit/787908403f1cb0394e4b4a4f8ea86e5cb8672e1f))
* **client:** fix parsing union responses when non-json is returned ([#28](https://github.com/togethercomputer/together-py/issues/28)) ([f748a99](https://github.com/togethercomputer/together-py/commit/f748a995b81fa2250a161e27be139cf796600700))
* **docs:** update client docstring ([#112](https://github.com/togethercomputer/together-py/issues/112)) ([1ea62fe](https://github.com/togethercomputer/together-py/commit/1ea62fe9605f93143fbbc63e2a6ba56ed23b6e45))
* **internal:** add support for parsing bool response content ([#41](https://github.com/togethercomputer/together-py/issues/41)) ([848cd31](https://github.com/togethercomputer/together-py/commit/848cd31a072cd8cab99ed8796aecda9787197c24))
* **internal:** add support for TypeAliasType ([#77](https://github.com/togethercomputer/together-py/issues/77)) ([8850496](https://github.com/togethercomputer/together-py/commit/8850496bad1c864e97c6993c661bc8829c814b94))
* **internal:** bummp ruff dependency ([#99](https://github.com/togethercomputer/together-py/issues/99)) ([c152d80](https://github.com/togethercomputer/together-py/commit/c152d805cade1e92a9bd17ac8c1d3d4d59015bfa))
* **internal:** bump httpx dependency ([#84](https://github.com/togethercomputer/together-py/issues/84)) ([7155d20](https://github.com/togethercomputer/together-py/commit/7155d205e82c5e5f255d7435b36ecc1a31182754))
* **internal:** bump pydantic dependency ([#72](https://github.com/togethercomputer/together-py/issues/72)) ([9266b43](https://github.com/togethercomputer/together-py/commit/9266b438f3bcd76b0821653099e0618c16ba1a5d))
* **internal:** bump pyright ([#70](https://github.com/togethercomputer/together-py/issues/70)) ([34237b9](https://github.com/togethercomputer/together-py/commit/34237b935b82e314b19b391eb740052b9f6c3ef3))
* **internal:** bump pyright ([#76](https://github.com/togethercomputer/together-py/issues/76)) ([b0f7cf2](https://github.com/togethercomputer/together-py/commit/b0f7cf20542a72d978f88d1c4acc8f789eed81ec))
* **internal:** change default timeout to an int ([#98](https://github.com/togethercomputer/together-py/issues/98)) ([5e0fd91](https://github.com/togethercomputer/together-py/commit/5e0fd9103c651ba148f4dbc7997bd9d71d6ed020))
* **internal:** codegen related update ([#113](https://github.com/togethercomputer/together-py/issues/113)) ([bbfb435](https://github.com/togethercomputer/together-py/commit/bbfb435fd81613ffd8537c88de8ff72aa3030bc8))
* **internal:** codegen related update ([#36](https://github.com/togethercomputer/together-py/issues/36)) ([523c4d1](https://github.com/togethercomputer/together-py/commit/523c4d1e4f0885e82abb9b3e4b7e773eb39ace51))
* **internal:** codegen related update ([#40](https://github.com/togethercomputer/together-py/issues/40)) ([40ea230](https://github.com/togethercomputer/together-py/commit/40ea2301b74e82f79293961cb0148d0c3c92db1f))
* **internal:** codegen related update ([#62](https://github.com/togethercomputer/together-py/issues/62)) ([53019a6](https://github.com/togethercomputer/together-py/commit/53019a60a126b8f69df6b8f00cc9f2727b2b8f72))
* **internal:** codegen related update ([#68](https://github.com/togethercomputer/together-py/issues/68)) ([5716d81](https://github.com/togethercomputer/together-py/commit/5716d8131b189d0a4f269932d1f506b6832c530b))
* **internal:** codegen related update ([#82](https://github.com/togethercomputer/together-py/issues/82)) ([69cc9ed](https://github.com/togethercomputer/together-py/commit/69cc9edb0d4b50ce1190dabdfb222c1ff1dbcf96))
* **internal:** codegen related update ([#87](https://github.com/togethercomputer/together-py/issues/87)) ([1ff846c](https://github.com/togethercomputer/together-py/commit/1ff846c69170e569a27ad4e561298c094ed3df98))
* **internal:** codegen related update ([#93](https://github.com/togethercomputer/together-py/issues/93)) ([1c16d7b](https://github.com/togethercomputer/together-py/commit/1c16d7bb252c6effb8180dd4aa9b4f1edc571422))
* **internal:** fix devcontainers setup ([#109](https://github.com/togethercomputer/together-py/issues/109)) ([df0b4c6](https://github.com/togethercomputer/together-py/commit/df0b4c6c024c142480b3366418934cd39011c6c9))
* **internal:** fix some typos ([#81](https://github.com/togethercomputer/together-py/issues/81)) ([1bcc6f0](https://github.com/togethercomputer/together-py/commit/1bcc6f020b95152cabc45add97db2245073505eb))
* **internal:** fix type traversing dictionary params ([#102](https://github.com/togethercomputer/together-py/issues/102)) ([ca385c7](https://github.com/togethercomputer/together-py/commit/ca385c743610da4c82b674bbfec2f820151036b9))
* **internal:** minor formatting changes ([#94](https://github.com/togethercomputer/together-py/issues/94)) ([b66a762](https://github.com/togethercomputer/together-py/commit/b66a762419391ad07bcd4501142296641fb0e4f2))
* **internal:** minor type handling changes ([#103](https://github.com/togethercomputer/together-py/issues/103)) ([901a1d3](https://github.com/togethercomputer/together-py/commit/901a1d37fc719e34a935940cbb176402b862c512))
* **internal:** properly set __pydantic_private__ ([#110](https://github.com/togethercomputer/together-py/issues/110)) ([634041c](https://github.com/togethercomputer/together-py/commit/634041c61fa25fd7dedfc8a972030a3776adac1f))
* **internal:** update client tests ([#104](https://github.com/togethercomputer/together-py/issues/104)) ([026f971](https://github.com/togethercomputer/together-py/commit/026f97187ef926303ae4fb00b9a9d06665e8a455))
* **internal:** update deps ([#91](https://github.com/togethercomputer/together-py/issues/91)) ([2a6fd12](https://github.com/togethercomputer/together-py/commit/2a6fd1225b89b44d3ee067d8d590feba9ea5db32))
* **internal:** updated imports ([#78](https://github.com/togethercomputer/together-py/issues/78)) ([3e66395](https://github.com/togethercomputer/together-py/commit/3e66395cd6ce99505636e446afe3b97a96bd6816))
* make the `Omit` type public ([#71](https://github.com/togethercomputer/together-py/issues/71)) ([e50e602](https://github.com/togethercomputer/together-py/commit/e50e602072586b0003afba7b32a22d455949ef5e))
* rebuild project due to codegen change ([#52](https://github.com/togethercomputer/together-py/issues/52)) ([140ec3a](https://github.com/togethercomputer/together-py/commit/140ec3a98ff40156f417eaece8b0738367a7a572))
* rebuild project due to codegen change ([#55](https://github.com/togethercomputer/together-py/issues/55)) ([46088fc](https://github.com/togethercomputer/together-py/commit/46088fc360d2d05ad2fc59cb42331c87e3ab3f06))
* rebuild project due to codegen change ([#56](https://github.com/togethercomputer/together-py/issues/56)) ([6fdde5a](https://github.com/togethercomputer/together-py/commit/6fdde5aaf60bf05de17c83ac369fbd6e66c9e9ba))
* rebuild project due to codegen change ([#58](https://github.com/togethercomputer/together-py/issues/58)) ([98cd9d5](https://github.com/togethercomputer/together-py/commit/98cd9d5700cfdcaba486d4c83b98dc86a702dbec))
* rebuild project due to codegen change ([#59](https://github.com/togethercomputer/together-py/issues/59)) ([96f0ddb](https://github.com/togethercomputer/together-py/commit/96f0ddb63bc654363303e23c1f02bda28d18f816))
* remove now unused `cached-property` dep ([#63](https://github.com/togethercomputer/together-py/issues/63)) ([e61ac83](https://github.com/togethercomputer/together-py/commit/e61ac834296fc38fc88158cd4d8d61d0273bd823))


### Documentation

* fix typos ([#86](https://github.com/togethercomputer/together-py/issues/86)) ([8061902](https://github.com/togethercomputer/together-py/commit/80619026d4dfb78e9823a87461a49fec2525014c))
* **readme:** add section on determining installed version ([#38](https://github.com/togethercomputer/together-py/issues/38)) ([f52840b](https://github.com/togethercomputer/together-py/commit/f52840b684a47a9d611511a325d4343360b61338))
* **readme:** example snippet for client context manager ([#79](https://github.com/togethercomputer/together-py/issues/79)) ([81f9dad](https://github.com/togethercomputer/together-py/commit/81f9dad95c710bc6de5d106ba67521699b692875))
* **readme:** fix http client proxies example ([#74](https://github.com/togethercomputer/together-py/issues/74)) ([001a301](https://github.com/togethercomputer/together-py/commit/001a301da287333c3cb20e90c3d26c9fbd578334))
* update URLs from stainlessapi.com to stainless.com ([#111](https://github.com/togethercomputer/together-py/issues/111)) ([728c998](https://github.com/togethercomputer/together-py/commit/728c9983019b13cd6a08f378f134902ab9e905d6))

## 0.1.0-alpha.2 (2024-08-17)

Full Changelog: [v0.1.0-alpha.1...v0.1.0-alpha.2](https://github.com/togethercomputer/together-py/compare/v0.1.0-alpha.1...v0.1.0-alpha.2)

### Features

* **api:** manual updates ([#17](https://github.com/togethercomputer/together-py/issues/17)) ([6c36480](https://github.com/togethercomputer/together-py/commit/6c36480b01a9c06bc4a38583128dfa0103a5a15f))
* **api:** OpenAPI spec update via Stainless API ([#12](https://github.com/togethercomputer/together-py/issues/12)) ([da7c038](https://github.com/togethercomputer/together-py/commit/da7c038db29c5b81b17f6f006ffb2086e929b4b7))
* **api:** OpenAPI spec update via Stainless API ([#21](https://github.com/togethercomputer/together-py/issues/21)) ([26ef309](https://github.com/togethercomputer/together-py/commit/26ef30958bf3cf1253772191bc6ae9ac15b021f0))
* **api:** removed pypi publishing for now ([#23](https://github.com/togethercomputer/together-py/issues/23)) ([badbc9a](https://github.com/togethercomputer/together-py/commit/badbc9a80cf09630b8b119e685ede1d4ed1831ed))


### Chores

* **ci:** bump prism mock server version ([#19](https://github.com/togethercomputer/together-py/issues/19)) ([fb2da6c](https://github.com/togethercomputer/together-py/commit/fb2da6c134ef986824f3f2f5a9f850674987d575))
* **examples:** minor formatting changes ([#22](https://github.com/togethercomputer/together-py/issues/22)) ([52377af](https://github.com/togethercomputer/together-py/commit/52377af8d8404270e7e22ff29bca47cdaf18be7c))
* **internal:** codegen related update ([#18](https://github.com/togethercomputer/together-py/issues/18)) ([8496650](https://github.com/togethercomputer/together-py/commit/84966509e71f5b8541ea09c917bc20a29ad20e63))
* **internal:** ensure package is importable in lint cmd ([#20](https://github.com/togethercomputer/together-py/issues/20)) ([324e03a](https://github.com/togethercomputer/together-py/commit/324e03a73ccef62ec1b1cb328253db0a1813d4ab))
* **internal:** use different 32bit detection method ([#24](https://github.com/togethercomputer/together-py/issues/24)) ([b14d279](https://github.com/togethercomputer/together-py/commit/b14d279715cc3ee2274d45fd1d44c83c7baaf279))

## 0.1.0-alpha.1 (2024-07-16)

Full Changelog: [v0.0.1-alpha.0...v0.1.0-alpha.1](https://github.com/togethercomputer/together-py/compare/v0.0.1-alpha.0...v0.1.0-alpha.1)

### Features

* **api:** Config update for pstern-sl/dev ([0a841c4](https://github.com/togethercomputer/together-py/commit/0a841c447d833ee2a6008db4b2ddd4b75eb47fbd))
* **api:** manual updates ([d43927b](https://github.com/togethercomputer/together-py/commit/d43927b37622bb7d233a178eceb21b2223bba1bc))
* **api:** manual updates ([94cfef7](https://github.com/togethercomputer/together-py/commit/94cfef7ff7d499fc2e8dd7b1ad4fed9e908cd28a))
* **api:** manual updates ([#6](https://github.com/togethercomputer/together-py/issues/6)) ([a25a797](https://github.com/togethercomputer/together-py/commit/a25a797f7f7d473ff3f2a939179e6576ec02f891))
* **api:** OpenAPI spec update via Stainless API ([a78681d](https://github.com/togethercomputer/together-py/commit/a78681d3a8ea469844936ac4793f0a374a4d1af1))
* **api:** OpenAPI spec update via Stainless API ([9d54568](https://github.com/togethercomputer/together-py/commit/9d54568072bbaef6b99bd0fbc54c451144f2e1f5))
* **api:** OpenAPI spec update via Stainless API ([00c8693](https://github.com/togethercomputer/together-py/commit/00c86934ed1ab85f0ed1cbc5ecb069d94366b2cd))
* **api:** OpenAPI spec update via Stainless API ([8609a6e](https://github.com/togethercomputer/together-py/commit/8609a6e8d13b50bf22ec67d0149c9ab51f5dea0e))
* **api:** OpenAPI spec update via Stainless API ([3dc55d1](https://github.com/togethercomputer/together-py/commit/3dc55d1f4cd41e5a4054bd2a43a5595373db150c))
* **api:** OpenAPI spec update via Stainless API ([add76c7](https://github.com/togethercomputer/together-py/commit/add76c7c0ef977dadc3b23f54c784a7f62b81528))
* **api:** OpenAPI spec update via Stainless API ([5eaa129](https://github.com/togethercomputer/together-py/commit/5eaa1290359411361b99008695d2c786507d2073))
* **api:** OpenAPI spec update via Stainless API ([d229eef](https://github.com/togethercomputer/together-py/commit/d229eeffe4022374b4d2fd9df208afe4c0fd21bb))
* **api:** OpenAPI spec update via Stainless API ([643f5cf](https://github.com/togethercomputer/together-py/commit/643f5cfc1d6c3d4d1c77e2c6f27411c5df0845df))
* **api:** OpenAPI spec update via Stainless API ([9ae4e1b](https://github.com/togethercomputer/together-py/commit/9ae4e1bf74193c6cc8d1509f3b05d816e5e071b4))
* **api:** OpenAPI spec update via Stainless API ([#10](https://github.com/togethercomputer/together-py/issues/10)) ([af93a5c](https://github.com/togethercomputer/together-py/commit/af93a5c78aaf2b9bf7f3c42f7ff19e06472ae5de))
* **api:** OpenAPI spec update via Stainless API ([#3](https://github.com/togethercomputer/together-py/issues/3)) ([cd703fb](https://github.com/togethercomputer/together-py/commit/cd703fbdb178f4f05ffc43af0e86f5218537ce5c))
* **api:** OpenAPI spec update via Stainless API ([#4](https://github.com/togethercomputer/together-py/issues/4)) ([00ef6cc](https://github.com/togethercomputer/together-py/commit/00ef6cc33f844ef3d214e805f3bdfa28240905b7))
* **api:** OpenAPI spec update via Stainless API ([#5](https://github.com/togethercomputer/together-py/issues/5)) ([3e9827b](https://github.com/togethercomputer/together-py/commit/3e9827b08f2698029e31df3d770d7f873b9d610d))
* **api:** OpenAPI spec update via Stainless API ([#7](https://github.com/togethercomputer/together-py/issues/7)) ([6bab9da](https://github.com/togethercomputer/together-py/commit/6bab9dadd17cacd94565c8f4df25c0ea6f83e987))
* **api:** OpenAPI spec update via Stainless API ([#8](https://github.com/togethercomputer/together-py/issues/8)) ([a7584db](https://github.com/togethercomputer/together-py/commit/a7584db12d26cc55833ade61dae8ec29878d5ed1))
* **api:** OpenAPI spec update via Stainless API ([#9](https://github.com/togethercomputer/together-py/issues/9)) ([04877a0](https://github.com/togethercomputer/together-py/commit/04877a01b5a9dd3988ff8283c665fad4ca0c643a))
* **api:** rename api key ([b7b55e6](https://github.com/togethercomputer/together-py/commit/b7b55e632590fbe2425be79f332352ba8367e365))
* **api:** update via SDK Studio ([5866250](https://github.com/togethercomputer/together-py/commit/58662506963afd2ed777fa3efa9f35263689437c))
* **api:** update via SDK Studio ([27bbc3c](https://github.com/togethercomputer/together-py/commit/27bbc3c53d9e8849d7e7099bee417ef99260eece))
* **api:** update via SDK Studio ([f7c11ec](https://github.com/togethercomputer/together-py/commit/f7c11ecec9f83889385b710e8270f9159f013bb1))
* **api:** update via SDK Studio ([22a5f1f](https://github.com/togethercomputer/together-py/commit/22a5f1f01c5dea75a28763bcb991e5276ed9efa4))
* **api:** update via SDK Studio ([159534b](https://github.com/togethercomputer/together-py/commit/159534b4efeabd8f445037f38af6acd4342c7e7f))
* **api:** update via SDK Studio ([30663ec](https://github.com/togethercomputer/together-py/commit/30663ec91f215ba7135dd8723e2876cf1bf70dde))
* **api:** update via SDK Studio ([6561269](https://github.com/togethercomputer/together-py/commit/6561269416ba964bc0b2d452474017cd8036d666))
* **api:** update via SDK Studio ([72bad68](https://github.com/togethercomputer/together-py/commit/72bad68007c5e595fa65bcff9e268aca93cb0bef))
* **api:** update via SDK Studio ([59cce01](https://github.com/togethercomputer/together-py/commit/59cce011f234371b089e375cca57f9984ead2a8e))
* **api:** update via SDK Studio ([b2b0177](https://github.com/togethercomputer/together-py/commit/b2b017748247196d975cdbc51c4fe5bea23b5bbf))
* **api:** update via SDK Studio ([331cc46](https://github.com/togethercomputer/together-py/commit/331cc4626448b1e5546ae11c4bd0b90f106094c6))
* **api:** update via SDK Studio ([6a57974](https://github.com/togethercomputer/together-py/commit/6a57974a5ae311f3f0faa917191964c09579c7bd))
* **api:** update via SDK Studio ([80c35ee](https://github.com/togethercomputer/together-py/commit/80c35ee69b20f6a9b78512be0344e71e0850bb29))
* **api:** update via SDK Studio ([668c023](https://github.com/togethercomputer/together-py/commit/668c02366615c5b073b29b03e45ae17ffe668bca))
* **api:** update via SDK Studio ([a592cff](https://github.com/togethercomputer/together-py/commit/a592cffcc08f9831bdd414168b2e57b45ce42c08))
* **api:** update via SDK Studio ([733f0b0](https://github.com/togethercomputer/together-py/commit/733f0b0917d8627014c2106a510a4b1322fb8927))
* **api:** update via SDK Studio ([5095404](https://github.com/togethercomputer/together-py/commit/50954043bcc19bad0ffc23207e8074fcc83a6212))
* **api:** update via SDK Studio ([d3b6a64](https://github.com/togethercomputer/together-py/commit/d3b6a6403251badab836ff9a75d060afb97440cb))
* **api:** update via SDK Studio ([adf918b](https://github.com/togethercomputer/together-py/commit/adf918b5c13d36d086d42847a249df124cda119b))
* **api:** update via SDK Studio ([a79da8e](https://github.com/togethercomputer/together-py/commit/a79da8ea98ed471fc23af36c30696fb910cc6657))
* **api:** update via SDK Studio ([44b426f](https://github.com/togethercomputer/together-py/commit/44b426fca286acecfbe37b1cef802f40ba73496e))
* **api:** update via SDK Studio ([1f7c7fe](https://github.com/togethercomputer/together-py/commit/1f7c7fe55e6c728c97df57147f5ae9c072f76e3b))
* **api:** update via SDK Studio ([500e41b](https://github.com/togethercomputer/together-py/commit/500e41b1eb4c960d5e14fe069251ef887f0e4976))
* **api:** update via SDK Studio ([ca665ed](https://github.com/togethercomputer/together-py/commit/ca665edb80300b97e269976e3f966308afc50e4a))
* **api:** updates ([3591c56](https://github.com/togethercomputer/together-py/commit/3591c56336cd5a7cd98c23feed5ae5fc737bcafb))
* update via SDK Studio ([c56e7d1](https://github.com/togethercomputer/together-py/commit/c56e7d1b19533d687c1dd23d35118546699be8b7))
* update via SDK Studio ([90adf12](https://github.com/togethercomputer/together-py/commit/90adf128d816a262f51c4dcc4a39b6693c7c746f))
* update via SDK Studio ([b75aa7f](https://github.com/togethercomputer/together-py/commit/b75aa7f8c46573e6047abc7f9bd03bcc6d90cfe7))
* update via SDK Studio ([48c9e19](https://github.com/togethercomputer/together-py/commit/48c9e1941baade2916cd4bf56becc42e35052d3a))
* update via SDK Studio ([592853d](https://github.com/togethercomputer/together-py/commit/592853d727033ea9421ed58576ae15325aca535f))
* update via SDK Studio ([611badd](https://github.com/togethercomputer/together-py/commit/611baddd1f735c4287e052798812a23f61213717))
* update via SDK Studio ([a84defc](https://github.com/togethercomputer/together-py/commit/a84defc9ab5274d5eafc9190055083322b8fb93f))
* update via SDK Studio ([3c83f12](https://github.com/togethercomputer/together-py/commit/3c83f120ee2b10c4ec2c0e359eaf9f1968f85dcb))
* update via SDK Studio ([67d01b0](https://github.com/togethercomputer/together-py/commit/67d01b03b05ee598539b68d70185192862fb0a29))
* update via SDK Studio ([065b990](https://github.com/togethercomputer/together-py/commit/065b9903a0c0e9eb67a591d51abbb27e08020ef5))


### Chores

* go live ([#1](https://github.com/togethercomputer/together-py/issues/1)) ([9c9e672](https://github.com/togethercomputer/together-py/commit/9c9e67276776b7169bd2e9066c6049f5237ed044))
* update SDK settings ([e082ad6](https://github.com/togethercomputer/together-py/commit/e082ad6d7beff79ae5301f63d7b334aeebc12024))
