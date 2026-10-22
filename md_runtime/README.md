# H1786D live MD jobs via GitHub Issues and Google Colab

This is a real queue, **not** a simulated Run button. GitHub Pages is static and cannot directly start a GPU job. The Run MD link opens an authenticated GitHub issue request. The owner submits it; a running Colab notebook polls GitHub and launches OpenMM. The website polls the public issue and displays status and validated endpoint results.

## Setup
1. Open [the worker notebook](https://colab.research.google.com/github/aribis77/vwf-variant-kg/blob/main/md_runtime/VWF_H1786D_Colab_Worker.ipynb) in Google Colab.
2. In Colab Secrets, add `GITHUB_TOKEN` (fine-grained PAT for this repository, Issues: Read and write). Do not put the token in GitHub Pages or share it in issue comments.
3. Restore the **validated** runner at `/content/vwf_nvt/run_restrained_nvt.py` and its private structures under `/content/vwf_nvt/private_inputs`. Existing Colab session files do not survive resets. The previous script is not in this GitHub repository.
4. Ensure the runner accepts `--input-dir` and `--out`, performs real OpenMM simulation, and writes `<out>/md_endpoint_results.json`. This final endpoint-analysis output was **not** present in the known previous pipeline; it must be added and audited against original trajectories before jobs can complete successfully.
5. Start the notebook; keep it running. Press **Request live MD run** on the KG webpage; GitHub opens a prefilled issue. Submit the issue, then return to the website and paste the issue number into **Track job**.
6. The worker accepts only issues created by `aribis77` with the exact title `[VWF-MD] H1786D 20ps x3`. The worker publishes progress as issue comments, and closes the issue on success or failure. It will never substitute the historical six endpoints for a new run.

## Result contract
The worker accepts JSON with `variant: "H1786D"`, `status: "completed"`, and `groups.WT` / `groups.H1786D`, each containing exactly three replicate records. Every replicate must have numeric `total_interface_contacts`, `residue1786_contacts`, `residue1786_distance_angstrom`, `disulfide_distance_angstrom`. Results should additionally include engine, input structure hashes, simulation parameters, seeds, run logs, and analysis method provenance.

## Limitations
No unattended execution when Colab is disconnected. GitHub issue API public reads are rate-limited. Only one worker should poll the queue at a time. A disconnected worker may leave jobs queued, or jobs in running state if the session terminates. Results are only published after actual OpenMM subprocess completion and result validation. GitHub Issues are public; do not submit private data.
