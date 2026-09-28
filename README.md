# Granpai3DGlobe video recorder

GitHub Actions records the live plugin demo in Chromium and renders a separate vertical MP4 for each demo. No site credentials are needed.

Open **Actions → Record 3D Globe demo → Run workflow**, choose `hvac`, `timeline`, `global-impact`, or `all`, then download the `granpai-videos-*` artifact from the completed run. The artifact includes MP4 files, the raw WebM recordings, and a check screenshot for each demo. The first push also runs an HVAC smoke test.

The source is the public live demo. If the canvas fails to render, the job fails instead of presenting an empty video as a finished asset. Review the check screenshot and final MP4 before publishing. All demo organization/location content is illustrative; identify the Global Impact organization as fictional in any post caption.

Customize each demo's URL and capture sequence in `scripts/record.mjs`; change the vertical layout and on-screen copy in `scripts/render.sh`.
