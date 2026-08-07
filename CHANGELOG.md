# Changelog

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
