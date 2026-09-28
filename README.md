# Granpai3DGlobe video recorder

GitHub Actions records the live plugin demo in Chromium and renders a 1080 × 1920 video with original generated music. HVAC uses a 17-second kinetic story edit; the other demos currently use the initial promo layout. No site credentials are needed.

Open **Actions → Record 3D Globe demo → Run workflow**, choose `hvac`, `timeline`, `global-impact`, or `all`, then download the `granpai-videos-*` artifact from the completed run. The artifact includes the finished MP4, the raw WebM recording, and check screenshots for each demo. Pushes run an HVAC smoke test. Timeline and Global Impact still need a first visual review before publishing.

The source is the public live demo. If the canvas fails to render, the job fails instead of presenting an empty video as a finished asset. Review the check screenshot and final MP4 before publishing. All demo organization/location content is illustrative; identify the Global Impact organization as fictional in any post caption.

Customize each demo's URL and capture sequence in `scripts/record.mjs`; edit `scripts/cinematic.py` for the HVAC story and `scripts/promo.py` for the other demos. The soundtrack is generated locally, so no third-party music license is required.
