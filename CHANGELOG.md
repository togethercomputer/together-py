# Changelog

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
