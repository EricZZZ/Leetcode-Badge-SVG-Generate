# LeetCode Badge SVG Generator

This is a tool that generates SVG images of LeetCode user badges. It supports both LeetCode international site (leetcode.com) and Chinese site (leetcode.cn).

## Features

- Supports both LeetCode international site and Chinese site
- Retrieves all earned badges for a user
- Generates a single SVG file containing all badges
- Supports both static and animated (GIF) badge icons
- Badge information includes name and acquisition date
- Icons embedded in SVG as inline base64 for self-contained files

## Installation Requirements

- Python 3.6+
- requests library

Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Configure the following parameters in the `config.ini` file:

```ini
[LEETCODE]
username = your_leetcode_username
animated = true/false
site = leetcode.com or leetcode.cn
```

- `username`: Your LeetCode username
- `animated`: Whether to use animated badge icons (true/false)
- `site`: Select site (leetcode.com or leetcode.cn)

Example configuration:
```ini
[LEETCODE]
username = ericzzz-5
animated = true
site = leetcode.cn
```

## Usage

1. Configure the `config.ini` file
2. Run the program:
```bash
python main.py
```
3. The generated SVG file will be saved in the `img` directory with the name `{username}_{site}_badges.svg`

## GitHub Actions Automation

This project can be automatically run using GitHub Actions to regularly update your badges SVG.

### Setup

1. Fork this repository or copy the workflow file to your repository at `.github/workflows/generate_badges.yml`
2. In your repository settings, add the following secrets under "Settings" > "Secrets and variables" > "Actions":
   - `LEETCODE_USERNAME` - Your LeetCode username
   - `LEETCODE_SITE` (optional) - Either `leetcode.com` or `leetcode.cn` (defaults to `leetcode.com`)
   - `LEETCODE_ANIMATED` (optional) - `true` or `false` (defaults to `false`)

### Permissions

To allow the workflow to push changes to your repository, you need to configure permissions:

1. Go to your repository's "Settings" > "Actions" > "General"
2. Under "Workflow permissions", select "Read and write permissions"
3. Click "Save"

Alternatively, the workflow file includes a `permissions: contents: write` setting which should grant the necessary permissions.

### How it works

The workflow is scheduled to run weekly on Mondays at 00:00 UTC (8:00 AM Beijing time). It will:
1. Checkout your repository
2. Set up Python environment
3. Install dependencies
4. Generate the badges SVG using your configured settings
5. Commit and push the updated SVG to your repository

You can also manually trigger the workflow from the "Actions" tab in your repository.

## Output Example

The generated SVG file will contain all user badges, displaying two badges per row, with each badge showing:
- Badge name
- Acquisition date
- Badge icon (if available)

## Supported Badge Types

- Submission badges (e.g. 100 Days Badge)
- Annual badges (e.g. Annual Badge 2023)
- Daily challenge badges (e.g. Oct LeetCoding Challenge)
- Other special badges (e.g. 1024 Commemorative Badge)

## Notes

- The program retrieves badge data through the LeetCode GraphQL API
- Chinese and international sites use different API endpoints and query structures
- Generated SVGs are self-contained and do not depend on external resources
- Ensure stable network connection to download badge icons