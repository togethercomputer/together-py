# Changelog

## [3.0.0](https://github.com/togethercomputer/together-py/compare/v2.40.0...v3.0.0) (2026-10-10)


### ⚠ BREAKING CHANGES

* **rl/mosh-5452:** return the created checkpoint from session checkpoint helpers ([#182](https://github.com/togethercomputer/together-py/issues/182))

### Features

* add RL model resource queue position ([e985c4b](https://github.com/togethercomputer/together-py/commit/e985c4bcf7ca4b19fb00990ce0872570596117c0))
* **cli:** add `tg training fp4` commands for FP4 inference preparation (MOSH-5443) ([#179](https://github.com/togethercomputer/together-py/issues/179)) ([6998308](https://github.com/togethercomputer/together-py/commit/6998308cc97fb40ff3a36f3b53e0ca1161c11529))
* **cli:** add training list and get commands ([#627](https://github.com/togethercomputer/together-py/issues/627)) ([b8ae661](https://github.com/togethercomputer/together-py/commit/b8ae66193a3e7df6ed2fe8d151faa42e3cb8dfd0))
* **cli:** Support deploying LoRA adapters as multi-lora attachments or merged deployments ([#608](https://github.com/togethercomputer/together-py/issues/608)) ([66c9b77](https://github.com/togethercomputer/together-py/commit/66c9b777d02735967339139853bc08baea95df5f))
* document shaping calibration files ([ae4557e](https://github.com/togethercomputer/together-py/commit/ae4557e0eefde4b15bfa2b23d619e04c1b08cbf8))
* expose RL checkpoint registry artifacts ([e140a5f](https://github.com/togethercomputer/together-py/commit/e140a5fb3b6deece69cbbc9a0a9caa55615e58eb))
* **rl/mosh-5452:** return the created checkpoint from session checkpoint helpers ([#182](https://github.com/togethercomputer/together-py/issues/182)) ([a3c0232](https://github.com/togethercomputer/together-py/commit/a3c0232f9d672bb2c0bae85cb4045b4fa029ec9d))
* **rl:** move the training SDK to together.post_training ([#634](https://github.com/togethercomputer/together-py/issues/634)) ([fb01780](https://github.com/togethercomputer/together-py/commit/fb0178059bb2e00be529c8050fcaa82642891003))


### Bug Fixes

* **rl/mosh-5323:** read checkpoint id from RL checkpoint results ([#180](https://github.com/togethercomputer/together-py/issues/180)) ([12e0bf7](https://github.com/togethercomputer/together-py/commit/12e0bf7a31a48794f2c30a62e344a9ac5fa5ffab))
* sync adapter attachment ids in OpenAPI ([c074a04](https://github.com/togethercomputer/together-py/commit/c074a04da6aa11f4f88e99df310e3e2b9d3870a6))
* sync RL checkpoint OpenAPI schemas ([250292e](https://github.com/togethercomputer/together-py/commit/250292ea7b3d2e2ba7f3aa46c795dfc7ca75a42a))
