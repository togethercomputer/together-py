# Changelog

## [2.16.2](https://github.com/togethercomputer/together-py/compare/v2.16.1...v2.16.2) (2026-06-16)


### Bug Fixes

* **ci:** pass app token to every authenticated step in promote workflow ([1baa0a4](https://github.com/togethercomputer/together-py/commit/1baa0a4be94080fdc18907a589a45c6b263ecaba))
* use regular print for jig volumes progress update ([#395](https://github.com/togethercomputer/together-py/issues/395)) ([06d1776](https://github.com/togethercomputer/together-py/commit/06d1776cb2cdb68f618e5b56dadaeff452a6289e))


### Chores

* integrate production changes to staging repo ([#30](https://github.com/togethercomputer/together-py/issues/30)) ([f67f123](https://github.com/togethercomputer/together-py/commit/f67f123acf28094bc4ff3852905969f287e6de37))
* Log warning when uploading a file that already exists ([ee2cee5](https://github.com/togethercomputer/together-py/commit/ee2cee5fc44315d6679afd6b4897a15873e204e2))
* Update release-please token auth ([f77a46a](https://github.com/togethercomputer/together-py/commit/f77a46a7ca833abdafb52ebbc563e6d1a5a54749))
* update scripts to use github app ([#32](https://github.com/togethercomputer/together-py/issues/32)) ([#403](https://github.com/togethercomputer/together-py/issues/403)) ([83f978c](https://github.com/togethercomputer/together-py/commit/83f978cc932728ebe5ed0e121c649020ffe54ee0))
* update stlc-promote flow auth token ([09eb41a](https://github.com/togethercomputer/together-py/commit/09eb41aa92b049014a3cf5c484953d2395429206))

## [2.16.1](https://github.com/togethercomputer/together-py/compare/v2.16.0...v2.16.1) (2026-06-10)


### Chores

* Add staging CI syncing ([#5](https://github.com/togethercomputer/together-py/issues/5)) ([3e314e5](https://github.com/togethercomputer/together-py/commit/3e314e59c1db68d6379972a9a9d9fa1f4dd2be00))
* Add stlc promote action ([0dd26bd](https://github.com/togethercomputer/together-py/commit/0dd26bd284aedbcccd6ce4638e1e91953662c354))
* Add stlc promote action ([8f092fd](https://github.com/togethercomputer/together-py/commit/8f092fd95f72d3f62d0964ce1f6e861d9168930c))
* Fix lock files and type issue ([#4](https://github.com/togethercomputer/together-py/issues/4)) ([dd9b3cd](https://github.com/togethercomputer/together-py/commit/dd9b3cda988599ec29202368d63ac4d3e5ed5586))
* fix production repo reference ([d25fc13](https://github.com/togethercomputer/together-py/commit/d25fc13d1d4cd9bdfc911998dbe6e2ca4389fb37))
* Improve summary docs for remediations ([5bb4793](https://github.com/togethercomputer/together-py/commit/5bb479351550c5c84c1314634363ea5304bade8e))
* sync custom code ([985e12e](https://github.com/togethercomputer/together-py/commit/985e12e6ad061c67e79e67cc96342d950bb33853))

## 2.16.0 (2026-05-22)

Full Changelog: [v2.15.0...v2.16.0](https://github.com/togethercomputer/together-py/compare/v2.15.0...v2.16.0)

### Features

* **cli:** expose new cluster SDK parameters ([#378](https://github.com/togethercomputer/together-py/issues/378)) ([b694d8f](https://github.com/togethercomputer/together-py/commit/b694d8f261da15835257bb0352e1ba312b4127d3))


### Documentation

* **api:** add size and duration limits to file parameter in audio transcriptions/translations ([cce54f2](https://github.com/togethercomputer/together-py/commit/cce54f2362fd8dba1205eccf89f6909be74e2c37))

## 2.15.0 (2026-05-20)

Full Changelog: [v2.14.0...v2.15.0](https://github.com/togethercomputer/together-py/compare/v2.14.0...v2.15.0)

### Features

* **api:** add cluster config/OIDC/add-ons params, project filtering, update storage types ([9a8c60e](https://github.com/togethercomputer/together-py/commit/9a8c60eb51daba174c0a4761612b3dd51fb5bee5))
* **api:** add disable_position_bias_correction, remove num_samples from eval compare results ([27e6c2d](https://github.com/togethercomputer/together-py/commit/27e6c2db1e2549d8b2352f73265067f0eac9b44c))
* **api:** add h200-140gb gpu_type to jig deploy/update methods ([0f34ea4](https://github.com/togethercomputer/together-py/commit/0f34ea4e1441a08b014f19d99588902b17eda1be))
* **api:** add instance_name field to remediation model ([4c7fc66](https://github.com/togethercomputer/together-py/commit/4c7fc662363054f47d5e7a01353e3f0da98d8b6a))
* **api:** Add node remediation APIs to clusters sdks ([029c3fd](https://github.com/togethercomputer/together-py/commit/029c3fd79c22f130dab4a46bc62a6e1410908da4))
* **api:** add trigger param, support multiple modes in remediations list ([997deea](https://github.com/togethercomputer/together-py/commit/997deeae7c514b0ce2dc65394d262abe9bd35766))
* **api:** manual updates ([f4de411](https://github.com/togethercomputer/together-py/commit/f4de41192250b3c609e44da6bee18309db209f35))
* **api:** manual updates ([b5e42a0](https://github.com/togethercomputer/together-py/commit/b5e42a042c367dbe14021be3c6612155ac8f6fac))
* **cli:** add eval compare bias correction flag ([#375](https://github.com/togethercomputer/together-py/issues/375)) ([ac8482e](https://github.com/togethercomputer/together-py/commit/ac8482ebbf9fdf7e67973ff36a0178ce774963cb))
* **cli:** add get as alias for retrieve subcommands ([#367](https://github.com/togethercomputer/together-py/issues/367)) ([d283d11](https://github.com/togethercomputer/together-py/commit/d283d1192b1c75ad676420be4ea30137883d55a6))
* **cli:** add remediation list filters ([#372](https://github.com/togethercomputer/together-py/issues/372)) ([1656759](https://github.com/togethercomputer/together-py/commit/16567597382f3345aff0450bcf1a257976a97139))
* **jig:** copy and use uv.lock if exists on autogenerated dockerfile ([#370](https://github.com/togethercomputer/together-py/issues/370)) ([47e5c89](https://github.com/togethercomputer/together-py/commit/47e5c891ac2272b0d20c1c266d0e3a9527448019))
* Sync deployments OpenAPI spec ([1caa5fa](https://github.com/togethercomputer/together-py/commit/1caa5fa4c41dff79164d8edd7436e66747eab712))


### Bug Fixes

* **api:** make duration_days optional in clusters create, size_tib optional in storage update ([899752d](https://github.com/togethercomputer/together-py/commit/899752dbebed9a75433b9ab95245c3bf15237eb3))
* **api:** remove error field, make request_id required in jig queue submit response ([5ae0fbc](https://github.com/togethercomputer/together-py/commit/5ae0fbca3e592dafedc4638642582585f29098df))
* **api:** remove trigger parameter from remediations list method ([d6310d8](https://github.com/togethercomputer/together-py/commit/d6310d881cc12bb67132c9446d301d1663fd9f48))
* **jig:** honor uv default groups in autogenerated dockerfile ([#301](https://github.com/togethercomputer/together-py/issues/301)) ([85cf77b](https://github.com/togethercomputer/together-py/commit/85cf77b6dc8df8a4f5859deb543123195c484b5b))
* **types:** correct status field to enum in cluster_storage model ([2109f0a](https://github.com/togethercomputer/together-py/commit/2109f0a0c897a7d5659f700042ec97b0843b3228))
* **types:** remove node_name from ControlPlaneNode and GPUWorkerNode ([7a1a7c2](https://github.com/togethercomputer/together-py/commit/7a1a7c21f1cb0e898cf9c9cf12746964c5d1b978))


### Documentation

* **api:** add parameter descriptions to storage methods and types ([8c35457](https://github.com/togethercomputer/together-py/commit/8c35457b06dc6a58f0c1343accb8db09ad91b845))

## 2.14.0 (2026-05-12)

Full Changelog: [v2.13.0...v2.14.0](https://github.com/togethercomputer/together-py/compare/v2.13.0...v2.14.0)

### Features

* **api:** Integrate fine_tuning.list_metrics from stainless ([0d3a6da](https://github.com/togethercomputer/together-py/commit/0d3a6da0fd4c5f16c119e016b41de2be148c9f95))


### Chores

* temp deletion ([a42892c](https://github.com/togethercomputer/together-py/commit/a42892c12297d8e264c00c7c100551896fad87d9))
* temp undeletion ([462d3f3](https://github.com/togethercomputer/together-py/commit/462d3f3c234ae8b256e7ff965c10ee6708be09af))

## 2.13.0 (2026-05-11)

Full Changelog: [v2.12.0...v2.13.0](https://github.com/togethercomputer/together-py/compare/v2.12.0...v2.13.0)

### Features

* **api:** add max_tokens and temperature to eval judge parameters ([d35fb64](https://github.com/togethercomputer/together-py/commit/d35fb643b2cd5eff5ccb2b8b2c0eb4fbc8d30734))
* **internal/types:** support eagerly validating pydantic iterators ([852ef60](https://github.com/togethercomputer/together-py/commit/852ef60dc108bef4dc7e80ea528ca7823d7030d9))


### Bug Fixes

* **api:** remove task field from audio transcription/translation responses ([f34ac96](https://github.com/togethercomputer/together-py/commit/f34ac960a980dbb5750208ff27eae4abc283783a))
* **client:** add missing f-string prefix in file type error message ([d62050f](https://github.com/togethercomputer/together-py/commit/d62050fb50b4858ed32fa27d2024c7505d842946))
* **types:** constrain endpoint parameter to literals in batches ([cc61be0](https://github.com/togethercomputer/together-py/commit/cc61be030cc95d6a3d8e262ec47f7ceacfd2eb75))


### Chores

* Add example usage for clusters commands ([#360](https://github.com/togethercomputer/together-py/issues/360)) ([a357ed6](https://github.com/togethercomputer/together-py/commit/a357ed65e81e3b1a94c3e5e63c7d2d8840f3f421))
* Add example usage for file commands ([#359](https://github.com/togethercomputer/together-py/issues/359)) ([8d2a18b](https://github.com/togethercomputer/together-py/commit/8d2a18b2647585f4e83bd42c679e699c841cd545))
* Add example usage for model commands ([#358](https://github.com/togethercomputer/together-py/issues/358)) ([1316203](https://github.com/togethercomputer/together-py/commit/13162032b1ae100ecc7c1a08f454b30474f0a6b4))
* Add example usage to fine-tuning CLI help pages ([#357](https://github.com/togethercomputer/together-py/issues/357)) ([ad3cdb2](https://github.com/togethercomputer/together-py/commit/ad3cdb2d0d4f5511fa06105c4a7169cc72cf9306))
* Add examples to the CLI help output for endpoint commands ([#354](https://github.com/togethercomputer/together-py/issues/354)) ([f51b5e8](https://github.com/togethercomputer/together-py/commit/f51b5e8ec65be8cee2eef9270b1af55cbdc2cd91))
* Add help examples to evals commands ([#356](https://github.com/togethercomputer/together-py/issues/356)) ([0794576](https://github.com/togethercomputer/together-py/commit/0794576cd274a8a55240b3a1b780df8b23261a7c))
* Add usage examples for jig commands ([#361](https://github.com/togethercomputer/together-py/issues/361)) ([643286f](https://github.com/togethercomputer/together-py/commit/643286f390291ebb3e5fed85c4fb1dc5dd9cd981))
* Switch to an async version of DownloadManager ([#353](https://github.com/togethercomputer/together-py/issues/353)) ([c756670](https://github.com/togethercomputer/together-py/commit/c7566702fb57fcce808bb23ba1bc9b0737b9c352))


### Documentation

* **api:** add .ogg, .opus, .aac to supported formats in audio transcriptions/translations ([9c1211a](https://github.com/togethercomputer/together-py/commit/9c1211a8143dc435ef351dd57b9553d39ae06b8e))
* **api:** clarify prompt parameter support in audio transcriptions/translations ([9889ead](https://github.com/togethercomputer/together-py/commit/9889ead58a66864a37d01ef0bbe92b4bc8786ff5))
* **api:** reword docstrings to present tense across resources ([65c1756](https://github.com/togethercomputer/together-py/commit/65c175682f4f8432dfe4d880d6dc0a21acc46655))

## 2.12.0 (2026-05-01)

Full Changelog: [v2.11.0...v2.12.0](https://github.com/togethercomputer/together-py/compare/v2.11.0...v2.12.0)

### Features

* Add default retrieve handler when passing an id to commands ([#345](https://github.com/togethercomputer/together-py/issues/345)) ([984519c](https://github.com/togethercomputer/together-py/commit/984519c038d4b99a794b5665c5c74b7c22f8802c))
* add the pronunciation dict ([f59d672](https://github.com/togethercomputer/together-py/commit/f59d672d1f26abc9b4ad6216209b6d6707cfa88b))
* **api:** add cached_input field to Pricing model ([c03fb18](https://github.com/togethercomputer/together-py/commit/c03fb180dc52531e4c99ebcd2a2ca8acea81dc9b))
* **api:** Update server url to .ai ([2ea6a2d](https://github.com/togethercomputer/together-py/commit/2ea6a2d9201373c8959b4c34749236183a785543))
* ENG-87042: clarify TTS language parameter supports lowercase locales ([95cf65b](https://github.com/togethercomputer/together-py/commit/95cf65b30233791b1e73f823a3cb0e6cdb731ab4))
* ENG-87042: document language on TTS WebSocket and simplify locale note ([14b429f](https://github.com/togethercomputer/together-py/commit/14b429f0e08c8ad9eba4ffb51ba6d8d95d35973d))
* MOSH-2181: Add default note on max-seq-length ([b1edd58](https://github.com/togethercomputer/together-py/commit/b1edd58f1bc7ccc2f3b1016ac5d09eaf2fad16b3))
* Show cache input token pricing in models list cli output ([#350](https://github.com/togethercomputer/together-py/issues/350)) ([1476f70](https://github.com/togethercomputer/together-py/commit/1476f709115b23e6ca08468c4b0ca6e72553d967))


### Bug Fixes

* Properly handle unlinking temp file during fine-tuning download ([#352](https://github.com/togethercomputer/together-py/issues/352)) ([2f1c458](https://github.com/togethercomputer/together-py/commit/2f1c458ee388a14757c50b077e8402c0a063fe01))
* **types:** remove eval-sample, eval-output, eval-summary, batch-generated from FilePurpose ([ea1d61a](https://github.com/togethercomputer/together-py/commit/ea1d61a182cad4f11f0e123a23381284f61b2153))


### Chores

* Improve --json support accross multiple commands ([#347](https://github.com/togethercomputer/together-py/issues/347)) ([949bfa4](https://github.com/togethercomputer/together-py/commit/949bfa4514e34b761727622fab3d345e940a7fe9))
* **internal:** reformat pyproject.toml ([a52e64b](https://github.com/togethercomputer/together-py/commit/a52e64bde79ccfe3f06c9d4a59af5e736889e412))
* Pass agent name in request headers when detected ([#351](https://github.com/togethercomputer/together-py/issues/351)) ([1668cf4](https://github.com/togethercomputer/together-py/commit/1668cf4208e4c32c7ee91a6978b708bc8c4c8256))
* Update references from .xyz to .ai domain ([#349](https://github.com/togethercomputer/together-py/issues/349)) ([0c33450](https://github.com/togethercomputer/together-py/commit/0c334506cfb7f56a7cc8fb0bba4c4b89aed0b408))


### Documentation

* polish CLI help text; introduce Options + Global Options panels ([#346](https://github.com/togethercomputer/together-py/issues/346)) ([4905c1a](https://github.com/togethercomputer/together-py/commit/4905c1ac807de4b317639524720592d51b1d23f9))

## 2.11.0 (2026-04-28)

Full Changelog: [v2.10.0...v2.11.0](https://github.com/togethercomputer/together-py/compare/v2.10.0...v2.11.0)

### Features

* Add `ft` as shorthand for `fine-tuning` cli command ([#334](https://github.com/togethercomputer/together-py/issues/334)) ([8bcfa7d](https://github.com/togethercomputer/together-py/commit/8bcfa7d781900bde8ef907367673b67ad15fa82a))
* Add `ls` shorthand command for `list` commands in cli ([#341](https://github.com/togethercomputer/together-py/issues/341)) ([5d238d0](https://github.com/togethercomputer/together-py/commit/5d238d0a85c5918861c6d0fcbb025a2820ff616b))
* Add `ls` shorthand command for `list` commands in cli ([#341](https://github.com/togethercomputer/together-py/issues/341)) ([#342](https://github.com/togethercomputer/together-py/issues/342)) ([c8c8cc3](https://github.com/togethercomputer/together-py/commit/c8c8cc3f35b2435399bd0793e293be32b0e60e05))
* **api:** add h100-40gb-mig and b200-192gb GPU types to jig deploy/update ([f61e4d4](https://github.com/togethercomputer/together-py/commit/f61e4d4619ce00491b4acc7ad09f592f5d57d849))
* **api:** api update ([7f66bb5](https://github.com/togethercomputer/together-py/commit/7f66bb59173b97721856c4785a03292dace2c327))
* support setting headers via env ([02a83b8](https://github.com/togethercomputer/together-py/commit/02a83b8dba39652d55a7c338c32f2aada32fc89a))


### Bug Fixes

* **client:** update videos API base URL from .xyz to .ai domain ([bd71981](https://github.com/togethercomputer/together-py/commit/bd719810bedfeea9427e5cb92ae65dfcad2fe858))
* **cli:** replace console.print for print_json for json outputs ([#338](https://github.com/togethercomputer/together-py/issues/338)) ([ab219c1](https://github.com/togethercomputer/together-py/commit/ab219c145234027842550988c51cb61c32626982))
* Improve error sanitization to avoid logging sensitive data in telemetry ([#336](https://github.com/togethercomputer/together-py/issues/336)) ([4ec3f64](https://github.com/togethercomputer/together-py/commit/4ec3f6469423516c5d75d00c4f761d7cc1e33c82))
* Remove certain negative boolean flags that were added by cyclopts ([#333](https://github.com/togethercomputer/together-py/issues/333)) ([20b2dc9](https://github.com/togethercomputer/together-py/commit/20b2dc93b35cf3880b3656a9f4035c4fecf88124))
* Remove false positives with `files check` command in certain scenarios ([#335](https://github.com/togethercomputer/together-py/issues/335)) ([67f6338](https://github.com/togethercomputer/together-py/commit/67f6338d807baeb4804f9e021db0251da09a60b5))
* use correct field name format for multipart file arrays ([b1f783f](https://github.com/togethercomputer/together-py/commit/b1f783f8bd009b79317b7349e3c34c882a94b6c6))


### Chores

* Add `-c` as an alias for the create command ([#343](https://github.com/togethercomputer/together-py/issues/343)) ([f9d3fcb](https://github.com/togethercomputer/together-py/commit/f9d3fcb0faee82718190059ade699100e0f5bc96))
* Add empty state for ListTables ([#337](https://github.com/togethercomputer/together-py/issues/337)) ([2608dc6](https://github.com/togethercomputer/together-py/commit/2608dc62b0b1ef2bb38e26b15112f125436ea0e5))
* Remove warning emoji from beta commands help group ([#340](https://github.com/togethercomputer/together-py/issues/340)) ([3b07b78](https://github.com/togethercomputer/together-py/commit/3b07b78ab8871e7d7130cb43b269675f372fc527))


### Documentation

* **api:** document voice mixing for speech voice parameter ([15aab9c](https://github.com/togethercomputer/together-py/commit/15aab9c8ad0d3470bdea1e654127bcbd02e71c5c))
* **api:** update billing_type parameter description in clusters create ([5f84188](https://github.com/togethercomputer/together-py/commit/5f841887801827c8bd199cfe8c167cb14043a514))
* **api:** update response_encoding and sample_rate descriptions in audio speech ([bff30bd](https://github.com/togethercomputer/together-py/commit/bff30bd5034ffd182fdd9992adcd8aa2dff00506))

## 2.10.0 (2026-04-22)

Full Changelog: [v2.9.0...v2.10.0](https://github.com/togethercomputer/together-py/compare/v2.9.0...v2.10.0)

### Features

* Major CLI foundational improvements ([#319](https://github.com/togethercomputer/together-py/issues/319)) ([5e0004a](https://github.com/togethercomputer/together-py/commit/5e0004ab7c96f368d62603e0b2fb392988dd6c5e))


### Chores

* **internal:** more robust bootstrap script ([d847567](https://github.com/togethercomputer/together-py/commit/d847567402ac92d3adb3bc8a9d0cf9532726a2e1))

## 2.9.0 (2026-04-17)

Full Changelog: [v2.8.0...v2.9.0](https://github.com/togethercomputer/together-py/compare/v2.8.0...v2.9.0)

### Features

* **api:** add max_seq_length to fine-tuning response models ([cfb6497](https://github.com/togethercomputer/together-py/commit/cfb64972ee879c74c777f5a7a85fc2903a152b58))


### Bug Fixes

* **jig:** removing command from jig configs doesn't disable it ([#316](https://github.com/togethercomputer/together-py/issues/316)) ([81f81b5](https://github.com/togethercomputer/together-py/commit/81f81b53d086694aa6382a2bc2be62d7cf0b728d))


### Performance Improvements

* **client:** optimize file structure copying in multipart requests ([4704a44](https://github.com/togethercomputer/together-py/commit/4704a44deb86f6fd6a688bd8cbff0bf03af8694f))


### Chores

* **jig:** deprecate tool.jig.autoscaling ([#328](https://github.com/togethercomputer/together-py/issues/328)) ([e41f4ef](https://github.com/togethercomputer/together-py/commit/e41f4ef71a35bf6fc65ca6643773062667aed22f))
* **tests:** bump steady to v0.22.1 ([acc8e35](https://github.com/togethercomputer/together-py/commit/acc8e35bfbc6910ad2b8df51f74a638296d7646e))

## 2.8.0 (2026-04-13)

Full Changelog: [v2.7.0...v2.8.0](https://github.com/togethercomputer/together-py/compare/v2.7.0...v2.8.0)

### Features

* **api:** accept strings for audio_inputs and source_video in video creation ([0b43374](https://github.com/togethercomputer/together-py/commit/0b43374a8b98ae44ed69fdcb2c60019304b647f9))
* **api:** add autoscale/OIDC/scheduling to clusters, replace driver_version params ([d1bd7b8](https://github.com/togethercomputer/together-py/commit/d1bd7b85cb373427c3240b6b3bac19c912ed8af8))
* **api:** add num_workers parameter to eval create parameters ([76ffcac](https://github.com/togethercomputer/together-py/commit/76ffcacd3dcd8af7de0d09232230e6ea322343ec))
* **api:** add RegionDriverVersion model, update cluster regions response types ([8151d02](https://github.com/togethercomputer/together-py/commit/8151d02fd2f5272d334e40ef03a60056d554eb3a))
* **api:** manual updates ([cec7a40](https://github.com/togethercomputer/together-py/commit/cec7a405e111c6a90cc5a6e8116dd94cc2c39913))
* **cli:** Add Analytic tracking to CLI commands ([#224](https://github.com/togethercomputer/together-py/issues/224)) ([7362cdc](https://github.com/togethercomputer/together-py/commit/7362cdcbf1535a276e7b8c431ac1c49b0c094c67))
* **jig:** jig secrets delete cmd to delete secret from remote and local ([#324](https://github.com/togethercomputer/together-py/issues/324)) ([227ae2f](https://github.com/togethercomputer/together-py/commit/227ae2f63a1d2b888496deaf3671f2953591e5bc))


### Bug Fixes

* **client:** preserve hardcoded query params when merging with user params ([1f900b6](https://github.com/togethercomputer/together-py/commit/1f900b69661ae3e7ded9545d7eee8f27bd4bfd63))
* ensure file data are only sent as 1 parameter ([2f95a88](https://github.com/togethercomputer/together-py/commit/2f95a88714e403bb74a00a905418b16fed7597d8))
* Ensure jig works with Python 3.9 ([#321](https://github.com/togethercomputer/together-py/issues/321)) ([e28b54a](https://github.com/togethercomputer/together-py/commit/e28b54af9f3ccf19f020c1bbaa48272ee27bfb83))


### Chores

* Update `clusters list-regions` output for new server response change ([#322](https://github.com/togethercomputer/together-py/issues/322)) ([329cf40](https://github.com/togethercomputer/together-py/commit/329cf40057bb85f23737549d79fd546fe01c9d41))


### Documentation

* improve examples ([07892d2](https://github.com/togethercomputer/together-py/commit/07892d276446615b7c0fdb109dd2b5201c16980f))

## 2.7.0 (2026-04-03)

Full Changelog: [v2.6.0...v2.7.0](https://github.com/togethercomputer/together-py/compare/v2.6.0...v2.7.0)

### Features

* **api:** add generate_audio, image_reference, media params to videos.create ([b2c5ca7](https://github.com/togethercomputer/together-py/commit/b2c5ca776fa2520e99b4e7c6de8bd1421b4de33f))

## 2.6.0 (2026-03-31)

Full Changelog: [v2.5.0...v2.6.0](https://github.com/togethercomputer/together-py/compare/v2.5.0...v2.6.0)

### Features

* [jig] updated created_at, updated_at format to datetime ([#310](https://github.com/togethercomputer/together-py/issues/310)) ([5a27da9](https://github.com/togethercomputer/together-py/commit/5a27da92da7199057d5c1a1c2749044cb325b269))
* **api:** add bit_rate parameter to speech create method ([e447ab6](https://github.com/togethercomputer/together-py/commit/e447ab6b6714e6615bd7285f53bc6a8f71a6edf8))
* **api:** add random_seed field to fine_tuning cancel and list responses ([57dcc89](https://github.com/togethercomputer/together-py/commit/57dcc89748da91dc5e5b70bc24b9e43702fd51ab))
* **internal:** implement indices array format for query and form serialization ([f896e54](https://github.com/togethercomputer/together-py/commit/f896e543c6df5db1657a6ad5ba91925a7d582768))


### Bug Fixes

* **jig:** conditionally install pyproject.toml dependancies in dockerfile only if pyproject.toml is available ([#314](https://github.com/togethercomputer/together-py/issues/314)) ([e06478c](https://github.com/togethercomputer/together-py/commit/e06478cc88c03bfb1915c6bb1e19d1b955bd7065))
* sanitize endpoint path params ([c445ed8](https://github.com/togethercomputer/together-py/commit/c445ed815d6209356ae033cb8408f959fe57c502))
* **types:** correct gpu_type literal in jig, timestamp types in deployment ([ef08cec](https://github.com/togethercomputer/together-py/commit/ef08cec1c13209592ad8547606c2363292589ff0))


### Chores

* **ci:** skip lint on metadata-only changes ([d22b49f](https://github.com/togethercomputer/together-py/commit/d22b49f397c4d9b79290c37f0840eee2b2d3ffea))
* Disable translation test temporarily ([#313](https://github.com/togethercomputer/together-py/issues/313)) ([4c2075d](https://github.com/togethercomputer/together-py/commit/4c2075ddb818c5d156734c851abd3ae28a865a95))
* **internal:** regenerate SDK with no functional changes ([e541c40](https://github.com/togethercomputer/together-py/commit/e541c4017882f28c00dbf711cf6ecba050deef6f))
* **internal:** update gitignore ([6c7113e](https://github.com/togethercomputer/together-py/commit/6c7113e73c0dab048935c14b48f5a7c27501ef33))
* **tests:** bump steady to v0.19.4 ([f2583ae](https://github.com/togethercomputer/together-py/commit/f2583aeb228f05440305b05d03c1b1e1a5926f2a))
* **tests:** bump steady to v0.19.5 ([e8de9f6](https://github.com/togethercomputer/together-py/commit/e8de9f612adbfc2d1612103c87ae5fd5242de766))
* **tests:** bump steady to v0.19.6 ([3f935af](https://github.com/togethercomputer/together-py/commit/3f935afab8e7714da23490d89752515b7ab37ad9))
* **tests:** bump steady to v0.19.7 ([859e9ba](https://github.com/togethercomputer/together-py/commit/859e9ba7b53111631abe46ec0c19c0556162c8f2))
* **tests:** bump steady to v0.20.1 ([a4b6f3d](https://github.com/togethercomputer/together-py/commit/a4b6f3d2472231dda03c4a776bfdebcf21de1fc9))
* **tests:** bump steady to v0.20.2 ([b38453b](https://github.com/togethercomputer/together-py/commit/b38453bac5db8f1c34e1ea945c60a0bb68a632eb))


### Documentation

* **api:** update voice parameter documentation URL in speech ([fe89657](https://github.com/togethercomputer/together-py/commit/fe896570536c106938c4dc1f7585b590bb2913be))


### Refactors

* **tests:** switch from prism to steady ([0b4c343](https://github.com/togethercomputer/together-py/commit/0b4c343fb6f72a4fda7593bdf6ea133cfad1ca29))

## 2.5.0 (2026-03-18)

Full Changelog: [v2.4.0...v2.5.0](https://github.com/togethercomputer/together-py/compare/v2.4.0...v2.5.0)

### Features

* **api:** manual updates ([9db2163](https://github.com/togethercomputer/together-py/commit/9db2163681520a95a54e03472ed6719abc40dc05))
* **api:** manual updates ([a3436ea](https://github.com/togethercomputer/together-py/commit/a3436ea1f04273a0d91103cbd850136854389794))
* **api:** manual updates ([ca7f97d](https://github.com/togethercomputer/together-py/commit/ca7f97de14718352cb990c281d3fa053e954fc42))
* Update llama 3.1 8b w/ qwen 3.5 9b ([0680858](https://github.com/togethercomputer/together-py/commit/0680858c6f88e9e8ad72c76dc6d374e5074e12a2))


### Bug Fixes

* **deps:** bump minimum typing-extensions version ([94c9632](https://github.com/togethercomputer/together-py/commit/94c96328c13e6955f777e4c6a3517744b84a1d23))
* **jig:** use Together.get instead of Together._client.get so that registry errors are handled correctly ([#302](https://github.com/togethercomputer/together-py/issues/302)) ([aefd483](https://github.com/togethercomputer/together-py/commit/aefd483f7c335232fe798be6f92f52a960f70e88))
* **pydantic:** do not pass `by_alias` unless set ([dca687e](https://github.com/togethercomputer/together-py/commit/dca687e39cf86f80cfd051e4e1596e8f54753968))
* **types:** remove model enum constraint in chat completions ([c30e2a0](https://github.com/togethercomputer/together-py/commit/c30e2a0929888955fe7bae94f38a024ff0a601ed))


### Chores

* Fix unit tests with recent model deprecations ([#305](https://github.com/togethercomputer/together-py/issues/305)) ([28902b4](https://github.com/togethercomputer/together-py/commit/28902b4f67f0f5158ea09589fe63de5e51efc9b7))
* **internal:** tweak CI branches ([556c449](https://github.com/togethercomputer/together-py/commit/556c4491ed2c1ad39f4d587db2c25d94dd210192))

## 2.4.0 (2026-03-11)

Full Changelog: [v2.3.2...v2.4.0](https://github.com/togethercomputer/together-py/compare/v2.3.2...v2.4.0)

### Features

* **jig:** move config.dockerfile to config.image.dockerfile_path and add an config.deploy.image option so that you don't have to always pass it as a flag ([#287](https://github.com/togethercomputer/together-py/issues/287)) ([16f64a5](https://github.com/togethercomputer/together-py/commit/16f64a58d8b83f137474ea3eabb31abdc7d38a5f))


### Bug Fixes

* fix autoscaling config usage in jig ([#298](https://github.com/togethercomputer/together-py/issues/298)) ([a3b6657](https://github.com/togethercomputer/together-py/commit/a3b6657efb440bed6cc9f722e54bffd264a95270))
* fixed autoscaling configs in deployments api ([d31204c](https://github.com/togethercomputer/together-py/commit/d31204c3e78340bb362ec8b44da9ee8b09e8f6ac))
* **jig:** deployment tracking ([#300](https://github.com/togethercomputer/together-py/issues/300)) ([f80a2b0](https://github.com/togethercomputer/together-py/commit/f80a2b05ec9c5d917a5a327ac002e44dddd96b84))
* **jig:** send {} for deployment autoscaling to unset if unset in config ([#294](https://github.com/togethercomputer/together-py/issues/294)) ([7657de3](https://github.com/togethercomputer/together-py/commit/7657de3ccc5ef077f8b413f67399d35724af21fd))


### Chores

* fix lints ([#299](https://github.com/togethercomputer/together-py/issues/299)) ([2b35ec4](https://github.com/togethercomputer/together-py/commit/2b35ec46fa2414b14b589b16781c42990e697dd4))

## 2.3.2 (2026-03-09)

Full Changelog: [v2.3.1...v2.3.2](https://github.com/togethercomputer/together-py/compare/v2.3.1...v2.3.2)

### Bug Fixes

* Address pydantic validation error on file literal ([#291](https://github.com/togethercomputer/together-py/issues/291)) ([ecb8e7d](https://github.com/togethercomputer/together-py/commit/ecb8e7d1c7a3eda011c214fa5931c916ef188ad0))

## 2.3.1 (2026-03-09)

Full Changelog: [v2.3.0...v2.3.1](https://github.com/togethercomputer/together-py/compare/v2.3.0...v2.3.1)

### Bug Fixes

* Improve multipart file uploads ([#290](https://github.com/togethercomputer/together-py/issues/290)) ([b27d19c](https://github.com/togethercomputer/together-py/commit/b27d19c7d789fbdcd54a5aa47872a8c425ea3e47))
* **jig:** compile cache should be owned by current user instead of root so cleanup works ([504717e](https://github.com/togethercomputer/together-py/commit/504717e21983ba7523326b7dafa64dd6b6fecb8d))


### Chores

* **ci:** skip uploading artifacts on stainless-internal branches ([e7d23c3](https://github.com/togethercomputer/together-py/commit/e7d23c36df459a47276f33b615301e8160231c32))
* update placeholder string ([9b0a5b9](https://github.com/togethercomputer/together-py/commit/9b0a5b984f4fe74ab8967e0a6dfe620b203b309a))

## 2.3.0 (2026-03-05)

Full Changelog: [v2.2.0...v2.3.0](https://github.com/togethercomputer/together-py/compare/v2.2.0...v2.3.0)

### Features

* Add typing for completion responses related to logprobs ([d81683a](https://github.com/togethercomputer/together-py/commit/d81683af427008e471ea9b4a26348a143db2ac9b))
* Another try ([d16cbaa](https://github.com/togethercomputer/together-py/commit/d16cbaa208ec913b14e6784b36078d783397614d))
* **cli:** Add --json to `fine-tuning retrieve` ([#272](https://github.com/togethercomputer/together-py/issues/272)) ([b9bb6e0](https://github.com/togethercomputer/together-py/commit/b9bb6e0188373ee882781d0259327985103abcfc))
* update deployments schemas to include volume versions ([b4dfb3d](https://github.com/togethercomputer/together-py/commit/b4dfb3dc9228fd3885b5e3169693c8d753ecd1d3))
* Update training type for price estimation too ([a430a3a](https://github.com/togethercomputer/together-py/commit/a430a3a87961d2bc7cf5745efcd539d843b0bc7a))


### Bug Fixes

* **cli:** Improve error output message when model/checkpoint is not provided in finetune create ([#271](https://github.com/togethercomputer/together-py/issues/271)) ([bae0065](https://github.com/togethercomputer/together-py/commit/bae00658a55f112e5f5d9a548b379129ed1d5f2c))
* **cli:** Improve output when downloading an incomplete finetune job ([#273](https://github.com/togethercomputer/together-py/issues/273)) ([eae629e](https://github.com/togethercomputer/together-py/commit/eae629e457d4433974c1ccd75012684a962b3f42))
* jig autoscaling config should be nullable ([#286](https://github.com/togethercomputer/together-py/issues/286)) ([589215f](https://github.com/togethercomputer/together-py/commit/589215f6187fbefc3222ce42c20b856d552d979a))
* **jig:** minor improvements ([#283](https://github.com/togethercomputer/together-py/issues/283)) ([98cb9fb](https://github.com/togethercomputer/together-py/commit/98cb9fb9948a5b9b33f7d963531328f9cb46779d))
* remove dependency from .jig.json managing setting secrets ([#282](https://github.com/togethercomputer/together-py/issues/282)) ([5470ade](https://github.com/togethercomputer/together-py/commit/5470ade6a6488f2de970ab93be1620b9a4483afb))
* use volume version metadata when updating volumes ([#279](https://github.com/togethercomputer/together-py/issues/279)) ([20304af](https://github.com/togethercomputer/together-py/commit/20304afd4e7d9b19804e85c1939cd24dd764ab3a))


### Chores

* **ci:** bump uv version ([8b138b5](https://github.com/togethercomputer/together-py/commit/8b138b5d12cd00f1f03b75dc43d0543f71efa424))
* **cli:** Improve output for `fine-tuning list` and `files list` commands ([#274](https://github.com/togethercomputer/together-py/issues/274)) ([a73f525](https://github.com/togethercomputer/together-py/commit/a73f525550fa19268c1e222076e0618345ca3910))
* **cli:** Improve output for file uploads and fine-tuning create ([#277](https://github.com/togethercomputer/together-py/issues/277)) ([089d4b9](https://github.com/togethercomputer/together-py/commit/089d4b9705b3f01fc1de67c395ada62dd69c21b7))
* **internal:** add request options to SSE classes ([174bf4d](https://github.com/togethercomputer/together-py/commit/174bf4dd0c704ad2744d294ae6cb5ed4c9099bee))
* **internal:** make `test_proxy_environment_variables` more resilient ([eb89afd](https://github.com/togethercomputer/together-py/commit/eb89afdd88624b69df0cf27a8aeff85ba2071812))
* **internal:** make `test_proxy_environment_variables` more resilient to env ([0bf71ae](https://github.com/togethercomputer/together-py/commit/0bf71ae8af070a04d6257e7fbe5c10faccd18f13))
* **test:** do not count install time for mock server timeout ([bbf3f2d](https://github.com/togethercomputer/together-py/commit/bbf3f2d858f6cb93def57e39472ce21c724a0e6b))

## 2.2.0 (2026-02-19)

Full Changelog: [v2.1.1...v2.2.0](https://github.com/togethercomputer/together-py/compare/v2.1.1...v2.2.0)

### Features

* **cli:** Add json mode to `fine-tuning list --json` ([#269](https://github.com/togethercomputer/together-py/issues/269)) ([13d3551](https://github.com/togethercomputer/together-py/commit/13d35511bb039b3053ecf3e7a90c04e2e2d91237))
* Improve file uploads and FT create flows with checksums ([#253](https://github.com/togethercomputer/together-py/issues/253)) ([3095b9a](https://github.com/togethercomputer/together-py/commit/3095b9af2ba564cefe6b64a7ee65450aacfbfa4c))
* Update descriptions for endpoints ([70900c6](https://github.com/togethercomputer/together-py/commit/70900c6da2e8f60bfd0f70a5497cf41c18008ee5))


### Bug Fixes

* **cli:** fine-tuning create regression ([#270](https://github.com/togethercomputer/together-py/issues/270)) ([59d0c33](https://github.com/togethercomputer/together-py/commit/59d0c3399643c42e1c6ee9cf74c70aa99104218c))


### Chores

* Add documentation and changelog to project.urls ([#264](https://github.com/togethercomputer/together-py/issues/264)) ([7b9e574](https://github.com/togethercomputer/together-py/commit/7b9e5749e448042f548a0fbcd5db5ff5bfbb99d7))
* Better jig deployment progress ([#242](https://github.com/togethercomputer/together-py/issues/242)) ([ba9c50a](https://github.com/togethercomputer/together-py/commit/ba9c50a8b9855ec95e871525a33932e46f470379))
* **cli:** Improve messaging when attempting to cancel finetune that is not cancellable ([#268](https://github.com/togethercomputer/together-py/issues/268)) ([6502acc](https://github.com/togethercomputer/together-py/commit/6502acc911413abceff3870f620a2bed742e9b08))
* configure new SDK language ([b312b50](https://github.com/togethercomputer/together-py/commit/b312b502fcff52aa3b877e03928ef6f5a34ed88a))
* Fix various docstrings ([2e1bd13](https://github.com/togethercomputer/together-py/commit/2e1bd13a49a1ddeb717c072e3b4a4e4c1669f2de))
* format all `api.md` files ([c16f892](https://github.com/togethercomputer/together-py/commit/c16f89205ebc2a371dfa468bfb9b3b1081e41a4f))
* format files ([#266](https://github.com/togethercomputer/together-py/issues/266)) ([2a452df](https://github.com/togethercomputer/together-py/commit/2a452df565a93a32963c615a5be3eb23a2e6b713))
* Refactor argument options with CLI file downloads ([#267](https://github.com/togethercomputer/together-py/issues/267)) ([642adbd](https://github.com/togethercomputer/together-py/commit/642adbda9f113bf815d63b90a9829367c4fac82e))
* Remove broken field LineCount from FileResponse ([778a7d9](https://github.com/togethercomputer/together-py/commit/778a7d9e61f1f69feff51a5c908a1d2221e8133d))
* Remove line_count field from files sdks/clis ([#265](https://github.com/togethercomputer/together-py/issues/265)) ([62c9da6](https://github.com/togethercomputer/together-py/commit/62c9da6efd0c8e8c5f686b45736b8765030e5e5f))
* Revert adding mcp code. Code additions were unexpected. ([7a322f7](https://github.com/togethercomputer/together-py/commit/7a322f7f3388149418e3a576d93cb0017f5fdecd))
* update mock server docs ([5bcfbdf](https://github.com/togethercomputer/together-py/commit/5bcfbdf4cd2ff84de834c8df0ecdccb18cac1e35))

## 2.1.1 (2026-02-12)

Full Changelog: [v2.1.0...v2.1.1](https://github.com/togethercomputer/together-py/compare/v2.1.0...v2.1.1)

### Bug Fixes

* **cli:** handle None model.type in 'together models list' sort ([9c17a0c](https://github.com/togethercomputer/together-py/commit/9c17a0c873264e30ee217edc43269f3c8f8d4990))


### Chores

* **internal:** fix lint error on Python 3.14 ([c66238c](https://github.com/togethercomputer/together-py/commit/c66238c18b21eaa8aa6184bbfb2fc1242d270b6f))

## 2.1.0 (2026-02-10)

Full Changelog: [v2.0.0...v2.1.0](https://github.com/togethercomputer/together-py/compare/v2.0.0...v2.1.0)

### Features

* **cli:** improve error messages for endpoint creation failures ([#230](https://github.com/togethercomputer/together-py/issues/230)) ([0285a69](https://github.com/togethercomputer/together-py/commit/0285a69893688938068d235aa109a5d7678cb713))
* jig support for multi deployment ([d1165fd](https://github.com/togethercomputer/together-py/commit/d1165fd786533e37ed401f4bb60601b39473a5d8))


### Bug Fixes

* **cli:** fine-tuning retrieve now renders data instead of schema ([#250](https://github.com/togethercomputer/together-py/issues/250)) ([52cde25](https://github.com/togethercomputer/together-py/commit/52cde258d39644a5a9706fc8f491c951115aa16d))
* **jig:** lint errors ([07f4d34](https://github.com/togethercomputer/together-py/commit/07f4d340ebd24247d0d280ce53cac768f76e03b8))
* **jig:** migrate old state files properly and be even more defensive about parsing deploy errors ([92ef79b](https://github.com/togethercomputer/together-py/commit/92ef79b4229953d8e463bebe8027420c8e8decfe))
* **jig:** pyright does not handle isinstance type narrowing in ternary expressions. also fix migration logic ([bf5267f](https://github.com/togethercomputer/together-py/commit/bf5267ff65fa409c21d3ac92e794dfd83f70c300))
* remove hardcoded API key from image example ([#254](https://github.com/togethercomputer/together-py/issues/254)) ([8f2c60c](https://github.com/togethercomputer/together-py/commit/8f2c60c8fa4c2352e5768aa47876dd51b379df6b))


### Chores

* **internal:** bump dependencies ([c9678ff](https://github.com/togethercomputer/together-py/commit/c9678ff922fa549261c5db2af5be60f719e6a1cf))
* Update descriptions for jig queue methods and properties ([23be158](https://github.com/togethercomputer/together-py/commit/23be1581cf1986bf4e9474e70f6e1029bc082ec4))

## 2.0.0 (2026-02-04)

Full Changelog: [v2.0.0-alpha.20...v2.0.0](https://github.com/togethercomputer/together-py/compare/v2.0.0-alpha.20...v2.0.0)

### Features

* **api:** Publish 2.0 Stable ([213f5c1](https://github.com/togethercomputer/together-py/commit/213f5c173bbe98c4ee80bd19a96e0a59bbbc236a))

## 2.0.0-alpha.20 (2026-02-04)

Full Changelog: [v2.0.0-alpha.19...v2.0.0-alpha.20](https://github.com/togethercomputer/together-py/compare/v2.0.0-alpha.19...v2.0.0-alpha.20)

### Features

* ENG-82904 - chore: update ReplicaEvent schema ([21d143c](https://github.com/togethercomputer/together-py/commit/21d143c457b73cd3042ca9c81acb9a660c41c7bc))
* Improve error handling and messaging when api key is missing in CLI usage ([#231](https://github.com/togethercomputer/together-py/issues/231)) ([cc16ba6](https://github.com/togethercomputer/together-py/commit/cc16ba6bb7bad823fc9c5b946a5de118e68753bb))
* simplify cli endpoints usability ([#233](https://github.com/togethercomputer/together-py/issues/233)) ([4649e95](https://github.com/togethercomputer/together-py/commit/4649e956f17ef8aa1126a7c5c19d3593e11ec1e1))


### Bug Fixes

* **jig:** fix jig submit response showing request_id and requestId ([#240](https://github.com/togethercomputer/together-py/issues/240)) ([0518b99](https://github.com/togethercomputer/together-py/commit/0518b99925be3ed30bee9e3a62fdbaac6bf5e174))
* **jig:** print raw json response for retrieve commands in order to maintain the same order ([#234](https://github.com/togethercomputer/together-py/issues/234)) ([15324d7](https://github.com/togethercomputer/together-py/commit/15324d7505df908a683d8b9c303a43a3efdcf40d))
* **jig:** replace pprint with click.echo ([67281e7](https://github.com/togethercomputer/together-py/commit/67281e7ef2601f8923230454db2540955c8753d8))


### Chores

* cleanup ([3511302](https://github.com/togethercomputer/together-py/commit/351130273cb5d1e388401d96ce06f2076800c244))


### Documentation

* Add jig documentation ([9bb2454](https://github.com/togethercomputer/together-py/commit/9bb2454678b9ce8ae6de306195bc2052097d2029))

## 2.0.0-alpha.19 (2026-02-03)

Full Changelog: [v2.0.0-alpha.18...v2.0.0-alpha.19](https://github.com/togethercomputer/together-py/compare/v2.0.0-alpha.18...v2.0.0-alpha.19)

### Features

* internal: Add code samples to deployments features ([eaa20a5](https://github.com/togethercomputer/together-py/commit/eaa20a59aa3bf1d48026f0018060ef6b34d7b50d))


### Chores

* **api:** move hardware listing feature under endpoints resource. ([ac6671a](https://github.com/togethercomputer/together-py/commit/ac6671a36b1c41374e7d491a37e7086718972e20))
* Fix CLI ([5d89415](https://github.com/togethercomputer/together-py/commit/5d8941523300914c62e4f97d354cdff664445517))
* run internal foramt ([45ef6b3](https://github.com/togethercomputer/together-py/commit/45ef6b3d97a49108f02eeeb4ec856bd7c352fd75))

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
