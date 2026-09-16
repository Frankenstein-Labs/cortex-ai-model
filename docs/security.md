# Security

Private project data must be scrubbed before dataset creation. Exclude `.env`, tokens, API keys, credentials, personal data, and private repository metadata. Permission modes should be explicit (`readonly`, `workspace`, `developer`, `trusted`) with approval gates for destructive filesystem, terminal, network, GitHub, Docker, and cloud operations.
