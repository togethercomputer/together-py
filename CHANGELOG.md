# Changelog

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
