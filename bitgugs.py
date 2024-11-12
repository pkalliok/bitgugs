#!/usr/bin/env python3

import sys, os, glob
import functools, re
from argparse import ArgumentParser

def die(message):
    sys.stderr.write(message + "\n")
    sys.exit(1)

def find_git_root():
    return os.popen("git rev-parse --show-toplevel").readline().rstrip()

@functools.cache
def ensure_issue_directory():
    root = find_git_root()
    if not root:
        die("Could not find issues, not in Git repository?")
    issue_dir = os.path.join(root, "issues")
    if not os.path.isdir(issue_dir): os.mkdir(issue_dir)
    return issue_dir

def get_issue_filename(identifier):
    issue_dir = ensure_issue_directory()
    names = glob.glob(f"{identifier}-*.txt", root_dir=issue_dir)
    if len(names) != 1:
        die(f"Issue {identifier} is not a single issue: found {names}")
    return os.path.join(issue_dir, names[0])

def all_issues():
    issue_dir = ensure_issue_directory()
    return glob.glob("*-*.txt", root_dir=issue_dir)

def filename_to_numbers(name):
    try:
        return [int(re.match(r"([^-]+)-", name).group(1))]
    except (AttributeError, ValueError):
        return []

def new_issue_number():
    names = all_issues()
    numbers = [nr for name in names for nr in filename_to_numbers(name)]
    if not numbers: return '1001'
    return str(max(numbers) + 1)

def new_issue_filename(identifier, title):
    issue_dir = ensure_issue_directory()
    title_norm = "-".join(title).casefold()
    return os.path.join(issue_dir, f"{identifier}-{title_norm}.txt")

def create_issue(args):
    identifier = args.id or new_issue_number()
    issue_filename = new_issue_filename(identifier, args.title)
    title = " ".join(args.title)
    with open(issue_filename, "at") as f:
        f.write(f"id: {identifier}\ntitle: {title}\nstatus: created\n")
        f.write("description: \n")
    os.system("${EDITOR:-sensible-editor} +4 " + f"'{issue_filename}'")
    if args.commit:
        os.system(f"git add '{issue_filename}'")
        os.system(f"git commit -m '{identifier}: {title} (created)'")

def commit_to_issue(args):
    issue_filename = get_issue_filename(args.id)
    message = " ".join(args.message)
    with open(issue_filename, "at") as f:
        f.write(f"commit: {message}\n")
        if args.status: f.write(f"status: {args.status}\n")
    os.system(f"git add '{issue_filename}'")
    commit_message = f"{args.id}: {message}"
    if args.status: commit_message += f" ({args.status})"
    os.system(f"git commit -m '{commit_message}'")

def issue_lines_no_meta(issue_filename):
    last_field = None
    last_field_value = ""
    with open(issue_filename, "rt") as f:
        for line in f:
            field, value = line.rstrip().split(": ", 1)
            if field == "+":
                field = last_field
                value = f"{last_field_value}\n{value}"
            yield field, dict(field=field, value=value)
            last_field = field
            last_field_value = value

def field_match(value, search):
    if not search: return True
    if not isinstance(search, list): return field_match(value, [search])
    if "or" in search:
        return (field_match(value, search[:search.index("or")])
                or field_match(value, search[search.index("or")+1:]))
    if "and" in search:
        return (field_match(value, search[:search.index("and")])
                and field_match(value, search[search.index("and")+1:]))
    if search[0] == "not":
        return not field_match(value, search[1:])
    return any((term in value) for term in search)

def list_issues(args):
    issue_dir = ensure_issue_directory()
    issues = all_issues()
    for issue in sorted(issues):
        fields = dict(issue_lines_no_meta(os.path.join(issue_dir, issue)))
        if not field_match(fields["status"]["value"], args.status): continue
        if (not field_match(fields["title"]["value"], args.search) and
                not field_match(fields["description"]["value"], args.search)):
            continue
        print(fields["id"]["value"], ":",
                fields["title"]["value"],
                "(", fields["status"]["value"], ")")
        if not args.quiet:
            for field in fields:
                if field in ("id", "title", "status"): continue
                print(field, ":", fields[field]["value"])
            print()


cmd_parser = ArgumentParser(
        prog="bitgugs",
        description="Git-based issue tracker",
)
cmd_parser.add_argument("-c", "--commit",
        action="store_true",
        help="Commit issue changes immediately",
)
subcommands = cmd_parser.add_subparsers(dest="subcommand", required=True)

newissue_parser = subcommands.add_parser("new", help="Create new issue")
newissue_parser.set_defaults(func=create_issue)
newissue_parser.add_argument("title",
        type=str, nargs="+",
        help="A short (few words) description of the issue",
)
newissue_parser.add_argument("-i", "--id",
        type=str,
        help="Identifier for new issue (default: pick next number)",
)

listissues_parser = subcommands.add_parser("list", help="List issues")
listissues_parser.set_defaults(func=list_issues)
listissues_parser.add_argument("search",
        type=str, nargs="*",
        help="Words to look for in the issue (default: show all issues)",
)
listissues_parser.add_argument("-s", "--status",
        type=str, nargs="+", default=["not", "closed"],
        help="List only issues of given status (default: not closed)",
)
listissues_parser.add_argument("-q", "--quiet",
        action="store_true",
        help="Show only issue titles, not contents"
)

commit_parser = subcommands.add_parser("commit", help="Commit code to issue")
commit_parser.set_defaults(func=commit_to_issue)
commit_parser.add_argument("id",
        type=str,
        help="Identifier for the issue you are assigning the changes to",
)
commit_parser.add_argument("message",
        type=str, nargs="+",
        help="Description of your changes",
)
commit_parser.add_argument("-s", "--status",
        type=str,
        help="Also change issue status when commiting",
)

if __name__ == "__main__":
    args = cmd_parser.parse_args()
    if not args.subcommand: cmd_parser.print_help()
    elif args.commit:
        if os.system("git stash -m 'bitgugs stash for --commit'") != 0:
            die("git stash was unsuccessful but needed for --commit")
        try:
            args.func(args)
        finally:
            os.system("git stash pop")
    else: args.func(args)

