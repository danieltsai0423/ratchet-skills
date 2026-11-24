#!/bin/sh
# ratchet-skills installer for macOS, Linux, WSL and Git Bash (POSIX sh).
# Windows PowerShell users: run install.ps1 instead.
set -eu

usage() {
  cat <<'EOF'
Usage: ./install.sh [options] [skill ...]

Copies skills from ./skills into the folder your agent discovers.
With no skill names, installs every skill.

Options:
  -a, --agent NAME     claude | codex | devin | all   (default: all)
  -s, --scope SCOPE    project | user                 (default: user)
  -p, --project DIR    target project root for --scope project (default: .)
  -f, --force          replace skills that already exist
  -l, --list           list available skills and exit
  -h, --help           show this help

Destinations:
  claude   project: <DIR>/.claude/skills   user: ~/.claude/skills
  codex    project: <DIR>/.agents/skills   user: ~/.agents/skills
  devin    project: <DIR>/.agents/skills   user: ~/.agents/skills
EOF
}

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
src="$script_dir/skills"
agent=all
scope=user
project=.
force=0
list=0
names=""

while [ $# -gt 0 ]; do
  case "$1" in
    -a|--agent)   [ $# -ge 2 ] || { echo "Missing value for $1" >&2; exit 2; }; agent=$2; shift 2 ;;
    -s|--scope)   [ $# -ge 2 ] || { echo "Missing value for $1" >&2; exit 2; }; scope=$2; shift 2 ;;
    -p|--project) [ $# -ge 2 ] || { echo "Missing value for $1" >&2; exit 2; }; project=$2; scope=project; shift 2 ;;
    -f|--force)   force=1; shift ;;
    -l|--list)    list=1; shift ;;
    -h|--help)    usage; exit 0 ;;
    -*)           echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
    *)            names="$names $1"; shift ;;
  esac
done

[ -d "$src" ] || { echo "Skills folder not found: $src" >&2; exit 1; }

if [ "$list" -eq 1 ]; then
  for d in "$src"/*/; do basename "$d"; done
  exit 0
fi

case "$scope" in
  user)    base=$HOME ;;
  project) [ -d "$project" ] || { echo "Project folder not found: $project" >&2; exit 1; }
           base=$(CDPATH= cd -- "$project" && pwd) ;;
  *)       echo "Invalid scope: $scope (use project or user)" >&2; exit 2 ;;
esac

case "$agent" in
  claude)       dests="$base/.claude/skills" ;;
  codex|devin)  dests="$base/.agents/skills" ;;
  all)          dests="$base/.claude/skills $base/.agents/skills" ;;
  *)            echo "Invalid agent: $agent (use claude, codex, devin or all)" >&2; exit 2 ;;
esac

if [ -z "$names" ]; then
  for d in "$src"/*/; do names="$names $(basename "$d")"; done
fi

for n in $names; do
  [ -f "$src/$n/SKILL.md" ] || { echo "Unknown skill: $n (try --list)" >&2; exit 1; }
done

status=0
for dest in $dests; do
  mkdir -p "$dest"
  for n in $names; do
    if [ -e "$dest/$n" ]; then
      if [ "$force" -eq 1 ]; then
        rm -rf "$dest/$n"
      else
        echo "skip     $dest/$n (exists; use --force to replace)"
        status=1
        continue
      fi
    fi
    cp -R "$src/$n" "$dest/$n"
    echo "install  $dest/$n"
  done
done

exit $status
