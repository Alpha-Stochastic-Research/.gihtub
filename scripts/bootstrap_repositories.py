\
#!/usr/bin/env python3
"""Apply ASR team permissions and ensure one GitHub Project per active repository."""

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
VALID_PERMISSIONS = {"pull", "triage", "push", "maintain", "admin"}


class GitHubError(RuntimeError):
    """Raised when a GitHub API request fails."""


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class GitHubClient:
    def __init__(self, token: str) -> None:
        self.token = token

    def _request(
        self,
        method: str,
        url: str,
        payload: dict[str, Any] | None = None,
    ) -> Any:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": API_VERSION,
                "User-Agent": "asr-repository-bootstrap",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                body = response.read()
                if not body:
                    return None
                return json.loads(body.decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise GitHubError(
                f"{method} {url} failed with HTTP {exc.code}: {body}"
            ) from exc
        except urllib.error.URLError as exc:
            raise GitHubError(f"{method} {url} failed: {exc}") from exc

    def rest(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        return self._request(method, f"{API_ROOT}{path}", payload)

    def graphql(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
        *,
        tolerate_errors: bool = False,
    ) -> dict[str, Any]:
        response = self._request(
            "POST",
            GRAPHQL_URL,
            {"query": query, "variables": variables or {}},
        )
        errors = response.get("errors") or []
        if errors and not tolerate_errors:
            raise GitHubError(f"GraphQL errors: {json.dumps(errors)}")
        return response

    def list_org_repositories(self, organization: str) -> list[dict[str, Any]]:
        repositories: list[dict[str, Any]] = []
        page = 1
        while True:
            encoded = urllib.parse.quote(organization, safe="")
            batch = self.rest(
                "GET",
                f"/orgs/{encoded}/repos?type=all&sort=full_name&per_page=100&page={page}",
            )
            repositories.extend(batch)
            if len(batch) < 100:
                return repositories
            page += 1

    def list_org_teams(self, organization: str) -> list[dict[str, Any]]:
        teams: list[dict[str, Any]] = []
        page = 1
        while True:
            encoded = urllib.parse.quote(organization, safe="")
            batch = self.rest(
                "GET",
                f"/orgs/{encoded}/teams?per_page=100&page={page}",
            )
            teams.extend(batch)
            if len(batch) < 100:
                return teams
            page += 1

    def set_team_repository_permission(
        self,
        organization: str,
        team_slug: str,
        repository: str,
        permission: str,
    ) -> None:
        org = urllib.parse.quote(organization, safe="")
        team = urllib.parse.quote(team_slug, safe="")
        repo = urllib.parse.quote(repository, safe="")
        self.rest(
            "PUT",
            f"/orgs/{org}/teams/{team}/repos/{org}/{repo}",
            {"permission": permission},
        )

    def list_projects(self, organization: str) -> tuple[str, dict[str, dict[str, Any]]]:
        query = """
        query($organization: String!, $cursor: String) {
          organization(login: $organization) {
            id
            projectsV2(first: 100, after: $cursor) {
              nodes { id title number }
              pageInfo { hasNextPage endCursor }
            }
          }
        }
        """
        cursor: str | None = None
        owner_id: str | None = None
        projects: dict[str, dict[str, Any]] = {}
        while True:
            response = self.graphql(
                query,
                {"organization": organization, "cursor": cursor},
            )
            org_data = response["data"]["organization"]
            if org_data is None:
                raise GitHubError(f"Organization not found: {organization}")
            owner_id = org_data["id"]
            connection = org_data["projectsV2"]
            for project in connection["nodes"]:
                projects[project["title"]] = project
            page_info = connection["pageInfo"]
            if not page_info["hasNextPage"]:
                break
            cursor = page_info["endCursor"]
        assert owner_id is not None
        return owner_id, projects

    def create_project(
        self,
        owner_id: str,
        repository_id: str,
        title: str,
    ) -> dict[str, Any]:
        mutation = """
        mutation($ownerId: ID!, $repositoryId: ID!, $title: String!) {
          createProjectV2(
            input: {
              ownerId: $ownerId
              repositoryId: $repositoryId
              title: $title
            }
          ) {
            projectV2 { id title number }
          }
        }
        """
        response = self.graphql(
            mutation,
            {
                "ownerId": owner_id,
                "repositoryId": repository_id,
                "title": title,
            },
        )
        return response["data"]["createProjectV2"]["projectV2"]

    def link_project_to_repository(
        self,
        project_id: str,
        repository_id: str,
    ) -> None:
        mutation = """
        mutation($projectId: ID!, $repositoryId: ID!) {
          linkProjectV2ToRepository(
            input: {
              projectId: $projectId
              repositoryId: $repositoryId
            }
          ) {
            clientMutationId
          }
        }
        """
        response = self.graphql(
            mutation,
            {"projectId": project_id, "repositoryId": repository_id},
            tolerate_errors=True,
        )
        errors = response.get("errors") or []
        if not errors:
            return
        combined = " ".join(str(error.get("message", "")) for error in errors).lower()
        if "already" in combined and "link" in combined:
            return
        raise GitHubError(f"Unable to link project: {json.dumps(errors)}")


def load_config(path: Path) -> dict[str, Any]:
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise GitHubError(f"Configuration file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise GitHubError(f"Invalid JSON configuration: {exc}") from exc

    for team, permission in config.get("team_permissions", {}).items():
        if permission not in VALID_PERMISSIONS:
            raise GitHubError(f"Invalid permission {permission!r} for team {team!r}")
    return config


def permission_for(
    repository_name: str,
    team_slug: str,
    config: dict[str, Any],
) -> str:
    permission = config.get("team_permissions", {}).get(
        team_slug,
        config.get("unknown_team_permission", "pull"),
    )
    for override in config.get("repository_overrides", []):
        patterns = override.get("patterns", [])
        if any(fnmatch.fnmatchcase(repository_name, pattern) for pattern in patterns):
            permission = override.get("permissions", {}).get(team_slug, permission)
    if permission not in VALID_PERMISSIONS:
        raise GitHubError(
            f"Invalid resolved permission {permission!r} "
            f"for {team_slug!r} on {repository_name!r}"
        )
    return permission


def main() -> int:
    token = os.getenv("ASR_ADMIN_TOKEN", "").strip()
    if not token:
        print("ERROR: ASR_ADMIN_TOKEN is not configured.", file=sys.stderr)
        return 2

    config_path = Path(os.getenv("ASR_CONFIG_PATH", "config/repository-access.json"))
    config = load_config(config_path)
    organization = os.getenv("ASR_ORG", config["organization"]).strip()
    dry_run = env_bool("ASR_DRY_RUN", default=False)

    client = GitHubClient(token)
    repositories = [
        repo
        for repo in client.list_org_repositories(organization)
        if not repo.get("archived") and not repo.get("disabled")
    ]
    teams = client.list_org_teams(organization)
    owner_id, projects = client.list_projects(organization)

    print(
        f"Organization={organization} repositories={len(repositories)} "
        f"teams={len(teams)} dry_run={dry_run}"
    )

    failures: list[str] = []

    for repo in repositories:
        repo_name = repo["name"]
        print(f"\nRepository: {repo_name}")

        for team in teams:
            team_slug = team["slug"]
            permission = permission_for(repo_name, team_slug, config)
            print(f"  team {team_slug}: {permission}")
            if dry_run:
                continue
            try:
                client.set_team_repository_permission(
                    organization,
                    team_slug,
                    repo_name,
                    permission,
                )
            except GitHubError as exc:
                failures.append(f"{repo_name}/{team_slug}: {exc}")

        title = config["project_title_template"].format(repository=repo_name)
        existing = projects.get(title)

        if existing:
            print(f"  project exists: {title}")
            if not dry_run:
                try:
                    client.link_project_to_repository(
                        existing["id"],
                        repo["node_id"],
                    )
                except GitHubError as exc:
                    failures.append(f"{repo_name}/project-link: {exc}")
        else:
            print(f"  project create: {title}")
            if not dry_run:
                try:
                    project = client.create_project(
                        owner_id,
                        repo["node_id"],
                        title,
                    )
                    projects[title] = project
                except GitHubError as exc:
                    failures.append(f"{repo_name}/project-create: {exc}")

        # Avoid sending a large burst of administrative requests.
        if not dry_run:
            time.sleep(0.2)

    if failures:
        print("\nFailures:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("\nRepository access and project policy completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
