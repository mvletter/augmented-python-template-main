import os
import sys

from git import Repo
from slack import WebClient
from slack.errors import SlackApiError


def post_changelog(before, current):
    """
    Run a git diff between before and current and post the resulting changelog
    to the proper slack channel.

    Args:
        before (str): Hash of the previous deployed commit.
        current (str): Hash of the commit being deployed.
    """
    slack_oath = os.environ.get("SLACK_NOTIFY_OAUTH")

    # Determine slack channel.
    if os.environ.get("CI_ENVIRONMENT_NAME") == "production":
        channel = os.environ.get("DEPLOYMENT_SLACK_CHANNEL_PRODUCTION")
    else:
        channel = os.environ.get("DEPLOYMENT_SLACK_CHANNEL_STAGING")

    # If variables are not set, do nothing.
    if not slack_oath or not channel:
        return

    slack_client = WebClient(slack_oath)
    repo = Repo(os.environ.get("CI_PROJECT_DIR"))

    project_url = os.environ.get("CI_PROJECT_URL")
    # Compare the two, results in a \n separated string containing all commits.
    # Formatted in slack as to copy Github behavior.
    # > `<url|short hash>` Commit message - Author
    commit_lines = repo.git.log(
        f"{before}...{current}",
        f"--pretty=format:> `<{project_url}/-/commit/%h|%h>` %s - %an",
        "--reverse",
        "--no-merges",
    )
    commit_lines = commit_lines.split("\n")
    total = len(commit_lines)
    plural = "" if total < 1 else "s"
    compare_url = f"{project_url}/-/compare/{before}...{current}"
    branch = os.environ.get("CI_COMMIT_REF_NAME")

    # Header with 'compare' link and total commits.
    project_name = os.environ.get("CI_PROJECT_NAME")
    message = f"<{compare_url}|[{project_name}:{branch}] {total} commit{plural}>\n"

    if total > 20:
        message += "\n".join(commit_lines[0:5])
        message += f"\n {len(commit_lines[5:-5])} more commits .....\n"
        message += "\n".join(commit_lines[-5:])
        message += "\n :thread: *See thread for all commits* :thread:"
    else:
        message += "\n".join(commit_lines)

    try:
        response = slack_client.chat_postMessage(
            channel=channel,
            username="Gitlab",
            text=message,
            unfurl_links=False,
            unfurl_media=False,
        )
    except SlackApiError as e:
        # Catch errors so our build never fails because of Slack errors.
        print(f'Error posting message to Slack: "{e}"')

    # Reply in thread with all commits.
    if total > 20:
        try:
            slack_client.chat_postMessage(
                channel=channel,
                thread_ts=response["ts"],
                username="Gitlab",
                text="\n".join(commit_lines),
                unfurl_links=False,
                unfurl_media=False,
            )
        except SlackApiError as e:
            # Catch errors so our build never fails because of Slack errors.
            print(f'Error posting thread message to Slack: "{e}"')


if __name__ == "__main__":
    # args:
    # Old git revision hash
    # New git revision hash
    before = sys.argv[1]
    current = sys.argv[2]
    post_changelog(before, current)
