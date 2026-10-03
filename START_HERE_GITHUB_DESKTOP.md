# GitHub Desktop: synchronize this repository or publish a new copy

The source code is already published at [HHFinAi/Transition-Plan-Credibility-Assessment](https://github.com/HHFinAi/Transition-Plan-Credibility-Assessment). Use the existing-repository workflow below for updates. The new-copy section applies only when you deliberately create a separate repository.

## Work with the existing repository

1. Select this repository in GitHub Desktop. If you do not have a clone, choose **File → Clone Repository**, enter `https://github.com/HHFinAi/Transition-Plan-Credibility-Assessment`, and select a new local folder.
2. Save or commit your local work, then use **Fetch origin** and **Pull origin** when changes are available. Resolve any conflicts before making further edits. Create a working branch for the update.
3. Copy only the reviewed files you intend to change. Keep the existing `.git` directory, history and unrelated content. Never replace `.git`, copy another clone's `.git`, or force-push to synchronize a downloaded package. Keep relevant `.github`, `.gitignore` and `.gitattributes` files with the project.
4. Run the checks documented in [README](README.md). Review the diff, confirm the Git author identity for HHFinAi, commit and push the branch, then open a pull request for review. Check the repository's [Actions results](https://github.com/HHFinAi/Transition-Plan-Credibility-Assessment/actions) for the commit being reviewed.

## Initial publication of a separate new copy

1. Confirm the intended GitHub account and choose an unused repository name. Use a new empty directory; do not repeat this step against the existing repository above.
2. Create a new local repository in GitHub Desktop. Copy the source files into its root, including `.github`, `.gitignore` and `.gitattributes`, while preserving the `.git` directory created for the new repository. Do not upload a ZIP in place of the source files or nest the whole project an extra level deep.
3. Update `repository-metadata.json` and repository links to describe the new owner/name. Before publication, use `publication_status: prepared-not-published`; after verifying the new remote, record `publication_status: published`, its actual `repository_name`, `repository_url`, visibility and verification date. The offline checker validates declarations, not live GitHub state.
4. Review the files and run the checks. Confirm the author name and verified email or GitHub-provided noreply address. Choose **Publish repository**, verify the owner/name, and select visibility deliberately. No visibility change is automatic.
5. Use the description and relevant topics in `repository-metadata.json` for the new repository's About settings. Inspect its Actions results after publication. Optional `docs/index.html` is a static source page; repository publication does not configure a hosted website or deploy an AI service.

Keep confidential evidence, run folders, credentials and licensed data outside public commits. GitHub Desktop menu labels can vary by version. See [GitHub Desktop documentation](https://docs.github.com/en/desktop) for the current interface.
