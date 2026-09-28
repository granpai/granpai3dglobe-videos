# Granpai3DGlobe video recorder

GitHub Actions records the live plugin demo in Chromium and renders a separate 1080 × 1920 promo with original generated music for each demo. No site credentials are needed.

Open **Actions → Record 3D Globe demo → Run workflow**, choose `hvac`, `timeline`, `global-impact`, or `all`, then download the `granpai-videos-*` artifact from the completed run. The artifact includes a `*-promo.mp4`, the raw WebM recording, and check screenshots for each demo. Pushes run an HVAC smoke test. The HVAC promo has been visually checked; the Timeline and Global Impact crops and interactions still need a first review before publishing.

The source is the public live demo. If the canvas fails to render, the job fails instead of presenting an empty video as a finished asset. Review the check screenshot and final MP4 before publishing. All demo organization/location content is illustrative; identify the Global Impact organization as fictional in any post caption.

Customize each demo's URL and capture sequence in `scripts/record.mjs`; change the vertical layout, on-screen copy, and generated soundtrack in `scripts/promo.py`.
