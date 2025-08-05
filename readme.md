\# Publine



Publine is a modular self-publishing tool designed to streamline multi-format publishing workflows for indie authors. Generate clean HTML, EPUB, PDF, and more—all from a single source.



\## Features



\- Chapter-based project structure with metadata

\- HTML/EPUB generation with navigation

\- Project-local and global social link support

\- Accessible styling and customizable layouts

\- Modular and scalable for future GUI integration



\## Branch Overview



Publine is actively developed across multiple branches:



| Branch        | Purpose                                      |

|---------------|----------------------------------------------|

| `cli-stable`  | Finalized CLI-only version (no new features) |

| `dev`         | Active development (web UI, refactoring)     |

| `main`        | Future release-ready branch                  |



\## Getting Started (CLI Version)



1\. Clone the repo:

&nbsp;  ```bash

&nbsp;  git clone https://github.com/your-username/publine.git

&nbsp;  cd publine

&nbsp;  ```



2\. (Optional) Checkout the CLI version:

&nbsp;  ```bash

&nbsp;  git checkout cli-stable

&nbsp;  ```



3\. Run the CLI:

&nbsp;  ```bash

&nbsp;  python run\_cli.py

&nbsp;  ```



4\. Choose Option 1 to create a new project.



\## Development Notes



\- CLI logic lives in `cli/src/`

\- Shared utilities are in `core/src/`

\- Web UI (FastAPI) is under development in `web/`



\## License



\*\*Publine Software License (Non-Commercial Use)\*\*  

Copyright © 2025 Gary Hartzell



This software is provided free for personal, educational, and non-commercial use. You may use, modify, and distribute the software under the following conditions:



\- Credit must be given to the original author.

\- This software may not be used, in whole or in part, for any commercial purpose without explicit written permission.

\- All modified versions must retain this license and attribution.



For commercial licensing inquiries, please contact the author: \[gary@hartzell.us](mailto:gary@hartzell.us)



