Normal workflows when working with Bitgugs
==========================================

Creating issues (i.e. writing down things you have to remember)

- Command: `bitgugs -c new <issue title>`
  - creates an issue with the given title, spawns an editor to give a
    longer description of the issue (if you want), and makes a commit
    out of it.

Looking for stuff to do

- Command: `bitgugs list -q`
  - shows all open issues
- Command: `bitgugs list <search terms>`
  - shows issues which match search terms, usually free text search

Working on something

- Command: `bitgugs take <issue id>`
  - marks the issue as being worked on by you.
  - use `-c` if you want to make a commit (to push this update for
    others to see)
- Command: `bitgugs commit <issue id> <commit message>`
  - mark the current changes (as given by git status) as being done to a
    specific issue, and make a commit with the given message
  - you should use `-s closed` if you want to mark the issue as done
    simultaneously

Fixing the issue data

- You can just edit the files in `issues/` and commit (or fixup/amend
  earlier commit)
- Command: `bitgugs -c update <issue id> status closed`
  - marks the issue as done

