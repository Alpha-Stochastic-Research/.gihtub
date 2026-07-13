\
#!/usr/bin/env python3
"""Tailor each ASR organization Project to its linked repository."""

from __future__ import annotations

import fnmatch
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

API_ROOT = "https://api.github.com"
GRAPHQL_URL = "https://api.github.com/graphql"
API_VERSION = "2022-11-28"
MAX_RETRIES = 4
MUTATION_DELAY = 1.0
MARKER = "<!-- asr-project-tailoring:v1 -->"


class GitHubError(RuntimeError):
    pass


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class GitHubClient:
    def __init__(self, token: str) -> None:
        self.token = token

    def request(
        self,
        method: str,
        url: str,
        payload: dict[str, Any] | None = None,
    ) -> Any:
        data = None if payload is None else json.dumps(payload).encode("utf-8")

        for attempt in range(MAX_RETRIES + 1):
            request = urllib.request.Request(
                url,
                data=data,
                method=method,
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {self.token}",
                    "X-GitHub-Api-Version": API_VERSION,
                    "User-Agent": "asr-project-tailoring",
                    "Content-Type": "application/json",
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    body = response.read()
                    return json.loads(body.decode("utf-8")) if body else None
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                lower = body.lower()
                limited = (
                    exc.code == 429
                    or (
                        exc.code == 403
                        and ("rate limit" in lower or "abuse" in lower)
                    )
                )
                if limited and attempt < MAX_RETRIES:
                    retry_after = exc.headers.get("Retry-After")
                    delay = (
                        int(retry_after)
                        if retry_after and retry_after.isdigit()
                        else min(30 * (2 ** attempt), 240)
                    )
                    print(f"Rate limited; retrying in {delay}s.", file=sys.stderr)
                    time.sleep(delay)
                    continue
                raise GitHubError(
                    f"{method} {url} failed with HTTP {exc.code}: {body}"
                ) from exc
            except urllib.error.URLError as exc:
                raise GitHubError(f"{method} {url} failed: {exc}") from exc

        raise GitHubError(f"{method} {url} failed after retries")

    def rest(self, path: str) -> Any:
        return self.request("GET", f"{API_ROOT}{path}")

    def graphql(
        self,
        query: str,
        variables: dict[str, Any],
    ) -> dict[str, Any]:
        response = self.request(
            "POST",
            GRAPHQL_URL,
            {"query": query, "variables": variables},
        )
        errors = response.get("errors") or []
        if errors:
            raise GitHubError(f"GraphQL errors: {json.dumps(errors)}")
        return response

    def list_repositories(self, organization: str) -> list[dict[str, Any]]:
        repos: list[dict[str, Any]] = []
        page = 1
        org = urllib.parse.quote(organization, safe="")
        while True:
            batch = self.rest(
                f"/orgs/{org}/repos?type=all&sort=full_name"
                f"&per_page=100&page={page}"
            )
            repos.extend(batch)
            if len(batch) < 100:
                return repos
            page += 1

    def list_projects(
        self,
        organization: str,
    ) -> dict[str, dict[str, Any]]:
        query = """
        query($organization: String!, $cursor: String) {
          organization(login: $organization) {
            projectsV2(first: 100, after: $cursor) {
              nodes {
                id
                title
                number
                shortDescription
                readme
                items(first: 100) {
                  nodes {
                    content {
                      ... on DraftIssue { title body }
                      ... on Issue { title body }
                      ... on PullRequest { title body }
                    }
                  }
                }
              }
              pageInfo { hasNextPage endCursor }
            }
          }
        }
        """
        projects: dict[str, dict[str, Any]] = {}
        cursor: str | None = None
        while True:
            response = self.graphql(
                query,
                {"organization": organization, "cursor": cursor},
            )
            org_data = response["data"]["organization"]
            if org_data is None:
                raise GitHubError(f"Organization not found: {organization}")
            connection = org_data["projectsV2"]
            for project in connection["nodes"]:
                projects[project["title"]] = project
            page_info = connection["pageInfo"]
            if not page_info["hasNextPage"]:
                return projects
            cursor = page_info["endCursor"]

    def update_project(
        self,
        project_id: str,
        *,
        short_description: str,
        readme: str,
        public: bool,
    ) -> None:
        mutation = """
        mutation(
          $projectId: ID!,
          $shortDescription: String!,
          $readme: String!,
          $public: Boolean!
        ) {
          updateProjectV2(
            input: {
              projectId: $projectId
              shortDescription: $shortDescription
              readme: $readme
              public: $public
            }
          ) {
            projectV2 { id }
          }
        }
        """
        self.graphql(
            mutation,
            {
                "projectId": project_id,
                "shortDescription": short_description,
                "readme": readme,
                "public": public,
            },
        )
        time.sleep(MUTATION_DELAY)

    def add_draft_item(
        self,
        project_id: str,
        title: str,
        body: str,
    ) -> None:
        mutation = """
        mutation($projectId: ID!, $title: String!, $body: String!) {
          addProjectV2DraftIssue(
            input: {
              projectId: $projectId
              title: $title
              body: $body
            }
          ) {
            projectItem { id }
          }
        }
        """
        self.graphql(
            mutation,
            {"projectId": project_id, "title": title, "body": body},
        )
        time.sleep(MUTATION_DELAY)


def load_config(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise GitHubError(f"Configuration not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise GitHubError(f"Invalid JSON configuration: {exc}") from exc


def select_profile(
    repository_name: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    for profile in config.get("profiles", []):
        if any(
            fnmatch.fnmatchcase(repository_name, pattern)
            for pattern in profile.get("patterns", [])
        ):
            return profile
    return config["default_profile"]


def build_readme(
    organization: str,
    repository: dict[str, Any],
    profile: dict[str, Any],
) -> str:
    repository_name = repository["name"]
    repo_url = repository["html_url"]
    stages = " → ".join(profile["stages"])
    teams = "\n".join(f"- {team}" for team in profile["primary_teams"])

    return f"""{MARKER}
# {profile["icon"]} {repository_name}

> **{profile["label"]}**  
> {profile["short_description"]}

## Repository

- **Source:** [{organization}/{repository_name}]({repo_url})
- **Visibility:** {repository["visibility"]}
- **Default branch:** `{repository["default_branch"]}`
- **Project model:** one Project per repository

## Delivery flow

`{stages}`

## Primary teams

{teams}

## Operating rules

1. Capture work as an issue or pull request whenever possible.
2. Keep scope, owner and acceptance criteria explicit.
3. Require review before moving work to completion.
4. Record research, security and reproducibility evidence in the repository.
5. Close the loop with documentation, release notes or a decision record.

## Project health

- Keep the active backlog intentionally small.
- Move blocked work back to triage with a clear reason.
- Review stale items during the repository's regular operating cadence.
- Use the repository's protected pull-request workflow for implementation.
"""


def existing_titles(project: dict[str, Any]) -> set[str]:
    titles: set[str] = set()
    for item in project.get("items", {}).get("nodes", []):
        content = item.get("content") or {}
        title = content.get("title")
        if title:
            titles.add(title)
    return titles


def main() -> int:
    token = os.getenv("ASR_PROJECT_TOKEN", "").strip()
    if not token:
        print("ERROR: ASR_PROJECT_TOKEN is not configured.", file=sys.stderr)
        return 2

    config_path = Path(
        os.getenv("ASR_PROJECT_STYLE_CONFIG", "config/project-styles.json")
    )
    config = load_config(config_path)
    organization = os.getenv(
        "ASR_ORG",
        config["organization"],
    ).strip()
    dry_run = env_bool("ASR_DRY_RUN", default=False)

    client = GitHubClient(token)
    repositories = [
        repo
        for repo in client.list_repositories(organization)
        if not repo.get("archived") and not repo.get("disabled")
    ]
    projects = client.list_projects(organization)

    print(
        f"Tailoring {len(repositories)} repositories; dry_run={dry_run}"
    )

    failures: list[str] = []

    for repository in repositories:
        name = repository["name"]
        project_title = config["project_title_template"].format(
            repository=name
        )
        project = projects.get(project_title)

        if project is None:
            print(f"{name}: project not found; skipped")
            continue

        profile = select_profile(name, config)
        readme = build_readme(
            organization,
            repository,
            profile,
        )
        short_description = profile["short_description"]
        public = repository.get("visibility") == "public"

        print(
            f"{name}: profile={profile['name']} "
            f"visibility={'public' if public else 'private'}"
        )

        if not dry_run and (
            project.get("readme") != readme
            or project.get("shortDescription") != short_description
        ):
            try:
                client.update_project(
                    project["id"],
                    short_description=short_description,
                    readme=readme,
                    public=public,
                )
            except GitHubError as exc:
                failures.append(f"{name}/settings: {exc}")

        titles = existing_titles(project)
        for item_title in profile["starter_items"]:
            decorated_title = f"{profile['icon']} {item_title}"
            if decorated_title in titles:
                print(f"  starter item unchanged: {decorated_title}")
                continue

            print(f"  starter item create: {decorated_title}")
            if dry_run:
                continue

            body = (
                f"{MARKER}\n"
                f"Initial operating item for `{name}`.\n\n"
                f"**Profile:** {profile['label']}\n"
                f"**Repository:** {repository['html_url']}\n\n"
                "Convert this draft into a repository issue when the work "
                "is ready to be assigned and executed."
            )
            try:
                client.add_draft_item(
                    project["id"],
                    decorated_title,
                    body,
                )
                titles.add(decorated_title)
            except GitHubError as exc:
                failures.append(f"{name}/starter-item: {exc}")

    if failures:
        print("\nFailures:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("\nAll available repository Projects are tailored.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

