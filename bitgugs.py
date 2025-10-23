#!/usr/bin/env python3

import sys, os, glob
import functools, re, time
from argparse import ArgumentParser

def die(message):
    sys.stderr.write(message + "\n")
    sys.exit(1)

def run(command):
    print(">>>", command)
    return os.system(command)

def result(command):
    print("?>>", command)
    return os.popen(command).readline().rstrip()

def commit_with_message(message, filename=None):
    if filename: run(f"git add '{filename}'")
    run(f"git commit -m '{message}'")

def find_git_root():
    return result("git rev-parse --show-toplevel")

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
        f.write(f"id: {identifier}\ntitle: {title}\nstatus: {args.status}\n")
        f.write("description: \n")
    run("${EDITOR:-sensible-editor} +4 " + f"'{issue_filename}'")
    if args.commit:
        commit_with_message(f"{identifier}: {title} ({args.status})",
                filename=issue_filename)

def commit_to_issue(args):
    if args.commit:
        die("The --commit switch doesn't make sense for the commit command")
    message = " ".join(args.message)
    issue_ids = [args.id] + (args.issues or [])
    for issue_id in issue_ids:
        issue_filename = get_issue_filename(issue_id)
        with open(issue_filename, "at") as f:
            f.write(f"commit: {message}\n")
            if args.status: f.write(f"status: {args.status}\n")
        run(f"git add '{issue_filename}'")
    message_id = ", ".join(issue_ids)
    commit_message = f"{message_id}: {message}"
    if args.status: commit_message += f" ({args.status})"
    commit_with_message(commit_message)

def update_issue(args):
    issue_filename = get_issue_filename(args.id)
    value = " ".join(args.value)
    with open(issue_filename, "at") as f:
        f.write(f"{args.field}: {value}\n")
    if args.commit:
        commit_with_message(f"{args.id}: {args.field} -> {value}",
                filename=issue_filename)

@functools.cache
def get_git_user():
    return result("git config user.email")

def take_issue(args):
    issue_filename = get_issue_filename(args.id)
    user = get_git_user()
    with open(issue_filename, "at") as f:
        f.write(f"assignee: {user}\nstatus: {args.status}\n")
    if args.commit:
        commit_with_message(f"{args.id}: taken by {user}",
                filename=issue_filename)

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

def issue_lines_with_meta(issue_filename):
    author, instant = None, None
    with os.popen(f"git blame -p '{issue_filename}'") as f:
        for line in f:
            author_match = re.match(r"author-mail <([^>\r\t ]*)>", line)
            if author_match: author = author_match.group(1)
            time_match = re.match(r"author-time ([0-9]+)", line)
            if time_match: instant = int(time_match.group(1))
            if line.startswith("\t"):
                field, value = line.strip().split(": ", 1)
                yield field, dict(
                    field=field, value=value, author=author, instant=instant
                )

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

def show_issue(args):
    if args.meta:
        old_meta = None
        for f, line in issue_lines_with_meta(get_issue_filename(args.id)):
            new_meta = (line["instant"], line["author"])
            if old_meta != new_meta:
                line["time"] = time.strftime("%F %H:%m",
                        time.gmtime(line["instant"]))
                print("\n{author} ({time}):".format(**line))
                old_meta = new_meta
            print(" {field}: {value}".format(**line))
    else:
        print(open(get_issue_filename(args.id)).read())

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
        description="""Git-based issue tracker.
          See https://github.com/pkalliok/bitgugs for documentation.""",
)
cmd_parser.add_argument("-c", "--commit", action="store_true",
        help="Commit issue changes immediately",
)
subcommands = cmd_parser.add_subparsers(dest="subcommand", required=True)

newissue_parser = subcommands.add_parser("new", help="Create new issue")
newissue_parser.set_defaults(func=create_issue)
newissue_parser.add_argument("title", nargs="+",
        help="A short (few words) description of the issue",
)
newissue_parser.add_argument("-i", "--id",
        help="Identifier for new issue (default: pick next number)",
)
newissue_parser.add_argument("-s", "--status", default="created",
        help="Which state to create the issue in (default created)",
)

listissues_parser = subcommands.add_parser("list", help="List issues")
listissues_parser.set_defaults(func=list_issues)
listissues_parser.add_argument("search", nargs="*",
        help="Words to look for in the issue (default: show all issues)",
)
listissues_parser.add_argument("-s", "--status", nargs="+",
        default=["not", "closed"],
        help="List only issues of given status (default: not closed)",
)
listissues_parser.add_argument("-q", "--quiet", action="store_true",
        help="Show only issue titles, not contents"
)

commit_parser = subcommands.add_parser("commit", help="Commit code to issue")
commit_parser.set_defaults(func=commit_to_issue)
commit_parser.add_argument("id",
        help="Identifier for the issue you are assigning the changes to",
)
commit_parser.add_argument("message", nargs="+",
        help="Description of your changes",
)
commit_parser.add_argument("-s", "--status",
        help="Also change issue status when commiting",
)
commit_parser.add_argument("-i", "--issues", nargs="+",
        help="Identifier(s) for more issue(s) that the changes belong to",
)

update_parser = subcommands.add_parser("update", help="Update an issue")
update_parser.set_defaults(func=update_issue)
update_parser.add_argument("id",
        help="Identifier for the issue you are making the changes to",
)
update_parser.add_argument("field",
        help="Which field (title, status, description, links...) to update",
)
update_parser.add_argument("value", nargs="+",
        help="New value for the field",
)

show_parser = subcommands.add_parser("show", help="Show issue by id")
show_parser.set_defaults(func=show_issue)
show_parser.add_argument("id",
        help="Identifier for issue to show",
)
show_parser.add_argument("-m", "--meta", action="store_true",
        help="Also show who made the update and when",
)

take_parser = subcommands.add_parser("take", help="Start work on an issue")
take_parser.set_defaults(func=take_issue)
take_parser.add_argument("id",
        help="Identifier for issue to mark as being worked upon",
)
take_parser.add_argument("-s", "--status", default="assigned",
        help="Which state to transition the issue to (default assigned)",
)

get_parser = lambda: cmd_parser

if __name__ == "__main__":
    args = cmd_parser.parse_args()
    if not args.subcommand: cmd_parser.print_help()
    elif args.commit:
        stash_name = result("git stash create bitgugs temp stash")
        run("git reset --hard HEAD")
        try:
            args.func(args)
        finally:
            if run(f"git stash apply --index {stash_name}") != 0:
                print("stash apply failed, but your changes are saved in",
                        stash_name)
    else: args.func(args)

