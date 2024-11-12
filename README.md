Bitgugs -- git-based bug tracker
--------------------------------

Bitgugs is a bug/issue tracker (similar to Jira, RT/RequestTracker,
certain uses of Trello, etc) that stores all information about a
project's issues into the project's Git repository.  It has the
following features:

- atomic updates of code and related issues: the way Bitgugs is meant to
  be used, is to include code and issue updates in the same commit, so
  that there is no point in project history with a discrepancy between
  the code and its metadata;

- simple, transparent, append-only data model: Bitgugs stores issues in
  plaintext files with a simple, human-readable but also machine
  processable format.  Each issue has its information in one file.  Each
  line in the file is an update to one property of the issue.  When the
  issue changes its properties, new lines are added at the end.

- code reviews as issues: a code review in Bitgugs is a special kind of
  issue that has references to the code versions whose changes should be
  reviewed.  Review comments are also issues when they request action.

- no integrations: Bitgugs doesn't seek to integrate with a nice UI,
  email gateway, or anything of the like.  Bitgugs' point is to be
  simple and transparent.  Further integrations can be built on Bitgugs'
  data model.

- no fiddling with branches: Some Git based issue trackers use their own
  branches to have a virtual "filesystem" where they can arrange things
  as they want.  As Bitgugs' point is to have the issues describe
  accurately what's up with a particular version of the code, the issues
  use the same branching as does the code.
