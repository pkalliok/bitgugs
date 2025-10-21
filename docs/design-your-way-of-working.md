How will you work?
==================

Bitgugs is not very opinionated when it comes to how you organise your
team / development practices.  Bitgugs has some default fields and
statuses, but you don't need to use those.  You can make up your own,
and create your own practices.

- The only status that is really special for Bitgugs is "closed", and
  it's only special because the default search (`bitgugs list`) lists
  `not closed` issues.
  - maybe someday Bitgugs will have a configuration file and you can
    override that too.

Where should you make issue changes?
------------------------------------

Because Bitgugs works in the source repo, the issues are also versioned,
and so they can differ in different branches, too.  This brings up the
question: which branch should issue changes be made in?  The overarching
principle is: change issues where the changes introduced are true.

- If your code is fixed in a branch, mark the issue as fixed in that
  branch (so that merging will mark the issue as fixed in `main` too).
- If the issue is a point of action in a code review, naturally it is
  created on the branch where the code review is being conducted.
- New issues are usually created on `main`, because they document
  bugs/TODO items of the `main` branch.
- If an issue is true in _every_ branch, it usually suffices to create
  it in `main`.  Usually there's no need to cherry-pick it into other
  non-merged branches.

Statuses and status transitions
-------------------------------

If you want to include more information in the issues, you can use your
own fields and statuses.  For instance, there could be a `planning`
status, or you could use `in-review` and `in-testing` statuses or e.g.
an `acceptance-criteria` field.

- usually when you transition an issue into a new status it makes sense
  to tell why.
  - for instance, an issue going from `assigned` to `review` doesn't
    need much explanation, but an issue going from `review` to
    `assigned` probably will.
- a good practice could be also to document all extra info to the issue
  as `comment` fields, especially if you want to show who comments.
