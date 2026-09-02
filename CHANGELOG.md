# Changelog

## [2.33.0](https://github.com/togethercomputer/together-py/compare/v2.32.0...v2.33.0) (2026-09-02)


### Features

* **cli:** add `list`/`delete` aliases for beta endpoints `ls`/`rm` (ENG-92294) ([#538](https://github.com/togethercomputer/together-py/issues/538)) ([b071670](https://github.com/togethercomputer/together-py/commit/b0716705a031bb9a34aa95717149722461a72e7e))
* **CLI:** add `tg batches` commands for the batch API ([#525](https://github.com/togethercomputer/together-py/issues/525)) ([013976d](https://github.com/togethercomputer/together-py/commit/013976dd92b9cb0ebb8d0e0a0f7e1a5b9b12d116))
* **cli:** introduce ExperimentalConfig for experimental opt-in features in jig ([#543](https://github.com/togethercomputer/together-py/issues/543)) ([d653373](https://github.com/togethercomputer/together-py/commit/d6533731a811be30966ea9233d0322cf14120ca4))
* **endpoints:** List enum values for endpoint scaling metric values ([be959b2](https://github.com/togethercomputer/together-py/commit/be959b278bd07913aa7f76b096f68e8ddb12d302))
* ENG-92086 - call prewarm API after volume upload and image build ([#535](https://github.com/togethercomputer/together-py/issues/535)) ([b436f0c](https://github.com/togethercomputer/together-py/commit/b436f0ce35aa9001ee02b2eb5e2cf28346e54b6a))
* **Evals CLI:** show files upload progress during evals create ([#534](https://github.com/togethercomputer/together-py/issues/534)) ([37ddff1](https://github.com/togethercomputer/together-py/commit/37ddff1fd7c5f313cde527adcf0c37a816a1b605))
* expose RL GPU configurations in OpenAPI ([91b508a](https://github.com/togethercomputer/together-py/commit/91b508a182555166da33d0c02c3d9d31ea7261f3))
* expose RL session policy state ([e83ef66](https://github.com/togethercomputer/together-py/commit/e83ef663f896cc6d9dd88c87a0b5755b81217f6d))
* **rl:** add forward-backward loss function outputs ([c6d8f3b](https://github.com/togethercomputer/together-py/commit/c6d8f3bcb63caf6b8e4ae16b6c44107b2fc8d7c8))


### Bug Fixes

* **cli:** preserve endpoint API failure diagnostics ([#537](https://github.com/togethercomputer/together-py/issues/537)) ([ba27d45](https://github.com/togethercomputer/together-py/commit/ba27d450eae86f4eafb9d91e8191a0863af9142c))
* **cli:** preserve endpoint creation diagnostics ([#541](https://github.com/togethercomputer/together-py/issues/541)) ([4641ddf](https://github.com/togethercomputer/together-py/commit/4641ddf3b624322bcd5456628549305069b6e463))
* **cli:** preserve endpoint deletion failure diagnostics ([#533](https://github.com/togethercomputer/together-py/issues/533)) ([6c706ae](https://github.com/togethercomputer/together-py/commit/6c706aedea354a404a0cc5155bf16ffc315f4b01))
* **cli:** preserve missing argument diagnostics ([#549](https://github.com/togethercomputer/together-py/issues/549)) ([d98ddc1](https://github.com/togethercomputer/together-py/commit/d98ddc1b539e28a8506d63de881508bbf01d4745))
* **cli:** remove --scale-to-zero-window from beta endpoints ([#545](https://github.com/togethercomputer/together-py/issues/545)) ([53710f9](https://github.com/togethercomputer/together-py/commit/53710f97d178523b37b87800aee449749b0a9424))
* **cli:** show upload progress for batch submit ([#546](https://github.com/togethercomputer/together-py/issues/546)) ([5b23e37](https://github.com/togethercomputer/together-py/commit/5b23e375d3e4436821476f2f29e6fbb544a00d88))
* **cli:** stabilize UnknownOptionError telemetry ([#539](https://github.com/togethercomputer/together-py/issues/539)) ([23c3498](https://github.com/togethercomputer/together-py/commit/23c34988cdc351b705a5dee85f2f21da2c8e4d84))
* **Finetuning CLI:** remove broken pagination on `list-events` command ([#540](https://github.com/togethercomputer/together-py/issues/540)) ([cd8018d](https://github.com/togethercomputer/together-py/commit/cd8018ddb910b66e8c62ade30034c3314487af0f))


### Chores

* **cli:** drop `tqdm` dependency (DX-458) ([#523](https://github.com/togethercomputer/together-py/issues/523)) ([479dd6a](https://github.com/togethercomputer/together-py/commit/479dd6aec61141b18ff2b8da419846d9f9eec6cd))


### Documentation

* **openapi:** sync rollout landing floor descriptions ([222b48a](https://github.com/togethercomputer/together-py/commit/222b48a887c623285a1e1ddebf817206badb55ea))
* sync rollout final target semantics ([be0aa66](https://github.com/togethercomputer/together-py/commit/be0aa6698e9cebbea21237ec71c22d3e1d410b5a))

## [2.32.0](https://github.com/togethercomputer/together-py/compare/v2.31.0...v2.32.0) (2026-08-26)


### Features

* **Endpoints CLI:** add `list`/`delete` aliases for beta endpoints `ls`/`rm` (ENG-92294) ([#538](https://github.com/togethercomputer/together-py/issues/538)) ([9a7c1e2](https://github.com/togethercomputer/together-py/commit/9a7c1e241ff6108be1eee9f5ae3f588c9a2a60bf))
* **Batches CLI:** add `tg batches` commands for the batch API ([#525](https://github.com/togethercomputer/together-py/issues/525)) ([f7d63e0](https://github.com/togethercomputer/together-py/commit/f7d63e07b42b7ed8b5f2107aa5c540ec49734bcf))
* **Jig CLI:** call prewarm API after volume upload and image build ([#535](https://github.com/togethercomputer/together-py/issues/535)) ([371ae93](https://github.com/togethercomputer/together-py/commit/371ae939bd3d8c860765cd2cf5be7adc7def8f04))
* **Evals CLI:** show files upload progress during evals create ([#534](https://github.com/togethercomputer/together-py/issues/534)) ([0b51221](https://github.com/togethercomputer/together-py/commit/0b51221b9c841064c736fcd50da1279a6fed65bf))


### Bug Fixes

* **CLI:** preserve controlled Jig failure diagnostics ([#529](https://github.com/togethercomputer/together-py/issues/529)) ([5b0412f](https://github.com/togethercomputer/together-py/commit/5b0412ffe2310a9c87e430e57c8d757fb8179821))
* **CLI:** preserve diagnostics in truncated telemetry ([#526](https://github.com/togethercomputer/together-py/issues/526)) ([4ee8806](https://github.com/togethercomputer/together-py/commit/4ee8806fdfd046b5b77e7ee3649b4ca8053c6095))
* **CLI:** preserve endpoint API failure diagnostics ([#537](https://github.com/togethercomputer/together-py/issues/537)) ([49f368b](https://github.com/togethercomputer/together-py/commit/49f368b36d1385f4cc45fd09beec0de6df3ad6de))
* **CLI:** preserve endpoint creation diagnostics ([#541](https://github.com/togethercomputer/together-py/issues/541)) ([a08d56c](https://github.com/togethercomputer/together-py/commit/a08d56cb38547a41d617b8411022b6fb8703dd8f))
* **CLI:** preserve endpoint deletion failure diagnostics ([#533](https://github.com/togethercomputer/together-py/issues/533)) ([cab1090](https://github.com/togethercomputer/together-py/commit/cab109099b4e2df59782f4c8692fa21ddd9633bb))
* **Endpoints CLI:** remove --scale-to-zero-window from beta endpoints ([#545](https://github.com/togethercomputer/together-py/issues/545)) ([0070438](https://github.com/togethercomputer/together-py/commit/007043898abef5f988e651b4ab46a16dbe682c2a))
* **CLI:** render numeric model revision fields ([#531](https://github.com/togethercomputer/together-py/issues/531)) ([d3bc330](https://github.com/togethercomputer/together-py/commit/d3bc330f48602f41d78af3a93bd3e79f9056d9be))
* **CLI:** stabilize UnknownOptionError telemetry ([#539](https://github.com/togethercomputer/together-py/issues/539)) ([9d23c56](https://github.com/togethercomputer/together-py/commit/9d23c562a17ade9b56dff2e37ec8e6cdb35d127c))
* **Endpoints CLI:** Rename models output label 'Inference Name' to 'Endpoint string' ([#530](https://github.com/togethercomputer/together-py/issues/530)) ([5bb08a5](https://github.com/togethercomputer/together-py/commit/5bb08a5164e7325cc12491b97a1865bced214fcb))
* **Finetuning CLI:** remove broken pagination on `list-events` command ([#540](https://github.com/togethercomputer/together-py/issues/540)) ([b88a85c](https://github.com/togethercomputer/together-py/commit/b88a85c9493212750b7375e02872457f211483e3))


### Chores

* **CLI:** drop `tqdm` dependency (DX-458) ([#523](https://github.com/togethercomputer/together-py/issues/523)) ([74cf947](https://github.com/togethercomputer/together-py/commit/74cf947446813468fd0ac75fcc1a25e2997cbe49))

## [2.31.0](https://github.com/togethercomputer/together-py/compare/v2.30.0...v2.31.0) (2026-08-12)


### Features

* **Models CLI:** Support model names for base model parameter in `tg beta models create` ([#506](https://github.com/togethercomputer/together-py/issues/506)) ([64a2c2c](https://github.com/togethercomputer/together-py/commit/64a2c2c608c6ac5ce7b5cd1dfaeb6217d4b696f3))
* **Models CLI:** Display supported model profile names in prompt flows ([#503](https://github.com/togethercomputer/together-py/issues/503)) ([7555e64](https://github.com/togethercomputer/together-py/commit/7555e64a1272c951b5eb8d9f6027fe6c0bb17c0a))
* **Jig CLI:** Warn about implicit volume version when there are multiple versions ([#521](https://github.com/togethercomputer/together-py/issues/521)) ([7db3db4](https://github.com/togethercomputer/together-py/commit/7db3db48db06d9ddec8848bf8ce1c1228ef25d73))
* **Clusters CLI:** Display configuration ID in `tg beta clusters list-regions` output ([#513](https://github.com/togethercomputer/together-py/issues/513)) ([4a52eed](https://github.com/togethercomputer/together-py/commit/4a52eedbe9cf8e5c195ef3ea82eba666710efa6d))
* **Endpoints CLI:** Display GPU and estimated price when deploying a new model ([#512](https://github.com/togethercomputer/together-py/issues/512)) ([4e17fa6](https://github.com/togethercomputer/together-py/commit/4e17fa6f7316b8a735109ab5ab3f08920975bc75))
* **Fine Tuning CLI:** add `tg ft model-limits` command ([#439](https://github.com/togethercomputer/together-py/issues/439)) ([4cf18b2](https://github.com/togethercomputer/together-py/commit/4cf18b2c1a182fc4e5abcec2b4ab1367cf1c982d))


### Bug Fixes

* **Fine Tuning CLI:** avoid crashing on timestamp boundaries ([#519](https://github.com/togethercomputer/together-py/issues/519)) ([f3152aa](https://github.com/togethercomputer/together-py/commit/f3152aadf8d92a5c7ece7b7f3eb4bed10522598e))
* **Fine Tuning CLI:** honor `--non-interactive` mode in delete command ([#518](https://github.com/togethercomputer/together-py/issues/518)) ([4992d76](https://github.com/togethercomputer/together-py/commit/4992d76785ac2883f5f6a05ec139e077946fdd25))
* **Jig CLI:** preserve Jig failure diagnostics in telemetry ([#514](https://github.com/togethercomputer/together-py/issues/514)) ([c6423c0](https://github.com/togethercomputer/together-py/commit/c6423c0d8e1194884086b2907c91618983b23246))
* **Models CLI:** support model names for `tg beta models configs --model` list filtering ([#500](https://github.com/togethercomputer/together-py/issues/500)) ([01d0105](https://github.com/togethercomputer/together-py/commit/01d01054dec583c03e9bd2b4ab8235a5a5f0b652))
* **CLI:** Tolerate unsupported terminal characters (notably for Windows OS) ([#501](https://github.com/togethercomputer/together-py/issues/501)) ([65eb647](https://github.com/togethercomputer/together-py/commit/65eb647739bd567c9f8f607350e4b347fac0d8af))
* **Clusters CLI:** skip cluster delete prompts when `--non-interactive` mode is set ([#502](https://github.com/togethercomputer/together-py/issues/502)) ([86fbe97](https://github.com/togethercomputer/together-py/commit/86fbe97678407d757cf4d8a94d2649445348e6c2))


### Chores

* bump detect-agent to 0.6.0 and remove unused dependencies ([#522](https://github.com/togethercomputer/together-py/issues/522)) ([abb6f5d](https://github.com/togethercomputer/together-py/commit/abb6f5dfdbafe5d5d63fe179d0f9e3553839d6ab))


### Documentation

* **audio:** correct direct-upload limit to 80 MB in descriptions ([a99b64b](https://github.com/togethercomputer/together-py/commit/a99b64b6244922df99acb9b4eb0c1f0a1e162b57))
* sync rollout OpenAPI defaults ([21213c2](https://github.com/togethercomputer/together-py/commit/21213c2f6cbca6e224f130ac8fa25f67ac267b55))

## [2.30.0](https://github.com/togethercomputer/together-py/compare/v2.29.0...v2.30.0) (2026-08-07)


### Features

* **cli:** add canonical NVIDIA version selector ([c6d7ea9](https://github.com/togethercomputer/together-py/commit/c6d7ea931006869f0855c7eb6a952eef97ebd16a))
* **cli:** Add B300 GPU to clusters create command ([#495](https://github.com/togethercomputer/together-py/issues/495)) ([d582b27](https://github.com/togethercomputer/together-py/commit/d582b2737be34aed25aa135364dc4c477ac9809d))
* **cli:** add beta endpoint events command ([#491](https://github.com/togethercomputer/together-py/issues/491)) ([6126bf8](https://github.com/togethercomputer/together-py/commit/6126bf8c2eab83ad5052051bcd9631216b2803fb))
* **cli:** add fine-tune tokenized dataset download ([#507](https://github.com/togethercomputer/together-py/issues/507)) ([0d678a6](https://github.com/togethercomputer/together-py/commit/0d678a6f3fd1851cf6ac2001bf294b26dc4cbaf1))
* **cli:** add NVIDIA catalog version selection ([d360f2a](https://github.com/togethercomputer/together-py/commit/d360f2a25ea47de5028ec2b76cf13537fbb73aa1))
* **fine-tuning:** sync tokenized dataset download OpenAPI ([f4b1b5e](https://github.com/togethercomputer/together-py/commit/f4b1b5e1b2a97d0b920a82c80ede4990789ae6ea))
* **cli:** add B300 GPU cluster type ([83d42e3](https://github.com/togethercomputer/together-py/commit/83d42e361599dc7540a5d8edc34153b4c8565ebd))
* **clusters:** sync reserved endpoint enums ([5b88316](https://github.com/togethercomputer/together-py/commit/5b88316f65619fe427c4ab6d1cd6f3d195c54d82))
* **clusters:** sync passive health check alert ordering ([b7bcd39](https://github.com/togethercomputer/together-py/commit/b7bcd39255a08dadc5bcc5222611ac51e181b1ab))


### Bug Fixes

* **cli:** avoid Unicode file status icons ([#493](https://github.com/togethercomputer/together-py/issues/493)) ([f2b00bd](https://github.com/togethercomputer/together-py/commit/f2b00bd03a45802ac958d4812bd782a286afd803))
* **cli:** keep JSON errors machine-readable ([b60eb19](https://github.com/togethercomputer/together-py/commit/b60eb192de926f52e5ce0ecdf50c08ef6284832c))
* **cli:** prefer NVIDIA version IDs in cluster help ([#498](https://github.com/togethercomputer/together-py/issues/498)) ([6eec5a5](https://github.com/togethercomputer/together-py/commit/6eec5a5a4e5ec85cb6fc7780cc5a70dcf18a8cbc))
* **cli:** preserve explicit legacy NVIDIA pairs ([8aa95c3](https://github.com/togethercomputer/together-py/commit/8aa95c345aacaf93859bbaa35c4325d45683970d))
* **cli:** Remove name parameter from `beta endpoints update` command ([#510](https://github.com/togethercomputer/together-py/issues/510)) ([65368c5](https://github.com/togethercomputer/together-py/commit/65368c5dd759e6d867fce904d4b15fce2adabb68))
* **cli:** search all shadow experiment pages ([#497](https://github.com/togethercomputer/together-py/issues/497)) ([7eca0da](https://github.com/togethercomputer/together-py/commit/7eca0da4f4848e976f4cdeb6cb803d3de7d15dd0))

### Chores

* **cli:** update fine-tuning LoRA option help ([#489](https://github.com/togethercomputer/together-py/issues/489)) ([7db37cf](https://github.com/togethercomputer/together-py/commit/7db37cf9372e0edb3c97c1ed387f5a7a4ff8d948))


### Documentation

* **cli:** sync shadow target eligibility help ([#494](https://github.com/togethercomputer/together-py/issues/494)) ([452669b](https://github.com/togethercomputer/together-py/commit/452669b432088400e7346ea889de74619ccfe66f))
* **openapi:** sync endpoint active rollout docs ([ce8ccc7](https://github.com/togethercomputer/together-py/commit/ce8ccc7c063e5a1957fbd8448964aadfeacd0504))
* **openapi:** sync rollout create defaults ([29c164e](https://github.com/togethercomputer/together-py/commit/29c164ef4c1d00827eee212a2cf38049120a0d74))
* sync endpoint events limit ([51fee0b](https://github.com/togethercomputer/together-py/commit/51fee0b328cf5921448a4d608abb4e14ab4dff0c))
* sync shadow target rollout guard ([15abe4b](https://github.com/togethercomputer/together-py/commit/15abe4bb03d6fe48ef7a872181dabbc32504995f))
* sync supported model profile name ([c14423b](https://github.com/togethercomputer/together-py/commit/c14423b0d48e790df9b969ff65df657a070cf08e))
